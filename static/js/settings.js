// Settings page logic

const API_BASE = '/api';

// Preset service configurations
const PRESET_SERVICES = {
    doubao: {
        name: '豆包（火山引擎）',
        protocol: 'openai',
        endpoint: 'https://ark.cn-beijing.volces.com/api/v3',
        model: 'doubao-pro-4k',
        extraFields: ['app_id']
    },
    qianwen: {
        name: '千问（阿里云）',
        protocol: 'openai',
        endpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        model: 'qwen-max',
        extraFields: []
    },
    claude: {
        name: 'Claude（Anthropic）',
        protocol: 'anthropic',
        endpoint: 'https://api.anthropic.com',
        model: 'claude-3-5-sonnet-20241022',
        extraFields: []
    },
    openai: {
        name: 'OpenAI（GPT）',
        protocol: 'openai',
        endpoint: 'https://api.openai.com/v1',
        model: 'gpt-4o-audio-preview',
        extraFields: []
    },
    zhipuai: {
        name: '智谱GLM',
        protocol: 'openai',
        endpoint: 'https://open.bigmodel.cn/api/paas/v4',
        model: 'glm-4',
        extraFields: []
    }
};

document.addEventListener('DOMContentLoaded', () => {
    loadCurrentConfig();
    setupEventListeners();
    renderServiceForms();
    checkServiceStatus();
});

async function loadCurrentConfig() {
    try {
        const response = await fetch(`${API_BASE}/config/llm`);
        if (!response.ok) return;

        const config = await response.json();
        document.getElementById('defaultService').value = config.default_service || 'doubao';

        // Load service configurations into forms
        if (config.services) {
            for (const [serviceId, serviceInfo] of Object.entries(config.services)) {
                if (serviceInfo.configured && serviceId !== 'default_service') {
                    loadServiceConfig(serviceId);
                }
            }
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

async function loadServiceConfig(serviceId) {
    try {
        const response = await fetch(`${API_BASE}/config/llm`);
        if (!response.ok) return;

        const config = await response.json();

        // Get full config from file to load actual values
        const fullResponse = await fetch(`${API_BASE}/config/llm/full`);
        if (fullResponse.ok) {
            const fullConfig = await fullResponse.json();
            if (fullConfig.services && fullConfig.services[serviceId]) {
                const serviceConfig = fullConfig.services[serviceId];
                document.getElementById(`${serviceId}ApiKey`).value = serviceConfig.api_key || '';
                document.getElementById(`${serviceId}Endpoint`).value = serviceConfig.endpoint || '';
                document.getElementById(`${serviceId}Model`).value = serviceConfig.model || '';

                // Load extra fields
                if (serviceConfig.extra) {
                    for (const [key, value] of Object.entries(serviceConfig.extra)) {
                        const extraField = document.getElementById(`${serviceId}_${key}`);
                        if (extraField) {
                            extraField.value = value || '';
                        }
                    }
                }

                updateServiceStatus(serviceId, true);
            }
        }
    } catch (error) {
        console.error(`Error loading ${serviceId} config:`, error);
    }
}

function renderServiceForms() {
    const container = document.getElementById('servicesContainer');
    if (!container) return;

    container.innerHTML = '';

    for (const [serviceId, preset] of Object.entries(PRESET_SERVICES)) {
        const section = document.createElement('section');
        section.className = 'config-section';
        section.innerHTML = `
            <h3>
                <span>${preset.name}</span>
                <span id="${serviceId}Status" class="api-status">检查中...</span>
            </h3>
            <form id="${serviceId}Form">
                <input type="hidden" name="protocol" value="${preset.protocol}">
                <div class="form-group">
                    <label>API协议</label>
                    <input type="text" value="${preset.protocol.toUpperCase()}" disabled>
                    <small>标准协议，支持主流AI服务</small>
                </div>
                <div class="form-group">
                    <label for="${serviceId}Endpoint">API地址</label>
                    <input type="text" id="${serviceId}Endpoint" name="endpoint" value="${preset.endpoint}" placeholder="输入API地址">
                    <small>完整的API端点URL</small>
                </div>
                <div class="form-group">
                    <label for="${serviceId}ApiKey">API Key</label>
                    <input type="password" id="${serviceId}ApiKey" name="api_key" placeholder="输入API Key">
                    <small>用于身份验证的密钥</small>
                </div>
                <div class="form-group">
                    <label for="${serviceId}Model">Model ID</label>
                    <input type="text" id="${serviceId}Model" name="model" value="${preset.model}" placeholder="输入模型ID">
                    <small>要使用的模型标识符</small>
                </div>
                ${renderExtraFields(serviceId, preset.extraFields)}
                <div class="btn-group">
                    <button type="submit">保存配置</button>
                    <button type="button" class="btn-validate" onclick="validateService('${serviceId}')">验证连通性</button>
                </div>
                <div id="${serviceId}Validation" class="validation-result"></div>
            </form>
        `;
        container.appendChild(section);

        // Add form submit listener
        document.getElementById(`${serviceId}Form`).addEventListener('submit', async (e) => {
            e.preventDefault();
            await saveServiceConfig(serviceId);
        });
    }
}

function renderExtraFields(serviceId, extraFields) {
    if (!extraFields || extraFields.length === 0) {
        return '';
    }

    return extraFields.map(field => `
        <div class="form-group">
            <label for="${serviceId}_${field}">${field.replace('_', ' ').toUpperCase()}</label>
            <input type="text" id="${serviceId}_${field}" name="${field}" placeholder="输入${field}">
        </div>
    `).join('');
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
}

async function saveServiceConfig(serviceId) {
    const form = document.getElementById(`${serviceId}Form`);
    const formData = new FormData(form);
    const preset = PRESET_SERVICES[serviceId];

    // Build config object
    const config = {
        service: serviceId,
        protocol: formData.get('protocol'),
        api_key: formData.get('api_key'),
        endpoint: formData.get('endpoint'),
        model: formData.get('model'),
        extra: {}
    };

    // Add extra fields
    for (const field of preset.extraFields) {
        const value = formData.get(field);
        if (value) {
            config.extra[field] = value;
        }
    }

    try {
        const response = await fetch(`${API_BASE}/config/llm`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            alert(`${preset.name}配置已保存`);
            updateServiceStatus(serviceId, true);
        } else {
            throw new Error('Failed to save config');
        }
    } catch (error) {
        alert('保存失败: ' + error.message);
    }
}

function updateServiceStatus(serviceId, configured) {
    const status = document.getElementById(`${serviceId}Status`);
    if (configured) {
        status.textContent = '已配置';
        status.className = 'api-status configured';
    } else {
        status.textContent = '未配置';
        status.className = 'api-status not-configured';
    }
}

async function checkServiceStatus() {
    try {
        const response = await fetch(`${API_BASE}/config/llm`);
        if (!response.ok) return;

        const config = await response.json();

        if (config.services) {
            for (const serviceId of Object.keys(PRESET_SERVICES)) {
                if (config.services[serviceId] && config.services[serviceId].configured) {
                    updateServiceStatus(serviceId, true);
                } else {
                    updateServiceStatus(serviceId, false);
                }
            }
        }
    } catch (error) {
        console.error('Error checking service status:', error);
    }
}

async function validateService(serviceId) {
    const validationDiv = document.getElementById(`${serviceId}Validation`);
    validationDiv.style.display = 'block';
    validationDiv.textContent = '验证中...';
    validationDiv.className = 'validation-result';

    try {
        const response = await fetch(`${API_BASE}/config/llm/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service: serviceId })
        });

        if (response.ok) {
            validationDiv.textContent = '✓ 连通性验证成功';
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

