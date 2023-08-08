import unittest
from datetime import datetime

from requests import Session
from requests.auth import HTTPBasicAuth

from flowableexternalworker import restclient


def basic_auth(session: Session):
    session.auth = ('admin', 'test')


class TestRestClient(unittest.TestCase):
    def test_list_jobs_customize_session(self):
        client = restclient.FlowableExternalWorkerRestClient(
            "http://localhost:8090",
            customize_session=basic_auth
        )
        jobs = client.list_jobs()
        self.assertEqual(1, jobs.total)
        first_entry = jobs.data[0]
        self.assertEqual('External Worker task', first_entry.element_name)
        self.assertEqual(3, first_entry.retries)
        self.assertLess(first_entry.create_time, datetime.now())

    def test_list_jobs_auth(self):
        client = restclient.FlowableExternalWorkerRestClient(
            "http://localhost:8090",
            auth=HTTPBasicAuth("admin", "test")
        )
        jobs = client.list_jobs()
        self.assertEqual(1, jobs.total)

    def test_list_jobs_invalid_auth(self):
        client = restclient.FlowableExternalWorkerRestClient(
            "http://localhost:8090",
            auth=HTTPBasicAuth("invalid", "auth")
        )
        with self.assertRaises(restclient.FlowableRestException) as context:
            client.list_jobs()

        self.assertEqual("Failed to call Flowable with status code 401", context.exception.args[0])
