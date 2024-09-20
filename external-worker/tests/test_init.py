import time
from datetime import timedelta

from flowable.external_worker_client import ExternalWorkerClient, WorkerResultBuilder, ExternalWorkerAcquireJobResponse, CallbackHandlerType
from tests.basic_test import BasicTest, base_url, auth
from tests.bpmn_utils import start_process, executed_activity_ids, terminate_process, get_process_variable
from tests.cmmn_utils import start_case, get_case_variable
from tests.vcr import my_vcr


class TestExternalWorkerClient(BasicTest):

    @classmethod
    def setUpClass(cls):
        cls._client = ExternalWorkerClient(
            base_url,
            auth=auth,
            worker_id='test-worker'
        )

    @my_vcr.use_cassette
    def test_consume(self):
        self.deploy_process()
        process_instance_id = start_process(base_url, auth, self._process_definition_id)
        try:
            def callback(job: ExternalWorkerAcquireJobResponse, work_result_builder: WorkerResultBuilder):
                return work_result_builder.success()

            #  Act
            self._consume_one_call(callback)

            activity_ids = executed_activity_ids(base_url, auth, process_instance_id)
            self.assertEqual(sorted(["startnoneevent1", "bpmnSequenceFlow_2", "bpmnTask_3", "bpmnSequenceFlow_4", "bpmnEndEvent_1"]), activity_ids)
        finally:
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_consume_with_bpmn_error(self):
        self.deploy_process()
        process_instance_id = start_process(base_url, auth, self._process_definition_id)
        try:
            def callback(job: ExternalWorkerAcquireJobResponse, work_result_builder: WorkerResultBuilder):
                return work_result_builder.failure() \
                    .error_message("Test Error Message") \
                    .error_details("Some error details") \
                    .retries(3) \
                    .retry_timeout("PT5M")

            #  Act
            failed_job = self._consume_one_call(callback)

            job_details = self._client._restClient.get_job(failed_job.id)

            self.assertEqual(3, job_details.retries)
            self.assertEqual("Test Error Message", job_details.exception_message)

            # The expiration time should be around five minutes after the start time
            expected_expiration_time = job_details.create_time + timedelta(minutes=5)
            difference = job_details.lock_expiration_time - expected_expiration_time
            self.assertLess(abs(difference.total_seconds()), 5)

            self.assertIsNone(job_details.lock_owner)

            activity_ids = executed_activity_ids(base_url, auth, process_instance_id)
            self.assertEqual(sorted(["startnoneevent1", "bpmnSequenceFlow_2", "bpmnTask_3"]), activity_ids)
        finally:
            terminate_process(base_url, auth, process_instance_id)
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_consume_with_cmmn_terminate(self):
        self.deploy_case()
        case_instance_id = start_case(base_url, auth, self._case_definition_id)
        try:
            def callback(job: ExternalWorkerAcquireJobResponse, work_result_builder: WorkerResultBuilder):
                return work_result_builder.cmmn_terminate() \
                    .variable_string("testVar", "test terminate")

            #  Act
            self._consume_one_call(callback, "cmmnTopic")

            variable = get_case_variable(base_url, auth, case_instance_id, "testVar")
            self.assertIsNotNone(variable)
            self.assertEqual("string", variable.get("type"))
            self.assertEqual("test terminate", variable.get("value"))
        finally:
            self.remove_deployment()

    @my_vcr.use_cassette
    def test_subscribe_with_bpmn_error(self):
        try:
            self.deploy_process('withBoundaryEvent.bpmn')
            process_instance_id = start_process(base_url, auth, self._process_definition_id)

            def callback(job: ExternalWorkerAcquireJobResponse, work_result_builder: WorkerResultBuilder):
                return work_result_builder.bpmn_error() \
                    .variable_string("testVar", "test failure") \
                    .error_code("errorCode1")

            #  Act
            self._consume_one_call(callback)

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

    def _consume_one_call(self, callback_handler: CallbackHandlerType, topic="myTopic") -> ExternalWorkerAcquireJobResponse:
        result = type('', (object,), {"completed": False, "job": None})()

        def callback(job: ExternalWorkerAcquireJobResponse, worker_result_builder: WorkerResultBuilder):
            return_value = callback_handler(job, worker_result_builder)
            result.job = job
            result.completed = True
            return return_value

        subscription = self._client.subscribe(topic, callback, wait_period_seconds=1)
        i = 0
        while i < 10 and not result.completed:
            time.sleep(0.2)
            i = i + 1
        subscription.unsubscribe(10)
        self.assertTrue(result.completed)
        return result.job
