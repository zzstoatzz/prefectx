from pathlib import Path

from prefect.utilities.urls import url_for

from prefectx.ast_utils import add_flow_decorator
from prefectx.github import create_github_repo, upload_file_to_repo
from prefectx.prefect_utils import ensure_managed_work_pool, create_deployment, get_parameter_schema_from_content, create_flow_run_from_deployment


async def main(filename: str, flow_func: str):
    raw_contents = Path(filename).read_text()
    contents_as_flow = add_flow_decorator(raw_contents, flow_func)
    parameter_schema = get_parameter_schema_from_content(raw_contents, flow_func)

    print("Turning your workflow into a prefect flow...")

    repo_url = await create_github_repo()
    await upload_file_to_repo(repo_url, filename, contents_as_flow)

    work_pool = await ensure_managed_work_pool()
    deployment_id = await create_deployment(filename, flow_func, work_pool, repo_url, parameter_schema)
    flow_run = await create_flow_run_from_deployment(deployment_id)

    print(f"View run at: {url_for(flow_run)}")