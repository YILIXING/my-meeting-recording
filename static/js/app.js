// My Meeting Recording - Enhanced JavaScript with real-time progress

const API_BASE = '/api';
let progressCheckInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initUploadForm();
    loadRecentMeetings();
    checkSystemStatus();
});

function initUploadForm() {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('audioFile');
    const uploadBtn = document.getElementById('uploadBtn');

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            const sizeMB = file.size / 1024 / 1024;
            if (sizeMB > 300) {
                alert('文件大小超过300MB限制');
                fileInput.value = '';
            } else {
                // Show file info
                updateProgressText(`已选择: ${file.name} (${sizeMB.toFixed(2)}MB)`);
            }
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const title = document.getElementById('title').value;

        if (title) {
            formData.append('title', title);
        }

        uploadBtn.disabled = true;
        uploadBtn.textContent = '上传中...';

        try {
            // Show progress section
            document.getElementById('uploadProgress').classList.remove('hidden');
            updateProgressText('正在上传音频文件...');
            updateProgress(0);

            const response = await fetch(`${API_BASE}/meetings`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('上传失败');
            }

            const meeting = await response.json();
            updateProgressText('上传成功，开始转写...');

            // Start polling for progress
            startProgressPolling(meeting.id);

        } catch (error) {
            updateProgressText('上传失败: ' + error.message);
            uploadBtn.disabled = false;
            uploadBtn.textContent = '上传并开始转写';
        }
    });
}

function startProgressPolling(meetingId) {
    let pollCount = 0;
    const maxPolls = 120; // Poll for up to 2 minutes

    progressCheckInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/meetings/${meetingId}`);
            if (!response.ok) return;

            const meeting = await response.json();

            // Calculate progress based on status
            let progress = 0;
            let statusText = '';

            switch (meeting.status) {
                case 'uploading':
                    progress = 20;
                    statusText = '上传中...';
                    break;
                case 'transcribing':
                    progress = 20 + (meeting.progress || 0) * 0.6; // 20-80%
                    statusText = `转写中... ${meeting.progress || 0}%`;
                    break;
                case 'generating':
                    progress = 85;
                    statusText = '生成纪要中...';
                    break;
                case 'completed':
                    progress = 100;
                    statusText = '完成！';
                    clearInterval(progressCheckInterval);

                    // Redirect to detail page after a short delay
                    setTimeout(() => {
                        window.location.href = `/static/detail.html?id=${meetingId}`;
                    }, 1000);
                    break;
                case 'failed':
                    progress = 0;
                    statusText = '失败: ' + (meeting.error_message || '未知错误');
                    clearInterval(progressCheckInterval);

                    document.getElementById('uploadBtn').disabled = false;
                    document.getElementById('uploadBtn').textContent = '上传并开始转写';
                    break;
                case 'cancelled':
                    progress = 0;
                    statusText = '已取消';
                    clearInterval(progressCheckInterval);
                    break;
            }

            updateProgress(progress);
            updateProgressText(statusText);

            pollCount++;
            if (pollCount >= maxPolls) {
                clearInterval(progressCheckInterval);
                updateProgressText('处理超时，请手动检查');
            }

        } catch (error) {
            console.error('Progress check error:', error);
        }
    }, 1000); // Poll every second
}

function updateProgress(percent) {
    const fill = document.getElementById('progressFill');
    if (fill) {
        fill.style.width = `${percent}%`;
    }
}

function updateProgressText(text) {
    const textEl = document.getElementById('progressText');
    if (textEl) {
        textEl.textContent = text;
    }
}

async function loadRecentMeetings() {
    const container = document.getElementById('meetingsList');

    try {
        const response = await fetch(`${API_BASE}/meetings`);
        const meetings = await response.json();

        if (meetings.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:#888;padding:40px;">暂无会议记录</p>';
            return;
        }

        container.innerHTML = meetings.slice(0, 5).map(meeting => `
            <div class="meeting-card status-${meeting.status}">
                <h3>${escapeHtml(meeting.title)}</h3>
                <p>
                    📅 ${formatDate(meeting.created_at)} |
                    ${getStatusWithIcon(meeting.status)}
                </p>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p style="text-align:center;color:#f44336;">加载失败</p>';
    }
}

async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/config/storage`);
        if (response.ok) {
            const info = await response.json();

            // Show storage warning if needed
            if (info.total_size_mb > 500) {
                const warning = document.createElement('div');
                warning.style.cssText = 'background:#fff3cd;padding:15px;margin:20px 0;border-radius:8px;border-left:4px solid #ffc107;text-align:center;';
                warning.innerHTML = `
                    <strong>⚠️ 存储空间提醒</strong>
                    <p style="margin-top:8px;color:#856404;">音频文件占用 ${info.total_size_mb}MB，建议清理旧文件释放空间</p>
                    <button onclick="cleanupAudio()" style="margin-top:10px;padding:8px 16px;background:#dc3545;color:white;border:none;border-radius:6px;cursor:pointer;">立即清理</button>
                `;
                document.querySelector('.container').appendChild(warning);
            }
        }
    } catch (error) {
        console.log('Could not check storage status');
    }
}

async function cleanupAudio() {
    if (!confirm('确定要清理7天前的音频文件吗？')) return;

    try {
        const response = await fetch(`${API_BASE}/config/cleanup`, {
            method: 'POST'
        });

        if (response.ok) {
            const result = await response.json();
            alert(`清理完成！删除了 ${result.cleaned_count} 个音频文件`);
            location.reload();
        } else {
            throw new Error('Cleanup failed');
        }
    } catch (error) {
        alert('清理失败: ' + error.message);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
        return '今天 ' + date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'});
    } else if (diffDays === 1) {
        return '昨天 ' + date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'});
    } else if (diffDays < 7) {
        return diffDays + '天前';
    } else {
        return date.toLocaleDateString('zh-CN');
    }
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

function getStatusWithIcon(status) {
    const text = getStatusText(status);
    const icons = {
        'uploading': '⬆️',
        'transcribing': '🎙️',
        'generating': '📝',
        'completed': '✅',
        'failed': '❌',
        'cancelled': '⏹️'
    };
    return `${icons[status] || ''} ${text}`;
}
