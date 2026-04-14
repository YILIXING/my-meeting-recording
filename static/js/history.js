// History page logic

const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    loadMeetings();
    setupEventListeners();
});

async function loadMeetings() {
    try {
        const response = await fetch(`${API_BASE}/meetings`);
        if (!response.ok) throw new Error('Failed to load meetings');

        let meetings = await response.json();
        meetings = sortMeetings(meetings);
        displayMeetings(meetings);
    } catch (error) {
        console.error('Error loading meetings:', error);
        document.getElementById('meetingsGrid').innerHTML =
            '<div class="empty-state"><h3>加载失败</h3></div>';
    }
}

function sortMeetings(meetings) {
    return meetings.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
}

function displayMeetings(meetings) {
    const container = document.getElementById('meetingsGrid');

    if (meetings.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>暂无会议记录</h3>
                <p><a href="/static/index.html">上传第一个录音</a></p>
            </div>
        `;
        return;
    }

    container.innerHTML = meetings.map(meeting => `
        <div class="meeting-card" onclick="goToDetail('${meeting.id}')">
            <h3>${escapeHtml(meeting.title)}</h3>
            <p>📅 ${formatDate(meeting.created_at)}</p>
            <p>📁 ${escapeHtml(meeting.original_filename)}</p>
            <span class="status status-${meeting.status}">${getStatusText(meeting.status)}</span>
        </div>
    `).join('');
}

function setupEventListeners() {
    // Status filter
    document.getElementById('statusFilter').addEventListener('change', filterMeetings);

    // Search
    let searchTimeout;
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => filterMeetings(), 300);
    });
}

async function filterMeetings() {
    const status = document.getElementById('statusFilter').value;
    const search = document.getElementById('searchInput').value.toLowerCase();

    try {
        const response = await fetch(`${API_BASE}/meetings`);
        if (!response.ok) return;

        let meetings = await response.json();

        // Apply filters
        if (status) {
            meetings = meetings.filter(m => m.status === status);
        }

        if (search) {
            meetings = meetings.filter(m =>
                m.title.toLowerCase().includes(search) ||
                m.original_filename.toLowerCase().includes(search)
            );
        }

        displayMeetings(meetings);
    } catch (error) {
        console.error('Error filtering meetings:', error);
    }
}

function goToDetail(meetingId) {
    window.location.href = `/static/detail.html?id=${meetingId}`;
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
