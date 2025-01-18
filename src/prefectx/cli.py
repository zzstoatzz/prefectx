from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
from prefect.cli.root import PrefectTyper
from prefect.utilities.urls import url_for

from prefectx.ast_utils import add_flow_decorator
from prefectx.github import create_github_repo, upload_file_to_repo
from prefectx.prefect_utils import ensure_managed_work_pool, create_deployment, get_parameter_schema_from_content, create_flow_run_from_deployment

app = PrefectTyper()

@app.command()
async def main(filename: str, flow_func: str):
    with Progress(
        SpinnerColumn(),
        TextColumn("[blue]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Prefect-ifying your workflow...", total=None)

        raw_contents = Path(filename).read_text()
        contents_as_flow = add_flow_decorator(raw_contents, flow_func)
        parameter_schema = get_parameter_schema_from_content(raw_contents, flow_func)

        progress.update(task, description="Creating temporary storage...")
        repo_url = await create_github_repo()

        progress.update(task, description="Uploading to temporary storage...")
        await upload_file_to_repo(repo_url, filename, contents_as_flow)

        progress.update(task, description="Creating work pool...")
        work_pool = await ensure_managed_work_pool()

        progress.update(task, description="Deploying flow...")
        deployment_id = await create_deployment(filename, flow_func, work_pool, repo_url, parameter_schema)

        progress.update(task, description="Running deployment...")

        flow_run = await create_flow_run_from_deployment(deployment_id)

    app.console.print(f"View run at: {url_for(flow_run)}", style="blue")