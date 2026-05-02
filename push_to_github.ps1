# Office Agent - GitHub 推送脚本
# 使用方法: .\push_to_github.ps1 -Token "your_github_token"

param(
    [Parameter(Mandatory=$true)]
    [string]$Token,
    
    [string]$RepoName = "office-agent",
    [string]$UserName = "twj110110",
    [string]$Email = "twj110110@github.com"
)

# 配置Git
Write-Host "配置Git..." -ForegroundColor Green
git config user.name $UserName
git config user.email $Email

# 添加远程仓库
Write-Host "添加远程仓库..." -ForegroundColor Green
$remoteUrl = "https://${Token}@github.com/${UserName}/${RepoName}.git"
git remote remove origin 2>$null
git remote add origin $remoteUrl

# 添加所有文件
Write-Host "添加文件到Git..." -ForegroundColor Green
git add .

# 提交
Write-Host "提交更改..." -ForegroundColor Green
git commit -m "Initial commit: Office Agent - 智能办公自动化助手

- 智能文档生成（工作总结、公文、汇报材料等）
- 多轮逻辑校验系统
- 格式自动排版
- 任务智能拆解与执行
- ReAct Agent 核心实现
- FastAPI Web 服务
- 前端交互界面
- 完整测试覆盖"

# 创建并切换到main分支
git branch -M main

# 推送到GitHub
Write-Host "推送到GitHub..." -ForegroundColor Green
git push -u origin main -f

if ($LASTEXITCODE -eq 0) {
    Write-Host "成功推送到GitHub!" -ForegroundColor Green
    Write-Host "仓库地址: https://github.com/$UserName/$RepoName" -ForegroundColor Cyan
} else {
    Write-Host "推送失败，请检查GitHub Token和仓库设置" -ForegroundColor Red
}
