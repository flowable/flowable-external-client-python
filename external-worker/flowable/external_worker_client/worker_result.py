from __future__ import annotations
from abc import abstractmethod

from flowable.external_worker_client import ExternalWorkerAcquireJobResponse, EngineRestVariable
from flowable.external_worker_client.restclient import FlowableExternalWorkerRestClient


class WorkResult(object):
    @abstractmethod
    def execute(self, rest_client: FlowableExternalWorkerRestClient):
        pass


class WorkResultWithVariables(object):

    def __init__(self):
        self._variables: list[EngineRestVariable] = []

    def variable_string(self, name: str, value: str):
        self._variables.append(EngineRestVariable(name, "string", value))
        return self

    def variable_int(self, name: str, value: int):
        self._variables.append(EngineRestVariable(name, "integer", value))
        return self

    def variable_float(self, name: str, value: float):
        self._variables.append(EngineRestVariable(name, "double", value))
        return self

    def variable_boolean(self, name: str, value: bool):
        self._variables.append(EngineRestVariable(name, "boolean", value))
        return self

    def variable_json(self, name: str, value: object):
        self._variables.append(EngineRestVariable(name, "json", value))
        return self


class WorkerResultSuccess(WorkResult, WorkResultWithVariables):

    def __init__(self, job: ExternalWorkerAcquireJobResponse):
        super().__init__()
        self._job_id = job.id

    def execute(self, rest_client: FlowableExternalWorkerRestClient):
        rest_client.complete_job(self._job_id, self._variables)


class WorkerResultFailure(WorkResult):

    def __init__(self, job: ExternalWorkerAcquireJobResponse):
        self._job_id = job.id
        self._error_message = None
        self._error_details = None
        self._retries = None
        self._retry_timeout = None

    def error_message(self, error_message: str) -> WorkerResultFailure:
        self._error_message = error_message
        return self

    def error_details(self, error_details: str) -> WorkerResultFailure:
        self._error_details = error_details
        return self

    def retries(self, retries: int) -> WorkerResultFailure:
        self._retries = retries
        return self

    def retry_timeout(self, retry_timeout: str) -> WorkerResultFailure:
        self._retry_timeout = retry_timeout
        return self

    def execute(self, rest_client: FlowableExternalWorkerRestClient):
        rest_client.fail_job(self._job_id, self._error_message, self._error_details, self._retries, self._retry_timeout)


class WorkerResultBpmnError(WorkResult, WorkResultWithVariables):

    def __init__(self, job: ExternalWorkerAcquireJobResponse):
        super().__init__()
        self._job_id = job.id
        self._error_code = None

    def error_code(self, error_code: str) -> WorkerResultBpmnError:
        self._error_code = error_code
        return self

    def execute(self, rest_client: FlowableExternalWorkerRestClient):
        rest_client.job_with_bpmn_error(self._job_id, self._variables, self._error_code)


class WorkerResultCmmnTerminate(WorkResult, WorkResultWithVariables):

    def __init__(self, job: ExternalWorkerAcquireJobResponse):
        super().__init__()
        self._job_id = job.id

    def execute(self, rest_client: FlowableExternalWorkerRestClient):
        rest_client.job_with_cmmn_terminate(self._job_id, self._variables)

