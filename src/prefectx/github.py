import base64
import subprocess
from pathlib import Path
from httpx import AsyncClient


def get_github_token() -> str:
    """Get GitHub token from various local sources."""
    # Try getting from gh cli first
    try:
        token = subprocess.check_output(
            ["gh", "auth", "token"],
            text=True
        ).strip()
        if token:
            return token
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Try getting from git credential helper
    try:
        proc = subprocess.Popen(
            ["git", "credential", "fill"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        output, _ = proc.communicate("url=https://github.com\n\n")
        for line in output.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1]
    except subprocess.SubprocessError:
        pass

    # Try reading from ~/.git-credentials
    try:
        cred_path = Path.home() / ".git-credentials"
        if cred_path.exists():
            creds = cred_path.read_text()
            for line in creds.splitlines():
                if "https://" in line:
                    token = line.split(":")[-1].split("@")[0]
                    if token:
                        return token
    except Exception:
        pass

    raise RuntimeError(
        "Could not find GitHub token. Please ensure you:\n"
        "1. Are logged in via 'gh auth login'\n"
        "2. Or have credentials stored in git config\n"
        "3. Or have a token in ~/.git-credentials"
    )

async def create_github_repo(repo_name: str | None = None) -> str:
    """Creates a public GitHub repo using GitHub's API."""
    if repo_name is None:
        # You might want to implement unique_name() separately
        from uuid import uuid4
        repo_name = f"temp-repo-{uuid4().hex[:8]}"

    headers = {
        "Authorization": f"token {get_github_token()}"
    }

    data = {
        "name": repo_name
    }

    async with AsyncClient() as client:
        response = await client.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json=data
        )
        response.raise_for_status()

    return response.json()["clone_url"]

async def upload_file_to_repo(repo_name: str, filename: str, contents: str, branch: str = "main") -> None:
    """Uploads a file directly to GitHub using the Contents API."""
    repo_name = repo_name.replace("https://github.com/", "").replace(".git", "")

    content_bytes = contents.encode('utf-8')
    content_b64 = base64.b64encode(content_bytes).decode('utf-8')

    headers = {
        "Authorization": f"token {get_github_token()}"
    }

    data = {
        "message": "Add flow file",
        "content": content_b64,
        "branch": branch
    }

    async with AsyncClient() as client:
        response = await client.put(
            f"https://api.github.com/repos/{repo_name}/contents/{filename}",
            headers=headers,
            json=data
        )
        response.raise_for_status()

    return response.json()["content"]["url"]