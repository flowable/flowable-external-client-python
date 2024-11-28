import os
import subprocess
import sys
from time import sleep

import requests

from tests.basic_test import BasicTest, base_url, auth
from tests.bpmn_utils import start_process, terminate_process, get_process_variable

from tests.vcr import my_vcr


class TestRestClient(BasicTest):
    @my_vcr.use_cassette
    def test_with_custom_action(self):
        self.run_test(
            [sys.executable, "-m", 'flowable.rpaframework_client',
             '--flowable-host', base_url,
             '--flowable-username', auth.username,
             '--flowable-password', auth.password,
             '--mode', 'action',
             'myTopic',
             os.path.join(os.path.dirname(os.path.abspath(__file__)), 'robocorp_action_weather.py')
             ]
        )

    @my_vcr.use_cassette
    def test_with_robot(self):
        self.run_test(
            [sys.executable, "-m", 'flowable.rpaframework_client',
             '--flowable-host', base_url,
             '--flowable-username', auth.username,
             '--flowable-password', auth.password,
             'myTopic',
             os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rpaframework_weather.robot')
             ]
        )

    def run_test(self, call_args):
        self.deploy_process('rpaframeworkExample.bpmn')
        process_instance_id = start_process(base_url, auth, self._process_definition_id, [
            {'name': 'city', 'type': 'string', 'value': 'Zurich'},
            {'name': 'days', 'type': 'integer', 'value': 3}
        ])
        try:

            print(" ".join(call_args))

            r = requests.get(base_url + '/external-job-api/jobs?processInstanceId=' + process_instance_id, auth=auth)
            result = r.json()
            job = result.get('data')[0].get('id')

            print('start subprocess with parameters', call_args)
            process = subprocess.Popen(call_args, text=True)
            i = 0
            while i < 10 and job is not None:
                # we are adding the i that vcr is not assuming it's the same request
                r = requests.get(base_url + '/external-job-api/jobs/' + job + '?i=' + str(i), auth=auth)
                if r.status_code == 200:
                    print('waiting for job to complete', job)
                    sleep(0.2)
                else:
                    job = None
                i += 1

            process.terminate()

            temperature = get_process_variable(base_url, auth, process_instance_id, 'temperature')
            self.assertIsNotNone(temperature)
            self.assertEqual(temperature['value'], 18)
        finally:
            terminate_process(base_url, auth, process_instance_id)
            self.remove_deployment()
