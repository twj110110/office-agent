/**
 * Office Agent - 前端应用
 */

// API基础URL
const API_BASE = '/api/v1';

// 当前会话ID
let currentSessionId = null;

// 当前文档内容
let currentDocument = null;

/**
 * 初始化应用
 */
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadDocumentTypes();
    setupEventListeners();
});

/**
 * 初始化导航
 */
function initNavigation() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            const tabId = tab.dataset.tab;
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = 'none';
            });
            document.getElementById(tabId).style.display = 'block';
        });
    });
}

/**
 * 设置事件监听
 */
function setupEventListeners() {
    // 文档生成表单
    const docForm = document.getElementById('docForm');
    if (docForm) {
        docForm.addEventListener('submit', handleDocumentSubmit);
    }
    
    // Agent对话
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }
    
    // 任务创建
    const taskForm = document.getElementById('taskForm');
    if (taskForm) {
        taskForm.addEventListener('submit', handleTaskSubmit);
    }
}

/**
 * 加载文档类型
 */
async function loadDocumentTypes() {
    try {
        const response = await fetch(`${API_BASE}/document-types`);
        const data = await response.json();
        
        const select = document.getElementById('docType');
        if (select) {
            data.types.forEach(type => {
                const option = document.createElement('option');
                option.value = type.value;
                option.textContent = type.label;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载文档类型失败:', error);
    }
}

/**
 * 处理文档生成提交
 */
async function handleDocumentSubmit(e) {
    e.preventDefault();
    
    const formData = {
        doc_type: document.getElementById('docType').value,
        title: document.getElementById('docTitle').value,
        content_requirements: document.getElementById('docRequirements').value,
        keywords: document.getElementById('docKeywords').value.split(',').map(k => k.trim()).filter(k => k),
        tone: document.getElementById('docTone').value,
        max_length: parseInt(document.getElementById('docLength').value),
        enable_validation: document.getElementById('enableValidation').checked,
        validation_rounds: parseInt(document.getElementById('validationRounds').value)
    };
    
    showLoading('正在生成文档...');
    
    try {
        const response = await fetch(`${API_BASE}/documents/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentDocument = data;
            displayDocument(data);
            showAlert('文档生成成功！', 'success');
        } else {
            showAlert(data.detail || '生成失败', 'error');
        }
    } catch (error) {
        showAlert('网络错误: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * 显示生成的文档
 */
function displayDocument(doc) {
    const preview = document.getElementById('docPreview');
    const editor = document.getElementById('docEditor');
    
    if (preview) {
        preview.innerHTML = `
            <div class="document-header">
                <h2>${doc.title}</h2>
                <div class="document-meta">
                    <span class="badge badge-info">${getDocTypeLabel(doc.doc_type)}</span>
                    <span>创建于: ${new Date(doc.created_at).toLocaleString()}</span>
                </div>
            </div>
            <div class="document-content">
                ${formatDocumentContent(doc.formatted_content)}
            </div>
            ${renderValidationResults(doc.validation_results)}
        `;
    }
    
    if (editor) {
        editor.value = doc.content;
    }
    
    // 显示操作按钮
    const actions = document.getElementById('docActions');
    if (actions) {
        actions.style.display = 'flex';
    }
}

/**
 * 格式化文档内容
 */
function formatDocumentContent(content) {
    // 简单Markdown渲染
    return content
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

/**
 * 渲染校验结果
 */
function renderValidationResults(results) {
    if (!results || results.length === 0) return '';
    
    const lastResult = results[results.length - 1];
    
    let html = '<div class="validation-section"><h3>校验结果</h3>';
    
    html += `<div class="validation-score">
        <span>综合评分: ${(lastResult.score * 100).toFixed(1)}%</span>
        <span class="badge ${lastResult.passed ? 'badge-success' : 'badge-warning'}">
            ${lastResult.passed ? '通过' : '需改进'}
        </span>
    </div>`;
    
    if (lastResult.issues.length > 0) {
        html += '<div class="issues"><h4>发现问题:</h4><ul>';
        lastResult.issues.forEach(issue => {
            html += `<li>${issue}</li>`;
        });
        html += '</ul></div>';
    }
    
    if (lastResult.suggestions.length > 0) {
        html += '<div class="suggestions"><h4>改进建议:</h4><ul>';
        lastResult.suggestions.forEach(suggestion => {
            html += `<li>${suggestion}</li>`;
        });
        html += '</ul></div>';
    }
    
    html += '</div>';
    return html;
}

/**
 * 处理Agent对话
 */
async function handleChatSubmit(e) {
    e.preventDefault();
    
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 添加用户消息
    addChatMessage('user', message);
    input.value = '';
    
    // 显示思考中
    const thinkingId = addChatMessage('assistant', '<div class="thinking">思考中...</div>');
    
    try {
        const response = await fetch(`${API_BASE}/agent/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentSessionId = data.session_id;
            updateChatMessage(thinkingId, data.response);
            
            // 显示使用的工具
            if (data.tools_used && data.tools_used.length > 0) {
                addChatMessage('system', `使用了工具: ${data.tools_used.join(', ')}`);
            }
        } else {
            updateChatMessage(thinkingId, '抱歉，处理失败: ' + (data.detail || '未知错误'));
        }
    } catch (error) {
        updateChatMessage(thinkingId, '网络错误: ' + error.message);
    }
}

/**
 * 添加聊天消息
 */
function addChatMessage(role, content) {
    const container = document.getElementById('chatMessages');
    if (!container) return null;
    
    const id = 'msg_' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = `chat-message ${role}`;
    div.innerHTML = `<div class="message-content">${content}</div>`;
    
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    
    return id;
}

/**
 * 更新聊天消息
 */
function updateChatMessage(id, content) {
    const msg = document.getElementById(id);
    if (msg) {
        msg.querySelector('.message-content').innerHTML = content;
    }
}

/**
 * 处理任务提交
 */
async function handleTaskSubmit(e) {
    e.preventDefault();
    
    const description = document.getElementById('taskDescription').value.trim();
    if (!description) return;
    
    showLoading('正在创建任务...');
    
    try {
        const response = await fetch(`${API_BASE}/tasks/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                task_description: description,
                auto_execute: true
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayTask(data);
            showAlert('任务创建成功！', 'success');
        } else {
            showAlert(data.detail || '创建失败', 'error');
        }
    } catch (error) {
        showAlert('网络错误: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * 显示任务信息
 */
function displayTask(task) {
    const container = document.getElementById('taskDisplay');
    if (!container) return;
    
    let html = `
        <div class="task-header">
            <h3>任务: ${task.description.substring(0, 50)}...</h3>
            <span class="badge badge-${getStatusClass(task.status)}">${task.status}</span>
        </div>
        <div class="task-subtasks">
    `;
    
    task.subtasks.forEach(subtask => {
        html += `
            <div class="task-item">
                <span class="task-status ${subtask.status}"></span>
                <div class="task-info">
                    <div class="task-name">${subtask.name}</div>
                    <div class="task-desc">${subtask.description}</div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    if (task.summary) {
        html += `<div class="task-summary"><h4>汇总结果</h4><pre>${task.summary}</pre></div>`;
    }
    
    container.innerHTML = html;
}

/**
 * 获取文档类型标签
 */
function getDocTypeLabel(type) {
    const labels = {
        'work_summary': '工作总结',
        'official_document': '公文',
        'report': '汇报材料',
        'policy': '政策文件',
        'notice': '通知',
        'announcement': '公告',
        'plan': '工作计划'
    };
    return labels[type] || type;
}

/**
 * 获取状态样式类
 */
function getStatusClass(status) {
    const classes = {
        'completed': 'success',
        'running': 'info',
        'pending': 'warning',
        'failed': 'error'
    };
    return classes[status] || 'info';
}

/**
 * 显示提示
 */
function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    if (!container) {
        alert(message);
        return;
    }
    
    const div = document.createElement('div');
    div.className = `alert alert-${type}`;
    div.textContent = message;
    
    container.appendChild(div);
    
    setTimeout(() => {
        div.remove();
    }, 5000);
}

/**
 * 显示加载中
 */
function showLoading(message = '加载中...') {
    let loader = document.getElementById('globalLoading');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'globalLoading';
        loader.className = 'loading-overlay';
        document.body.appendChild(loader);
    }
    
    loader.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <span>${message}</span>
        </div>
    `;
    loader.style.display = 'flex';
}

/**
 * 隐藏加载中
 */
function hideLoading() {
    const loader = document.getElementById('globalLoading');
    if (loader) {
        loader.style.display = 'none';
    }
}

/**
 * 导出文档
 */
async function exportDocument(format) {
    if (!currentDocument) {
        showAlert('请先生成文档', 'warning');
        return;
    }
    
    try {
        const response = await fetch(
            `${API_BASE}/documents/${currentDocument.id}/export/${format}`
        );
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentDocument.title}.${format}`;
            a.click();
            window.URL.revokeObjectURL(url);
            showAlert('导出成功！', 'success');
        } else {
            showAlert('导出失败', 'error');
        }
    } catch (error) {
        showAlert('导出错误: ' + error.message, 'error');
    }
}

/**
 * 格式化文档
 */
async function formatCurrentDocument() {
    const editor = document.getElementById('docEditor');
    if (!editor || !editor.value.trim()) {
        showAlert('请先输入内容', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/utils/format`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: editor.value,
                format_type: 'official'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            editor.value = data.formatted_text;
            showAlert('格式化成功！', 'success');
        } else {
            showAlert('格式化失败', 'error');
        }
    } catch (error) {
        showAlert('格式化错误: ' + error.message, 'error');
    }
}

/**
 * 校验文档
 */
async function validateCurrentDocument() {
    const editor = document.getElementById('docEditor');
    if (!editor || !editor.value.trim()) {
        showAlert('请先输入内容', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/utils/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: editor.value })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayValidationResults(data);
        } else {
            showAlert('校验失败', 'error');
        }
    } catch (error) {
        showAlert('校验错误: ' + error.message, 'error');
    }
}

/**
 * 显示校验结果
 */
function displayValidationResults(results) {
    const container = document.getElementById('validationResults');
    if (!container) return;
    
    container.innerHTML = renderValidationResults([results]);
    container.style.display = 'block';
}
