import json
import shlex

from flowable.external_worker_client import ExternalWorkerAcquireJobResponse, WorkerResultBuilder
from flowable.robocorp_client.call_robocorp import call_robocorp


def extract_action_and_parameters(job):
    action = None
    params = []
    for variable in job.variables:
        if variable.name == '__robocorpTaskName':
            action = variable.value
        else:
            if variable.value is not None:
                params.append('--' + shlex.quote(variable.name) + '=' + shlex.quote(variable.value.__str__()))
    return action, params


def extract_result(results):
    result_item = None
    lines = results.strip().splitlines()
    for line in lines:
        parsed = json.loads(line)
        if parsed['message_type'] == 'R':
            result_item = parsed
    result = None
    if result_item is not None:
        result = result_item['value']
    return result


def create_output_dir(job):
    return 'output/' + job.id + '-' + (job.scope_id or job.process_instance_id) + '-' + job.element_id


class RobocorpActionHandler:
    def __init__(self, robocorp_action_file: str):
        self.robocorp_action_file = robocorp_action_file

    def handle_task(self, job: ExternalWorkerAcquireJobResponse, worker_result_builder: WorkerResultBuilder):
        action, params = extract_action_and_parameters(job)
        if action is None:
            return worker_result_builder.failure().error_message('failed to find robocorp action name')

        output_dir = create_output_dir(job)
        robocorp_args = ['run', self.robocorp_action_file, '-a' + action.__str__(), '--log-output-to-stdout=json', '-o' + output_dir, '--']
        robocorp_args.extend(params)
        print('---> Execute job "' + job.id + '"', robocorp_args)
        results = call_robocorp(robocorp_args)
        if results.returncode != 0:
            return worker_result_builder.failure().error_message('failed with status code ' + str(results.returncode)).error_details(results.stdout)
        result = extract_result(results.stdout)
        print('---> Job execution done for "' + job.id + '" with result ' + result + '". Output saved to ' + output_dir, robocorp_args)
        return worker_result_builder.success().variable_string('result', result)


class RobocorpTaskHandler:
    def __init__(self, robocorp_action_file: str):
        self.robocorp_action_file = robocorp_action_file

    def handle_task(self, job: ExternalWorkerAcquireJobResponse, worker_result_builder: WorkerResultBuilder):
        action, params = extract_action_and_parameters(job)
        if action is None:
            return worker_result_builder.failure().error_message('failed to find robocorp action name')

        output_dir = create_output_dir(job)
        robocorp_args = ['run', self.robocorp_action_file, '-t' + action.__str__(), '-o' + output_dir, '--']
        robocorp_args.extend(params)
        print('---> Execute job "' + job.id + '"', robocorp_args)
        results = call_robocorp(robocorp_args, mod_name='robocorp.tasks')
        if results.returncode != 0:
            return worker_result_builder.failure().error_message('failed with status code ' + str(results.returncode)).error_details(results.stdout)
        print('---> Job execution done for "' + job.id + '". Output saved to ' + output_dir, robocorp_args)
        return worker_result_builder.success()
