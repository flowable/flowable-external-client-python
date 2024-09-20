import unittest
from datetime import datetime
from pathlib import Path

from requests import Session
from requests.auth import HTTPBasicAuth

from flowable.external_worker_client import restclient
from flowable.external_worker_client.engine_rest_variable import EngineRestVariable
from tests.basic_test import base_url, auth, BasicTest
from tests.bpmn_utils import deploy_process, delete_deployment, start_process, terminate_process, get_process_definition_id, get_process_variable, \
    executed_activity_ids
from tests.cmmn_utils import deploy_case, get_case_definition_id, delete_case_deployment, start_case, get_case_variable
from tests.vcr import my_vcr


def basic_auth(session: Session):
    session.auth = ('admin', 'test')

class TestRestClient(BasicTest):

    @classmethod
    def setUpClass(cls):
        cls._client = restclient.FlowableExternalWorkerRestClient(
            base_url,
            auth=auth,
            worker_id='test-worker'
        )

    @my_vcr.use_cassette
    def test_list_jobs_customize_session(self):
        self.deploy_process()
        process_instance_id = start_process(base_url, auth, self._process_definition_id)
        try:
            client = restclient.FlowableExternalWorkerRestClient(
                base_url,
                customize_session=basic_auth,
                worker_id='test-worker'
            )
            jobs = client.list_jobs()
            self.assertEqual(1, jobs.total)
        finally:
            terminate_process(base_url, auth, process_instance_id)
            self.remove_deployment()

    @my_vcr.use_cassette("test_list_jobs_invalid_auth.yml")
    def test_list_jobs_invalid_auth(self):
        self.deploy_process()
        process_instance_id = start_process(base_url, auth, self._process_definition_id)
        try:
            client = restclient.FlowableExternalWorkerRestClient(
                base_url,
                auth=HTTPBasicAuth("invalid", "auth"),
                worker_id='test-worker'
            )
            with self.assertRaises(restclient.FlowableRestException) as context:
                client.list_jobs()

            self.assertEqual("Failed to call Flowable with status code 401", context.exception.args[0])
        finally:
            terminate_process(base_url, auth, process_instance_id)
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_list_jobs(self):
        self.deploy_process()
        process_instance_id = start_process(base_url, auth, self._process_definition_id)
        try:
            jobs = self._client.list_jobs()
            self.assertEqual(1, jobs.total)
            first_entry = jobs.data[0]
            self.assertEqual('External Worker task', first_entry.element_name)
            self.assertEqual(3, first_entry.retries)
            self.assertLess(first_entry.create_time, datetime.now())
        finally:
            terminate_process(base_url, auth, process_instance_id)
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_get_job(self):
        self.deploy_process()
        process_instance_id = start_process(base_url, auth, self._process_definition_id)
        try:
            jobs = self._client.list_jobs()
            self.assertEqual(1, jobs.total)
            first_entry = jobs.data[0]
            self.assertEqual("External Worker task", first_entry.element_name)
            self.assertEqual(3, first_entry.retries)
            self.assertLess(first_entry.create_time, datetime.now())

            job_id = first_entry.id
            job = self._client.get_job(job_id)
            self.assertEqual("External Worker task", job.element_name)
            self.assertEqual(3, job.retries)
            self.assertLess(job.create_time, datetime.now())
        finally:
            terminate_process(base_url, auth, process_instance_id)
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_acquire_jobs(self):
        self.deploy_process()
        process_instance_id = start_process(base_url, auth, self._process_definition_id)
        try:
            acquired_jobs = self._client.acquire_jobs("myTopic", "PT10S")
            self.assertEqual(1, len(acquired_jobs))

            first_entry = acquired_jobs[0]
            self.assertEqual('External Worker task', first_entry.element_name)
            self.assertLess(first_entry.create_time, datetime.now())
            self.assertEqual(1, len(first_entry.variables))

            first_variable = first_entry.variables[0]
            self.assertEqual('initiator', first_variable.name)
            self.assertEqual('admin', first_variable.value)
        finally:
            terminate_process(base_url, auth, process_instance_id)
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_complete_job(self):
        try:
            self.deploy_process()
            process_instance_id = start_process(base_url, auth, self._process_definition_id)
            acquired_jobs = self._client.acquire_jobs("myTopic", "PT10S")
            self.assertEqual(1, len(acquired_jobs))

            first_entry = acquired_jobs[0]
            self.assertEqual('External Worker task', first_entry.element_name)

            job_id = first_entry.id
            variables: list[EngineRestVariable] = [
                EngineRestVariable("testVar", "string", "test content")
            ]

            self._client.complete_job(job_id, variables)

            variable = get_process_variable(base_url, auth, process_instance_id, "testVar")
            self.assertIsNotNone(variable)
            self.assertEqual("string", variable.get("type"))
            self.assertEqual("test content", variable.get("value"))

            activity_ids = executed_activity_ids(base_url, auth, process_instance_id)
            self.assertEqual(sorted(["startnoneevent1", "bpmnSequenceFlow_2", "bpmnTask_3", "bpmnSequenceFlow_4", "bpmnEndEvent_1"]), activity_ids)

        finally:
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_job_with_bpmn_error_without_error_code_execute_first(self):
        try:
            self.deploy_process('withBoundaryEvent.bpmn')
            process_instance_id = start_process(base_url, auth, self._process_definition_id)
            acquired_jobs = self._client.acquire_jobs("myTopic", "PT10S")
            self.assertEqual(1, len(acquired_jobs))

            first_entry = acquired_jobs[0]
            self.assertEqual('External Worker task', first_entry.element_name)

            job_id = first_entry.id
            variables: list[EngineRestVariable] = [
                EngineRestVariable("testVar", "string", "test failure")
            ]

            self._client.job_with_bpmn_error(job_id, variables)

            variable = get_process_variable(base_url, auth, process_instance_id, "testVar")
            self.assertIsNotNone(variable)
            self.assertEqual("string", variable.get("type"))
            self.assertEqual("test failure", variable.get("value"))

            activity_ids = executed_activity_ids(base_url, auth, process_instance_id)
            self.assertEqual(sorted(
                ["startnoneevent1", "bpmnSequenceFlow_2", "bpmnTask_3", "bpmnBoundaryEvent_3", "bpmnSequenceFlow_6", "bpmnEndEvent_5", "bpmnBoundaryEvent_4"]),
                activity_ids
            )

        finally:
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_job_with_bpmn_error_without_error_code_1_execute_first(self):
        try:
            self.deploy_process('withBoundaryEvent.bpmn')
            process_instance_id = start_process(base_url, auth, self._process_definition_id)
            acquired_jobs = self._client.acquire_jobs("myTopic", "PT10S")
            self.assertEqual(1, len(acquired_jobs))

            first_entry = acquired_jobs[0]
            self.assertEqual('External Worker task', first_entry.element_name)

            job_id = first_entry.id
            variables: list[EngineRestVariable] = [
                EngineRestVariable("testVar", "string", "test failure")
            ]

            self._client.job_with_bpmn_error(job_id, variables, error_code="errorCode1")

            variable = get_process_variable(base_url, auth, process_instance_id, "testVar")
            self.assertIsNotNone(variable)
            self.assertEqual("string", variable.get("type"))
            self.assertEqual("test failure", variable.get("value"))

            activity_ids = executed_activity_ids(base_url, auth, process_instance_id)
            self.assertEqual(sorted(
                ["startnoneevent1", "bpmnSequenceFlow_2", "bpmnTask_3", "bpmnBoundaryEvent_3", "bpmnSequenceFlow_6", "bpmnEndEvent_5", "bpmnBoundaryEvent_4"]),
                activity_ids
            )

        finally:
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_job_with_bpmn_error_without_error_code_2_execute_second(self):
        try:
            self.deploy_process('withBoundaryEvent.bpmn')
            process_instance_id = start_process(base_url, auth, self._process_definition_id)
            acquired_jobs = self._client.acquire_jobs("myTopic", "PT10S")
            self.assertEqual(1, len(acquired_jobs))

            first_entry = acquired_jobs[0]
            self.assertEqual('External Worker task', first_entry.element_name)

            job_id = first_entry.id
            variables: list[EngineRestVariable] = [
                EngineRestVariable("testVar", "string", "test failure")
            ]

            self._client.job_with_bpmn_error(job_id, variables, error_code="errorCode2")

            variable = get_process_variable(base_url, auth, process_instance_id, "testVar")
            self.assertIsNotNone(variable)
            self.assertEqual("string", variable.get("type"))
            self.assertEqual("test failure", variable.get("value"))

            activity_ids = executed_activity_ids(base_url, auth, process_instance_id)
            self.assertEqual(sorted(
                ["startnoneevent1", "bpmnSequenceFlow_2", "bpmnTask_3", "bpmnBoundaryEvent_3", "bpmnSequenceFlow_8", "bpmnEndEvent_7", "bpmnBoundaryEvent_4"]),
                activity_ids
            )

        finally:
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_fail_job(self):
        self.deploy_process()
        process_instance_id = start_process(base_url, auth, self._process_definition_id)
        try:
            acquired_jobs = self._client.acquire_jobs("myTopic", "PT10S")
            self.assertEqual(1, len(acquired_jobs))

            first_entry = acquired_jobs[0]
            self.assertEqual('External Worker task', first_entry.element_name)
            self.assertEqual(3, first_entry.retries)

            job_id = first_entry.id

            self._client.fail_job(job_id)

            job_after_fail = self._client.get_job(job_id)
            self.assertEqual(2, job_after_fail.retries)

            activity_ids = executed_activity_ids(base_url, auth, process_instance_id)
            self.assertEqual(sorted(["startnoneevent1", "bpmnSequenceFlow_2", "bpmnTask_3"]), activity_ids)

        finally:
            terminate_process(base_url, auth, process_instance_id)
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_job_with_cmmn_terminate(self):
        self.deploy_case()
        case_instance_id = start_case(base_url, auth, self._case_definition_id)
        try:
            acquired_jobs = self._client.acquire_jobs("cmmnTopic", "PT10S")
            self.assertEqual(1, len(acquired_jobs))

            first_entry = acquired_jobs[0]
            self.assertEqual('External Worker task', first_entry.element_name)

            job_id = first_entry.id
            variables: list[EngineRestVariable] = [
                EngineRestVariable("testVar", "string", "test terminate")
            ]

            self._client.job_with_cmmn_terminate(job_id, variables)

            variable = get_case_variable(base_url, auth, case_instance_id, "testVar")
            self.assertIsNotNone(variable)
            self.assertEqual("string", variable.get("type"))
            self.assertEqual("test terminate", variable.get("value"))

        finally:
            self.remove_deployment()
