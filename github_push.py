"""
GitHub 代码推送脚本
使用 GitHub API 创建仓库并推送代码
"""

import os
import sys
import base64
import json
import requests
from pathlib import Path


class GitHubPusher:
    """GitHub 推送器"""
    
    def __init__(self, token: str, username: str = "twj110110"):
        self.token = token
        self.username = username
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
    
    def create_repo(self, name: str, description: str = "") -> dict:
        """创建仓库"""
        url = f"{self.base_url}/user/repos"
        data = {
            "name": name,
            "description": description,
            "private": False,
            "auto_init": False,
            "license_template": "mit"
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 201:
            print(f"✅ 仓库 '{name}' 创建成功!")
            return response.json()
        elif response.status_code == 422:
            print(f"⚠️ 仓库 '{name}' 已存在，将推送到现有仓库")
            return self.get_repo(name)
        else:
            print(f"❌ 创建仓库失败: {response.status_code}")
            print(response.text)
            return None
    
    def get_repo(self, name: str) -> dict:
        """获取仓库信息"""
        url = f"{self.base_url}/repos/{self.username}/{name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_ref(self, repo_name: str, ref: str = "heads/main") -> str:
        """获取分支引用"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/git/ref/{ref}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()["object"]["sha"]
        return None
    
    def create_blob(self, repo_name: str, content: str) -> str:
        """创建文件Blob"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/git/blobs"
        data = {
            "content": base64.b64encode(content.encode()).decode(),
            "encoding": "base64"
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            return response.json()["sha"]
        return None
    
    def create_tree(self, repo_name: str, base_tree: str, files: list) -> str:
        """创建树对象"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/git/trees"
        
        tree = []
        for filepath, content in files:
            blob_sha = self.create_blob(repo_name, content)
            if blob_sha:
                tree.append({
                    "path": filepath,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                })
        
        data = {
            "base_tree": base_tree,
            "tree": tree
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            return response.json()["sha"]
        return None
    
    def create_commit(self, repo_name: str, message: str, tree_sha: str, parent_sha: str) -> str:
        """创建提交"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/git/commits"
        data = {
            "message": message,
            "tree": tree_sha,
            "parents": [parent_sha]
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            return response.json()["sha"]
        return None
    
    def update_ref(self, repo_name: str, ref: str, sha: str) -> bool:
        """更新分支引用"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/git/refs/{ref}"
        data = {"sha": sha}
        
        response = requests.patch(url, headers=self.headers, json=data)
        return response.status_code == 200
    
    def push_files(self, repo_name: str, repo_path: Path, commit_message: str = "Initial commit"):
        """推送文件到仓库"""
        # 获取仓库信息
        repo = self.get_repo(repo_name)
        if not repo:
            print(f"❌ 仓库 '{repo_name}' 不存在")
            return False
        
        # 获取默认分支
        default_branch = repo.get("default_branch", "main")
        
        # 获取基础树SHA
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/git/trees/{default_branch}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            base_tree = response.json()["sha"]
            # 获取最新提交SHA
            commits_url = f"{self.base_url}/repos/{self.username}/{repo_name}/commits/{default_branch}"
            commits_resp = requests.get(commits_url, headers=self.headers)
            if commits_resp.status_code == 200:
                parent_sha = commits_resp.json()["sha"]
            else:
                print("⚠️ 无法获取父提交，将创建新提交")
                parent_sha = None
        else:
            print("⚠️ 无法获取基础树，将创建新的树")
            base_tree = None
            parent_sha = None
        
        # 收集文件
        files = []
        exclude = {
            '.git', '__pycache__', '*.pyc', '.pytest_cache',
            'venv', 'env', '.venv', 'node_modules', '.idea', '.vscode'
        }
        
        for path in repo_path.rglob('*'):
            if path.is_file():
                # 排除文件
                rel_path = path.relative_to(repo_path).as_posix()
                if any(ex in str(path) for ex in exclude):
                    continue
                
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                    
                    # 尝试以UTF-8解码文本文件
                    try:
                        content = content.decode('utf-8')
                    except:
                        content = base64.b64encode(content).decode()
                    
                    files.append((rel_path, content))
                    print(f"📄 准备上传: {rel_path}")
                except Exception as e:
                    print(f"⚠️ 跳过文件 {rel_path}: {e}")
        
        print(f"\n共准备 {len(files)} 个文件")
        
        # 由于API限制，我们分批处理
        # 创建内容API调用
        for filepath, content in files:
            url = f"{self.base_url}/repos/{self.username}/{repo_name}/contents/{filepath}"
            data = {
                "message": f"Add {filepath}",
                "content": base64.b64encode(content.encode() if isinstance(content, str) else content).decode()
            }
            
            if parent_sha:
                data["sha"] = parent_sha
            
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                print(f"✅ 已上传: {filepath}")
            elif response.status_code == 422:
                # 文件已存在，更新
                # 获取文件SHA
                get_resp = requests.get(url, headers=self.headers)
                if get_resp.status_code == 200:
                    file_sha = get_resp.json()["sha"]
                    data["sha"] = file_sha
                    update_resp = requests.put(url, headers=self.headers, json=data)
                    if update_resp.status_code in [200, 201]:
                        print(f"✅ 已更新: {filepath}")
                    else:
                        print(f"⚠️ 更新失败 {filepath}: {update_resp.status_code}")
            else:
                print(f"⚠️ 上传失败 {filepath}: {response.status_code}")
        
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='推送代码到GitHub')
    parser.add_argument('token', help='GitHub Personal Access Token')
    parser.add_argument('--name', default='office-agent', help='仓库名称')
    parser.add_argument('--desc', default='智能办公自动化助手', help='仓库描述')
    parser.add_argument('--path', default='.', help='代码路径')
    
    args = parser.parse_args()
    
    pusher = GitHubPusher(args.token)
    
    # 创建仓库
    print(f"创建仓库: {args.name}")
    repo = pusher.create_repo(args.name, args.desc)
    
    if repo:
        # 推送文件
        print(f"\n推送文件到仓库...")
        repo_path = Path(args.path).resolve()
        success = pusher.push_files(args.name, repo_path)
        
        if success:
            print(f"\n✅ 完成!")
            print(f"🌐 仓库地址: {repo['html_url']}")
        else:
            print("\n❌ 推送失败")


if __name__ == "__main__":
    main()
