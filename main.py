import os
import git
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def get_git_diff(repo_path="."):
    repo = git.Repo(repo_path)
    # ステージングされていない変更とステージング済みの変更の両方を取得
    diff = repo.git.diff("HEAD", "--cached") + "\n" + repo.git.diff()
    return diff

def generate_commit_message(diff):
    if not diff:
        return "No changes detected"
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    prompt = f"以下のgit diffの変更内容を要約し、Markdown形式でコミットメッセージを生成してください:\n\n{diff}"
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }
    
    response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def generate_markdown(repo_path="."):
    try:
        # リポジトリパスを正規化
        repo_path = os.path.expanduser(repo_path)
        if not os.path.exists(repo_path):
            raise Exception(f"指定されたパスが存在しません: {repo_path}")
            
        repo = git.Repo(repo_path)
        diff = get_git_diff(repo_path)
        
        if not diff:
            print("変更がありません")
            return None
            
        markdown_content = generate_commit_message(diff)
        
        # Markdownファイルに保存
        output_path = os.path.join(repo_path, "CHANGES.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        print(f"Markdownファイルを生成しました: {output_path}")
        print(f"指定されたリポジトリの直下にCHANGES.mdファイルを作成しました")
        print(f"例: /path/to/blog-app/CHANGES.md")
        print(f"ファイルを開くには以下を実行してください:")
        print(f"open {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Markdown生成中にエラーが発生しました: {str(e)}")
        return None

def main():
    try:
        repo_path = input("コミットメッセージを生成したいリポジトリのパスを入力してください: ")
        repo_path = os.path.expanduser(repo_path) if repo_path else "."
        
        if not os.path.exists(repo_path):
            raise Exception(f"指定されたパスが存在しません: {repo_path}")
            
        output_path = generate_markdown(repo_path)
        
        if output_path:
            print(f"\n生成されたMarkdownファイルを開くには以下を実行してください:")
            print(f"open {output_path}")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()
