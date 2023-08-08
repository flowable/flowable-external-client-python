from flowableexternalworker.engine_rest_variable import EngineRestVariable
from flowableexternalworker.external_worker_job_response import ExternalWorkerJobResponse


class ExternalWorkerAcquireJobResponse(ExternalWorkerJobResponse):

    def __init__(self, variables: list[EngineRestVariable], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variables = variables
