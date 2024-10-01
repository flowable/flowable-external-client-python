import unittest
from pathlib import Path

from requests.auth import HTTPBasicAuth

from tests.bpmn_utils import deploy_process, get_process_definition_id, delete_deployment

base_url = "http://localhost:8090/flowable-work"
auth = HTTPBasicAuth("admin", "test")


class BasicTest(unittest.TestCase):

    def deploy_process(self, fileToDeploy='externalWorkerProcess.bpmn'):
        self._process_deployment_id = deploy_process(base_url, auth, str(Path(__file__).parent.absolute()) + '/fixtures/processes/' + fileToDeploy)
        self._process_definition_id = get_process_definition_id(base_url, auth, self._process_deployment_id)

    def remove_deployment(self):
        if hasattr(self, "_process_deployment_id"):
            delete_deployment(base_url, auth, self._process_deployment_id)
