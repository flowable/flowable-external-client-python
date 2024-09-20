from flowable.external_worker_client.engine_rest_variable import EngineRestVariable
from flowable.external_worker_client.external_worker_acquire_job_response import ExternalWorkerAcquireJobResponse
from flowable.external_worker_client.external_worker_job_response import ExternalWorkerJobResponse
from flowable.external_worker_client.utils import parse_date_time


def convert_to_external_worker_job_response(o) -> ExternalWorkerJobResponse:
    return ExternalWorkerJobResponse(
        o.get('id'),
        o.get('url'),
        o.get('correlationId'),
        o.get('processInstanceId'),
        o.get('executionId'),
        o.get('scopeId'),
        o.get('subScopeId'),
        o.get('scopeDefinitionId'),
        o.get('scopeType'),
        o.get('elementId'),
        o.get('elementName'),
        o.get('retries'),
        o.get('exceptionMessage'),
        parse_date_time(o.get('dueDate')),
        parse_date_time(o.get('createTime')),
        o.get('tenantId'),
        o.get('lockOwner'),
        parse_date_time(o.get('lockExpirationTime')),
    )


def convert_to_external_worker_acquire_job_response(o) -> ExternalWorkerAcquireJobResponse:
    return ExternalWorkerAcquireJobResponse(
        list(map(convert_to_engine_rest_variable, o.get('variables'))),
        id=o.get('id'),
        url=o.get('url'),
        correlation_id=o.get('correlationId'),
        process_instance_id=o.get('processInstanceId'),
        execution_id=o.get('executionId'),
        scope_id=o.get('scopeId'),
        sub_scope_id=o.get('subScopeId'),
        scope_definition_id=o.get('scopeDefinitionId'),
        scope_type=o.get('scopeType'),
        element_id=o.get('elementId'),
        element_name=o.get('elementName'),
        retries=o.get('retries'),
        exception_message=o.get('exceptionMessage'),
        due_date=parse_date_time(o.get('dueDate')),
        create_time=parse_date_time(o.get('createTime')),
        tenant_id=o.get('tenantId'),
        lock_owner=o.get('lockOwner'),
        lock_expiration_time=parse_date_time(o.get('lockExpirationTime')),
    )


def convert_to_engine_rest_variable(o) -> EngineRestVariable:
    return EngineRestVariable(
        o.get('name'),
        o.get('type'),
        o.get('value'),
        o.get('valueUrl')
    )
