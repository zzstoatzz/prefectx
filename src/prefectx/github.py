import base64
import uuid
from pathlib import Path

from httpx import AsyncClient

from prefectx.settings import settings
from prefectx.utils import unique_name

async def create_github_repo(repo_name: str | None = None) -> str:
    """Creates a public GitHub repo using GitHub's API."""
    if repo_name is None:
        repo_name = unique_name("temp-repo")

    headers = {
        "Authorization": f"token {settings.github_token}"
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
    # Clean repo name - remove .git and any URL parts
    repo_name = repo_name.replace("https://github.com/", "").replace(".git", "")

    # Encode contents
    content_bytes = contents.encode('utf-8')
    content_b64 = base64.b64encode(content_bytes).decode('utf-8')

    headers = {
        "Authorization": f"token {settings.github_token}"
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
