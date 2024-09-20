import argparse

from requests.auth import HTTPBasicAuth

from flowable.external_worker_client import ExternalWorkerClient
from flowable.external_worker_client.cloud_token import FlowableCloudToken
from flowable.robocorp_client.robocorp_handler import RobocorpActionHandler, RobocorpTaskHandler

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flowable Robocorp Client")

    parser.add_argument('topic', help='Topic of the Robocorp Action to listen to')
    parser.add_argument('mode', type=str, choices=['action', 'task'], help='Type of robocorp action/task')
    parser.add_argument('path', type=str, help='The directory or file with the actions/tasks to run.')
    parser.add_argument('--flowable-host', type=str, default='https://trial.flowable.com', help='URL of Flowable Work')
    parser.add_argument('--flowable-token', type=str, help='Bearer Token, can be used for example with the Flowable Trial')
    parser.add_argument('--flowable-username', type=str, help='Username for Flowable Work when using Basic Authentication')
    parser.add_argument('--flowable-password', type=str, help='Password for Flowable Work when using Basic Authentication')

    args = parser.parse_args()

    topic = args.topic
    robocorp_action_file = args.path
    auth = None
    if args.flowable_token:
        auth = FlowableCloudToken(args.flowable_token)
    elif args.flowable_username and args.flowable_password:
        auth = HTTPBasicAuth(args.flowable_username, args.flowable_password)

    print('---> Start consuming for topic "' + topic + '"')
    client = ExternalWorkerClient(args.flowable_host, auth=auth)

    if args.mode == 'action':
        robocorp_job_handler = RobocorpActionHandler(robocorp_action_file)
    else:
        robocorp_job_handler = RobocorpTaskHandler(robocorp_action_file)
    subscription = client.subscribe(topic, robocorp_job_handler.handle_task)
