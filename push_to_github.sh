#!/bin/bash
# Office Agent - GitHub 推送脚本
# 使用方法: ./push_to_github.sh <your_github_token>

TOKEN=$1
USERNAME="twj110110"
REPO_NAME="office-agent"

if [ -z "$TOKEN" ]; then
    echo "请提供GitHub Token"
    echo "使用方法: ./push_to_github.sh <your_github_token>"
    exit 1
fi

echo "配置Git..."
git config user.name "twj110110"
git config user.email "twj110110@github.com"

echo "添加远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://${TOKEN}@github.com/${USERNAME}/${REPO_NAME}.git"

echo "添加文件到Git..."
git add .

echo "提交更改..."
git commit -m "Initial commit: Office Agent - 智能办公自动化助手

- 智能文档生成（工作总结、公文、汇报材料等）
- 多轮逻辑校验系统
- 格式自动排版
- 任务智能拆解与执行
- ReAct Agent 核心实现
- FastAPI Web 服务
- 前端交互界面
- 完整测试覆盖"

echo "创建main分支..."
git branch -M main

echo "推送到GitHub..."
git push -u origin main -f

if [ $? -eq 0 ]; then
    echo "成功推送到GitHub!"
    echo "仓库地址: https://github.com/$USERNAME/$REPO_NAME"
else
    echo "推送失败，请检查GitHub Token和仓库设置"
fi
