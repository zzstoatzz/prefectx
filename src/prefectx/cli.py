import json
from pathlib import Path

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from prefect.cli.root import PrefectTyper
from prefect.utilities.urls import url_for
from prefectx.ast_utils import add_flow_decorator
from prefectx.prefect_utils import (
    create_deployment,
    create_flow_run_from_deployment,
    ensure_managed_work_pool,
    get_parameter_schema_from_content,
    store_code_in_variable,
)

app = PrefectTyper()


@app.command()
async def main(
    filename: str,
    flow_func: str,
    parameters: Annotated[str, typer.Option()] = None,
):
    parsed_parameters = {}
    if parameters:
        try:
            parsed_parameters = json.loads(parameters)
        except json.JSONDecodeError:
            app.console.print("Error: Parameters must be valid JSON", style="red")
            return

    with Progress(
        SpinnerColumn(),
        TextColumn("[blue]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Prefect-ifying your workflow...", total=None)

        raw_contents = Path(filename).read_text()
        contents_as_flow = add_flow_decorator(raw_contents, flow_func)
        parameter_schema = get_parameter_schema_from_content(raw_contents, flow_func)

        progress.update(task, description="Uploading code to temporary storage...")
        variable_name = await store_code_in_variable(contents_as_flow)

        progress.update(task, description="Creating work pool...")
        work_pool = await ensure_managed_work_pool()

        progress.update(task, description="Deploying flow...")
        deployment_id = await create_deployment(
            filename, flow_func, work_pool, variable_name, parameter_schema
        )

        progress.update(task, description="Running deployment...")

        flow_run = await create_flow_run_from_deployment(
            deployment_id, parsed_parameters
        )

    app.console.print(f"View run: {url_for(flow_run)}", style="blue", no_wrap=True)
