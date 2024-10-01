import ast
import json
import os
import shlex
import tempfile

from flowable.external_worker_client import ExternalWorkerAcquireJobResponse, WorkerResultBuilder
from flowable.rpaframework_client.call_python_module import call_python_module


def extract_action_and_parameters(job):
    action = None
    params = []
    for variable in job.variables:
        if variable.name == '__rpaFrameworkTaskName':
            action = variable.value
        else:
            if variable.value is not None:
                params.append('--' + shlex.quote(variable.name) + '=' + shlex.quote(variable.value.__str__()))
    return action, params


def extract_action_and_parameters_map(job):
    action = None
    params = {}
    for variable in job.variables:
        if variable.name == '__rpaFrameworkTaskName':
            action = variable.value
        else:
            if variable.value is not None:
                params[variable.name] = variable.value
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


def add_variables_to_result(work_result, json_result):

    if isinstance(json_result, dict):
        for key in json_result:
            value = json_result[key]
            if isinstance(value, str):
                work_result.variable_string(key, value)
            elif isinstance(value, int):
                work_result.variable_int(key, value)
            elif isinstance(value, float):
                work_result.variable_float(key, value)
            elif isinstance(value, bool):
                work_result.variable_boolean(key, value)
            elif isinstance(value, object):
                work_result.variable_json(key, value)
            else:
                work_result.variable_string(key, str(value))
    else:
        work_result.variable_json('result', json_result)
    return work_result


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
        results = call_python_module(robocorp_args, mod_name='robocorp.actions')
        if results.returncode != 0:
            print('---> Job execution failed for "' + job.id + '". Output saved to ' + output_dir)
            return worker_result_builder.failure().error_message('failed with status code ' + str(results.returncode)).error_details(results.stderr + results.stdout)
        result = extract_result(results.stdout)
        print('---> Job execution done for "' + job.id + '" with result ' + result + '". Output saved to ' + output_dir, robocorp_args)
        work_result = worker_result_builder.success()
        json_result = ast.literal_eval(result)
        return add_variables_to_result(work_result, json_result)


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
        results = call_python_module(robocorp_args, mod_name='robocorp.tasks')
        if results.returncode != 0:
            print('---> Job execution failed for "' + job.id + '". Output saved to ' + output_dir)
            return worker_result_builder.failure().error_message('failed with status code ' + str(results.returncode)).error_details(results.stderr + results.stdout)
        print('---> Job execution done for "' + job.id + '". Output saved to ' + output_dir, robocorp_args)
        return worker_result_builder.success()


class RpaframeworkRobotHandler:
    def __init__(self, rpaframework_action_file: str):
        self.rpaframework_action_file = rpaframework_action_file

    def handle_task(self, job: ExternalWorkerAcquireJobResponse, worker_result_builder: WorkerResultBuilder):
        action, params = extract_action_and_parameters_map(job)
        if action is None:
            return worker_result_builder.failure().error_message('failed to find rpaframework action name')

        output_dir = create_output_dir(job)
        rpaframework_args = ['--rpa', '--name', action.__str__(), '--report', 'NONE', '--outputdir', output_dir, self.rpaframework_action_file]
        print('---> Execute job "' + job.id + '"', rpaframework_args)
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        new_env = os.environ.copy()
        new_env["FLOWABLE_INPUT_VARIABLES"] = json.dumps(params)
        new_env["FLOWABLE_OUTPUT_FILE"] = tmp.name
        results = call_python_module(rpaframework_args, mod_name='robot', env=new_env)

        if results.returncode != 0:
            print('---> Job execution failed for "' + job.id + '". Output saved to ' + output_dir)
            os.unlink(tmp.name)
            return worker_result_builder.failure().error_message('failed with status code ' + str(results.returncode)).error_details(results.stderr + results.stdout)
        print('---> Job execution done for "' + job.id + '". Output saved to ' + output_dir, rpaframework_args)

        with open(tmp.name, 'r') as content_file:
            content = json.loads(content_file.read())
        os.unlink(tmp.name)

        if content is None:
            return worker_result_builder.success()
        else:
            return add_variables_to_result(worker_result_builder.success(), content)
