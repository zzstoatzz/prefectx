from uuid import UUID
from typing import Any

from prefect import get_client
from prefect.exceptions import ObjectNotFound
from prefect.client.schemas.actions import WorkPoolCreate
from prefect.client.schemas.objects import FlowRun
from prefect.utilities.callables import ParameterSchema, _generate_signature_from_source, _get_docstring_from_source, generate_parameter_schema, parameter_docstrings
from prefect.workers.utilities import get_default_base_job_template_for_infrastructure_type

from prefectx.utils import unique_name

PREFECT_MANAGED = "prefect:managed"
DEFAULT_WORK_POOL_NAME = "managed-work-pool"

async def ensure_managed_work_pool(name: str = DEFAULT_WORK_POOL_NAME) -> str:
    async with get_client() as client:
        try:
            work_pool = await client.read_work_pool(work_pool_name=name)
        except ObjectNotFound:
            template = await get_default_base_job_template_for_infrastructure_type(PREFECT_MANAGED)
            wp = WorkPoolCreate(
                name=name,
                type=PREFECT_MANAGED,
                base_job_template=template,
            )
            work_pool = await client.create_work_pool(work_pool=wp, overwrite=True)

    return work_pool.name

def create_pull_step(
    repo: str,
    branch: str = "main"
) -> dict[str, Any]:
    return {
        "prefect.deployments.steps.git_clone": {
            "branch": branch,
            "repository": repo
        }
    }

async def create_deployment(
    filename: str,
    flow_func: str,
    work_pool_name: str,
    repo: str,
    parameter_schema: ParameterSchema
):
    async with get_client() as client:
        flow_id = await client.create_flow_from_name(flow_func)
        deployment_id = await client.create_deployment(
            flow_id=flow_id,
            entrypoint=f"{filename}:{flow_func}",
            name=unique_name("deployment"),
            work_pool_name=work_pool_name,
            pull_steps=[create_pull_step(repo)],
            parameter_openapi_schema=parameter_schema.model_dump_for_openapi(),
        )
        return deployment_id


async def create_flow_run_from_deployment(deployment_id: UUID) -> FlowRun:
    async with get_client() as client:
        flow_run = await client.create_flow_run_from_deployment(
            deployment_id,
        )

    return flow_run


def get_parameter_schema_from_content(content: str, function_name: str) -> ParameterSchema:
    signature = _generate_signature_from_source(content, function_name)
    docstring = _get_docstring_from_source(content, function_name)
    return generate_parameter_schema(signature, parameter_docstrings(docstring))
