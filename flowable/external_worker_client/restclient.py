from typing import Callable

import requests
from requests import Session
from requests.auth import AuthBase

from flowable.external_worker_client import response_converter
from flowable.external_worker_client.engine_rest_variable import EngineRestVariable
from flowable.external_worker_client.external_worker_acquire_job_response import ExternalWorkerAcquireJobResponse
from flowable.external_worker_client.external_worker_job_response import ExternalWorkerJobResponse
from flowable.external_worker_client.flowable_rest_exception import FlowableRestException
from flowable.external_worker_client.list_result import ListResult
from flowable.external_worker_client.request_converter import convert_from_engine_rest_variable

JOB_API = '/external-job-api'


class FlowableExternalWorkerRestClient(object):
    """
    Create a REST API Client for the Flowable External Worker.
    Used to communicate with the REST API and exchange information.
    """

    def __init__(
            self,
            flowable_host: str,
            worker_id: str,
            auth: AuthBase = None,
            customize_session: Callable[[Session], None] = lambda session: None
    ) -> None:
        self.flowable_host: str = flowable_host
        self.worker_id: str = worker_id
        self.request_session: Session = requests.Session()
        if auth is not None:
            self.request_session.auth = auth
        if customize_session is not None:
            customize_session(self.request_session)

    def list_jobs(self) -> ListResult[ExternalWorkerJobResponse]:
        r = self.request_session.get(self.flowable_host + JOB_API + '/jobs')

        if r.status_code != 200:
            raise FlowableRestException(r.status_code, r.text)

        result = r.json()
        jobs = list(map(response_converter.convert_to_external_worker_job_response, result.get('data')))

        return ListResult(
            jobs,
            result.get('total'),
            result.get('start'),
            result.get('sort'),
            result.get('order'),
            result.get('size')
        )

    def get_job(self, job_id: str) -> ExternalWorkerJobResponse:
        r = self.request_session.get(self.flowable_host + JOB_API + "/jobs/" + job_id)
        if r.status_code != 200:
            raise FlowableRestException(r.status_code, r.text)

        return response_converter.convert_to_external_worker_job_response(r.json())

    def acquire_jobs(
            self,
            topic: str,
            lock_duration: str,
            number_of_tasks: int = 1,
            number_of_retries: int = 5,
            worker_id: str = None,
            scope_type: str = None
    ) -> list[ExternalWorkerAcquireJobResponse]:
        r = self.request_session.post(
            self.flowable_host + JOB_API + '/acquire/jobs',
            json={
                "topic": topic,
                "lockDuration": lock_duration,
                "numberOfTasks": number_of_tasks,
                "numberOfRetries": number_of_retries,
                "workerId": worker_id or self.worker_id,
                "scopeType": scope_type
            },
            headers={
                "Content-Type": "application/json"
            }
        )
        if r.status_code != 200:
            raise FlowableRestException(r.status_code, r.text)

        return list(map(response_converter.convert_to_external_worker_acquire_job_response, r.json()))

    def complete_job(self, job_id: str, variables: list[EngineRestVariable] = None, worker_id: str = None) -> None:
        request_variables = list(map(convert_from_engine_rest_variable, variables or []))

        r = self.request_session.post(
            self.flowable_host + JOB_API + '/acquire/jobs/' + job_id + '/complete',
            json={
                "workerId": worker_id or self.worker_id,
                "variables": request_variables
            },
            headers={
                "Content-Type": "application/json"
            }
        )
        if r.status_code != 204:
            raise FlowableRestException(r.status_code, r.text)

    def job_with_bpmn_error(self, job_id: str, variables: list[EngineRestVariable] = None, error_code: str = None, worker_id: str = None) -> None:
        request_variables = list(map(convert_from_engine_rest_variable, variables or []))

        r = self.request_session.post(
            self.flowable_host + JOB_API + '/acquire/jobs/' + job_id + '/bpmnError',
            json={
                "workerId": worker_id or self.worker_id,
                "variables": request_variables,
                "errorCode": error_code
            },
            headers={
                "Content-Type": "application/json"
            }
        )
        if r.status_code != 204:
            raise FlowableRestException(r.status_code, r.text)

    def fail_job(self, job_id: str, error_message: str = None, error_details: str = None, retries: int = None, retry_timeout: str = None, worker_id: str = None) -> None:
        r = self.request_session.post(
            self.flowable_host + JOB_API + '/acquire/jobs/' + job_id + '/fail',
            json={
                "workerId": worker_id or self.worker_id,
                "errorMessage": error_message,
                "errorDetails": error_details,
                "retries": retries,
                "retryTimeout": retry_timeout
            }
        )
        if r.status_code != 204:
            raise FlowableRestException(r.status_code, r.text)

    def job_with_cmmn_terminate(self, job_id: str, variables: list[EngineRestVariable], worker_id: str = None):
        request_variables = list(map(convert_from_engine_rest_variable, variables or []))
        r = self.request_session.post(
            self.flowable_host + JOB_API + '/acquire/jobs/' + job_id + '/cmmnTerminate',
            json={
                "workerId": worker_id or self.worker_id,
                "variables": request_variables
            }
        )
        if r.status_code != 204:
            raise FlowableRestException(r.status_code, r.text)

