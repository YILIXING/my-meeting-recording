// Settings page logic

const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    loadCurrentConfig();
    setupEventListeners();
    checkServiceStatus();
});

async function loadCurrentConfig() {
    try {
        const response = await fetch(`${API_BASE}/config/llm`);
        if (!response.ok) return;

        const config = await response.json();
        document.getElementById('defaultService').value = config.default_service || 'doubao';

        // Load service status
        if (config.services && config.services.doubao) {
            const doubao = config.services.doubao;
            if (doubao.configured) {
                document.getElementById('doubaoStatus').textContent = '已配置';
                document.getElementById('doubaoStatus').className = 'api-status configured';
            } else {
                document.getElementById('doubaoStatus').textContent = '未配置';
                document.getElementById('doubaoStatus').className = 'api-status not-configured';
            }
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

function setupEventListeners() {
    // Default service form
    document.getElementById('defaultServiceForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const service = document.getElementById('defaultService').value;

        try {
            const response = await fetch(`${API_BASE}/config/llm`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ service })
            });

            if (response.ok) {
                alert('默认服务已保存');
            } else {
                throw new Error('Failed to save config');
            }
        } catch (error) {
            alert('保存失败: ' + error.message);
        }
    });

    // Doubao form
    document.getElementById('doubaoForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        try {
            const response = await fetch(`${API_BASE}/config/llm`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    service: 'doubao',
                    api_key: formData.get('api_key'),
                    app_id: formData.get('app_id'),
                    model: formData.get('model')
                })
            });

            if (response.ok) {
                alert('豆包配置已保存');
                checkServiceStatus();
            } else {
                throw new Error('Failed to save config');
            }
        } catch (error) {
            alert('保存失败: ' + error.message);
        }
    });
}

async function checkServiceStatus() {
    // Check if Doubao is configured
    const apiKey = document.getElementById('doubaoApiKey').value;
    const status = document.getElementById('doubaoStatus');

    if (apiKey && apiKey !== 'your_doubao_api_key_here') {
        status.textContent = '已配置';
        status.className = 'api-status configured';
    } else {
        status.textContent = '未配置';
        status.className = 'api-status not-configured';
    }
}

async function validateService(service) {
    const validationDiv = document.getElementById(`${service}Validation`);
    validationDiv.style.display = 'block';
    validationDiv.textContent = '验证中...';
    validationDiv.className = 'validation-result';

    try {
        const response = await fetch(`${API_BASE}/config/llm/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service })
        });

        if (response.ok) {
            validationDiv.textContent = '✓ 配置验证成功';
            validationDiv.className = 'validation-result success';
        } else {
            const error = await response.json();
            validationDiv.textContent = '✗ 验证失败: ' + (error.detail || '未知错误');
            validationDiv.className = 'validation-result error';
        }
    } catch (error) {
        validationDiv.textContent = '✗ 验证失败: ' + error.message;
        validationDiv.className = 'validation-result error';
    }
}
