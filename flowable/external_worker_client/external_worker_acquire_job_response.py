from flowable.external_worker_client.engine_rest_variable import EngineRestVariable
from flowable.external_worker_client.external_worker_job_response import ExternalWorkerJobResponse


class ExternalWorkerAcquireJobResponse(ExternalWorkerJobResponse):

    def __init__(self, variables: list[EngineRestVariable], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variables = variables
