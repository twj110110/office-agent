# Office Agent - 部署指南

## 方式一：本地运行

### 1. 环境要求

- Python 3.9+
- pip 包管理器

### 2. 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/twj110110/office-agent.git
cd office-agent

# 2. 创建虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. 安装依赖
pip install -e ".[dev]"
```

### 3. 运行服务

```bash
# 启动服务
python -m src.web.main

# 或使用 uvicorn
uvicorn src.web.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000 打开应用。

## 方式二：Docker 部署

### 1. 创建 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -e "."

EXPOSE 8000

CMD ["uvicorn", "src.web.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 构建并运行

```bash
# 构建镜像
docker build -t office-agent .

# 运行容器
docker run -d -p 8000:8000 --name office-agent office-agent
```

## 方式三：云服务器部署

### 使用 systemd (Linux)

创建服务文件 `/etc/systemd/system/office-agent.service`:

```ini
[Unit]
Description=Office Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/office-agent
Environment="PATH=/var/www/office-agent/venv/bin"
ExecStart=/var/www/office-agent/venv/bin/uvicorn src.web.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable office-agent
sudo systemctl start office-agent
sudo systemctl status office-agent
```

### 使用 Nginx 反向代理

配置 `/etc/nginx/sites-available/office-agent`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /static {
        alias /var/www/office-agent/static;
        expires 30d;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/office-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 配置说明

### 环境变量

创建 `.env` 文件：

```env
# 基础配置
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# LLM 配置（可选）
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7

# 文档配置
DOC_OUTPUT_DIR=output
VALIDATION_MAX_ROUNDS=3
TASK_MAX_DEPTH=5
```

## 使用说明

### Web 界面

1. 打开浏览器访问服务地址
2. 在左侧菜单选择功能
3. 填写表单并提交
4. 查看生成结果

### API 调用

```bash
# 生成文档
curl -X POST http://localhost:8000/api/v1/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "doc_type": "work_summary",
    "title": "2024年度工作总结",
    "content_requirements": "总结全年工作...",
    "keywords": ["数字化", "创新"],
    "enable_validation": true
  }'

# 智能对话
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "帮我写一份工作总结"
  }'
```

## 故障排除

### 端口被占用

```bash
# 查找占用端口的进程
netstat -tlnp | grep 8000

# 或修改端口
uvicorn src.web.main:app --port 8080
```

### 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip setuptools wheel

# 重新安装
pip install -e "." --force-reinstall
```

### 权限问题

```bash
# 修改文件权限
chmod -R 755 /var/www/office-agent
chown -R www-data:www-data /var/www/office-agent
```

## 更新升级

```bash
# 拉取最新代码
git pull origin main

# 重新安装依赖
pip install -e "." --force-reinstall

# 重启服务
sudo systemctl restart office-agent
```
