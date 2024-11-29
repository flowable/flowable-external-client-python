import argparse

from requests.auth import HTTPBasicAuth

from flowable.external_worker_client import ExternalWorkerClient
from flowable.external_worker_client.cloud_token import FlowableCloudToken
from flowable.rpaframework_client.rpaframework_handler import RobocorpActionHandler, RobocorpTaskHandler, RpaframeworkRobotHandler

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flowable RPA Framework Client")

    parser.add_argument('topic', help='Topic of the client to listen to')
    parser.add_argument('path', type=str, help='The directory or file with the RPA framework task to run.')
    parser.add_argument('--mode', type=str, choices=['robot', 'action', 'task'], default='robot', help='Type of rpaframework robot or robocorp action or task')
    parser.add_argument('--flowable-host', type=str, default='https://trial.flowable.com/work', help='URL of Flowable Work')
    parser.add_argument('--flowable-token', type=str, help='Bearer Token, can be used for example with the Flowable Trial')
    parser.add_argument('--flowable-username', type=str, help='Username for Flowable Work when using Basic Authentication')
    parser.add_argument('--flowable-password', type=str, help='Password for Flowable Work when using Basic Authentication')

    args = parser.parse_args()

    topic = args.topic
    auth = None
    if args.flowable_token:
        auth = FlowableCloudToken(args.flowable_token)
    elif args.flowable_username and args.flowable_password:
        auth = HTTPBasicAuth(args.flowable_username, args.flowable_password)

    print('---> Start consuming for topic "' + topic + '"')
    client = ExternalWorkerClient(args.flowable_host, auth=auth)

    if args.mode == 'action':
        job_handler = RobocorpActionHandler(args.path)
    elif args.mode == 'task':
        job_handler = RobocorpTaskHandler(args.path)
    else:
        job_handler = RpaframeworkRobotHandler(args.path)
    subscription = client.subscribe(topic, job_handler.handle_task)
