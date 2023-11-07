import threading
import time
from os import getpid
from socket import gethostname
from typing import Callable, Union

from requests import Session
from requests.auth import AuthBase

from flowable.external_worker_client.engine_rest_variable import EngineRestVariable
from flowable.external_worker_client.external_worker_acquire_job_response import ExternalWorkerAcquireJobResponse
from flowable.external_worker_client.restclient import FlowableExternalWorkerRestClient
from flowable.external_worker_client.worker_result import WorkerResultSuccess, WorkerResultFailure, WorkerResultBpmnError, WorkerResultCmmnTerminate, WorkResult


class WorkerResultBuilder(object):

    def __init__(self, job: ExternalWorkerAcquireJobResponse):
        self._job = job

    def success(self) -> WorkerResultSuccess:
        return WorkerResultSuccess(self._job)

    def failure(self) -> WorkerResultFailure:
        return WorkerResultFailure(self._job)

    def cmmn_terminate(self) -> WorkerResultCmmnTerminate:
        return WorkerResultCmmnTerminate(self._job)

    def bpmn_error(self) -> WorkerResultBpmnError:
        return WorkerResultBpmnError(self._job)


class ExternalWorkerSubscription(object):

    def __init__(self, thread: threading.Thread, event: threading.Event):
        self.thread = thread
        self.event = event

    def unsubscribe(self, timeout: float = None):
        self.event.set()
        self.thread.join(timeout)


CallbackHandlerType = Union[
    Callable[[ExternalWorkerAcquireJobResponse, WorkerResultBuilder], WorkResult],
    Callable[[ExternalWorkerAcquireJobResponse, WorkerResultBuilder], None]
]


class ExternalWorkerClient(object):

    def __init__(
            self,
            flowable_host: str = "https://cloud.flowable.com/work",
            worker_id: str = None,
            auth: AuthBase = None,
            customize_session: Callable[[Session], None] = lambda session: None
    ) -> None:
        self._restClient = FlowableExternalWorkerRestClient(
            flowable_host=flowable_host,
            worker_id=worker_id or gethostname() + '-' + str(getpid()),
            auth=auth,
            customize_session=customize_session
        )

    def subscribe(
            self,
            topic,
            callback_handler: CallbackHandlerType,
            lock_duration: str = "PT1M",
            number_of_retries: int = 5,
            scope_type: str = None,
            wait_period_seconds: int = 30,
            number_of_tasks: int = 1
    ) -> ExternalWorkerSubscription:
        event = threading.Event()
        thread = threading.Thread(target=self._consume,
                                  args=(event, topic, callback_handler, lock_duration, number_of_retries, scope_type, wait_period_seconds, number_of_tasks))
        thread.start()
        return ExternalWorkerSubscription(thread, event)

    def _consume(
            self,
            event: threading.Event,
            topic: str,
            callback_handler: CallbackHandlerType,
            lock_duration: str,
            number_of_retries: int,
            scope_type: str,
            wait_period_seconds: int,
            number_of_tasks: int
    ):
        while not event.is_set():
            jobs = self._restClient.acquire_jobs(topic, lock_duration, number_of_tasks, number_of_retries=number_of_retries, scope_type=scope_type)
            if len(jobs) == 0:
                time.sleep(wait_period_seconds)

            for job in jobs:
                try:
                    result = callback_handler(job, WorkerResultBuilder(job))
                    if result is not None:
                        result.execute(self._restClient)
                    else:
                        self._restClient.complete_job(job.id)
                except:
                    self._restClient.fail_job(job.id)
