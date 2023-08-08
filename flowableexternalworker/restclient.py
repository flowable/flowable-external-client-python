from datetime import datetime
from typing import Generic, TypeVar, Callable

import requests
from requests import Session
from requests.auth import AuthBase

T = TypeVar('T')


class ListResult(Generic[T]):
    def __init__(self, data, total, start, sort, order, size) -> None:
        self.data: list[T] = data
        self.total: int = total
        self.start: int = start
        self.sort: str = sort
        self.order: str = order
        self.size: int = size


class FlowableRestException(Exception):
    def __init__(self, status_code, content=None):
        if content is not None and content != '':
            super().__init__("Failed to call Flowable with status code " + str(status_code) + " and content '" + content + "'")
        else:
            super().__init__("Failed to call Flowable with status code " + str(status_code))


class ExternalWorkerJob(object):
    def __init__(
            self,
            id,
            url,
            correlation_id,
            process_instance_id,
            execution_id,
            scope_id,
            sub_scope_id,
            scope_definition_id,
            scope_type,
            element_id,
            element_name,
            retries,
            exception_message,
            due_date,
            create_time,
            tenant_id,
            lock_owner,
            lock_expiration_time
    ):
        self.id: str = id
        self.url: str = url
        self.correlation_id: str = correlation_id
        self.process_instance_id: str = process_instance_id
        self.execution_id: str = execution_id
        self.scope_id: str = scope_id
        self.sub_scope_id: str = sub_scope_id
        self.scope_definition_id: str = scope_definition_id
        self.scope_type: str = scope_type
        self.element_id: str = element_id
        self.element_name: str = element_name
        self.retries: int = retries
        self.exception_message: str = exception_message
        self.due_date: datetime = due_date
        self.create_time: datetime = create_time
        self.tenant_id: str = tenant_id
        self.lock_owner: str = lock_owner
        self.lock_expiration_time: datetime = lock_expiration_time


class FlowableExternalWorkerRestClient(object):
    """
    Create a REST API Client for the Flowable External Worker.
    Used to communicate with the REST API and exchange information.
    """

    def __init__(self, flowable_host: str, auth: AuthBase = None, customize_session: Callable[[Session], None] = lambda session: None) -> None:
        self.flowable_host: str = flowable_host
        self.request_session: Session = requests.Session()
        if auth is not None:
            self.request_session.auth = auth
        if customize_session is not None:
            customize_session(self.request_session)

    def list_jobs(self) -> ListResult[ExternalWorkerJob]:
        r = self.request_session.get(self.flowable_host + '/external-job-api/jobs')

        if r.status_code != 200:
            raise FlowableRestException(r.status_code, r.text)

        result = r.json()
        jobs = list(map(lambda o: ExternalWorkerJob(
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
        ), result.get('data')))

        return ListResult(
            jobs,
            result.get('total'),
            result.get('start'),
            result.get('sort'),
            result.get('order'),
            result.get('size')
        )


def parse_date_time(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ") if date is not None else None
