// Meeting detail page logic

const API_BASE = '/api';
let currentMeetingId = null;

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    currentMeetingId = urlParams.get('id');

    if (!currentMeetingId) {
        alert('缺少会议ID');
        window.location.href = '/static/index.html';
        return;
    }

    loadMeetingDetail();
    loadSpeakers();
    loadTranscription();
    loadSummaries();
    loadTemplates();
    setupEventListeners();
});

async function loadMeetingDetail() {
    try {
        const response = await fetch(`${API_BASE}/meetings/${currentMeetingId}`);
        if (!response.ok) throw new Error('Failed to load meeting');

        const meeting = await response.json();

        document.getElementById('meetingTitle').textContent = meeting.title;
        document.getElementById('meetingDate').textContent = formatDate(meeting.created_at);
        document.getElementById('meetingStatus').textContent = getStatusText(meeting.status);

        // Update audio section
        updateAudioSection(meeting);
    } catch (error) {
        console.error('Error loading meeting:', error);
        alert('加载会议详情失败');
    }
}

function updateAudioSection(meeting) {
    const audioStatus = document.getElementById('audioStatus');
    const deleteBtn = document.getElementById('deleteAudioBtn');

    if (meeting.is_audio_available) {
        audioStatus.textContent = '音频文件：已保存';
        deleteBtn.style.display = 'inline-block';
    } else {
        audioStatus.textContent = '音频文件：已删除';
        deleteBtn.style.display = 'none';
    }
}

async function loadSpeakers() {
    try {
        const response = await fetch(`${API_BASE}/meetings/${currentMeetingId}/transcription`);
        if (!response.ok) return;

        const segments = await response.json();
        const speakers = new Set();

        segments.forEach(seg => {
            speakers.add(seg.speaker_id);
        });

        const speakerList = document.getElementById('speakerList');
        speakerList.innerHTML = Array.from(speakers).map(speakerId => `
            <span class="speaker-mapping">
                ${speakerId}
                <button class="speaker-edit" onclick="renameSpeaker('${speakerId}')">重命名</button>
            </span>
        `).join('');

        if (speakers.size === 0) {
            speakerList.innerHTML = '<p>暂无说话人数据</p>';
        }
    } catch (error) {
        console.error('Error loading speakers:', error);
    }
}

async function renameSpeaker(speakerId) {
    const customName = prompt(`请输入 "${speakerId}" 的新名称：`);

    if (customName === null || customName.trim() === '') return;

    try {
        // Get current mappings
        const response = await fetch(`${API_BASE}/meetings/${currentMeetingId}/transcription`);
        const segments = await response.json();

        const speakers = new Set();
        segments.forEach(seg => speakers.add(seg.speaker_id));

        const mappings = Array.from(speakers).map(id => ({
            speaker_id: id,
            custom_name: id === speakerId ? customName : null
        }));

        // Update mappings
        await fetch(`${API_BASE}/meetings/${currentMeetingId}/speakers`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mappings })
        });

        // Reload
        loadSpeakers();
        loadTranscription();
    } catch (error) {
        console.error('Error renaming speaker:', error);
        alert('重命名失败');
    }
}

async function loadTranscription() {
    try {
        const response = await fetch(`${API_BASE}/meetings/${currentMeetingId}/transcription`);
        if (!response.ok) return;

        const segments = await response.json();
        const container = document.getElementById('transcriptList');

        if (segments.length === 0) {
            container.innerHTML = '<p>暂无转写结果</p>';
            return;
        }

        container.innerHTML = segments.map(seg => `
            <div class="transcript-item">
                <div class="transcript-speaker">${escapeHtml(seg.display_name)}</div>
                <div class="transcript-time">${seg.timestamp}</div>
                <div class="transcript-text">${escapeHtml(seg.text)}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading transcription:', error);
    }
}

async function loadSummaries() {
    try {
        const response = await fetch(`${API_BASE}/meetings/${currentMeetingId}/summaries`);
        if (!response.ok) return;

        const summaries = await response.json();
        const container = document.getElementById('summariesList');

        if (summaries.length === 0) {
            container.innerHTML = '<p>暂无纪要</p>';
            return;
        }

        container.innerHTML = summaries.map(summary => `
            <div class="summary-card">
                <div class="summary-version">版本 ${summary.version} · ${formatDate(summary.created_at)}</div>
                <div class="summary-content">${escapeHtml(summary.content)}</div>
                <div class="btn-group">
                    <button onclick="exportSummary('${summary.id}', 'markdown')">导出Markdown</button>
                    <button onclick="exportSummary('${summary.id}', 'txt')">导出TXT</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading summaries:', error);
    }
}

async function loadTemplates() {
    try {
        const response = await fetch(`${API_BASE}/templates`);
        if (!response.ok) return;

        const templates = await response.json();
        const select = document.getElementById('promptTemplate');

        select.innerHTML = '<option value="">自定义提示词</option>' +
            templates.map(t => `<option value="${t.id}">${escapeHtml(t.name)}</option>`).join('');

        select.addEventListener('change', () => {
            const selected = templates.find(t => t.id === select.value);
            if (selected) {
                document.getElementById('promptInput').value = selected.content;
            }
        });
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

function setupEventListeners() {
    // Summary form
    document.getElementById('summaryForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const prompt = formData.get('prompt');

        if (!prompt || prompt.trim() === '') {
            alert('请输入提示词');
            return;
        }

        const btn = document.getElementById('generateBtn');
        btn.disabled = true;
        btn.textContent = '生成中...';

        try {
            const response = await fetch(`${API_BASE}/meetings/${currentMeetingId}/summaries`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: prompt,
                    save_as_template: formData.get('save_as_template') === 'on',
                    template_name: formData.get('template_name') || undefined
                })
            });

            if (!response.ok) throw new Error('Failed to generate summary');

            // Reload summaries and meeting detail
            await loadSummaries();
            await loadMeetingDetail();

            // Clear form
            e.target.reset();
            alert('纪要生成成功！');
        } catch (error) {
            console.error('Error generating summary:', error);
            alert('生成纪要失败: ' + error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = '生成纪要';
        }
    });

    // Save as template checkbox
    document.getElementById('saveAsTemplate').addEventListener('change', (e) => {
        const nameInput = document.getElementById('templateName');
        nameInput.style.display = e.target.checked ? 'block' : 'none';
    });

    // Delete audio button
    document.getElementById('deleteAudioBtn').addEventListener('click', async () => {
        if (!confirm('确定要删除音频文件吗？此操作不可撤销。')) return;

        try {
            const response = await fetch(`${API_BASE}/meetings/${currentMeetingId}/audio`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Failed to delete audio');

            alert('音频文件已删除');
            loadMeetingDetail();
        } catch (error) {
            console.error('Error deleting audio:', error);
            alert('删除音频失败: ' + error.message);
        }
    });
}

async function exportSummary(summaryId, format) {
    try {
        const response = await fetch(`${API_BASE}/summaries/${summaryId}/export?format=${format}`);

        if (!response.ok) throw new Error('Failed to export');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `summary_${summaryId}.${format === 'markdown' ? 'md' : 'txt'}`;
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting summary:', error);
        alert('导出失败: ' + error.message);
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

function getStatusText(status) {
    const statusMap = {
        'uploading': '上传中',
        'transcribing': '转写中',
        'generating': '生成纪要中',
        'completed': '已完成',
        'failed': '失败',
        'cancelled': '已取消'
    };
    return statusMap[status] || status;
}
