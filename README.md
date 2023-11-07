# Flowable External Worker Library for Python


[License:
![license](https://img.shields.io/hexpm/l/plug.svg)](https://github.com/flowable/flowable-external-client-python/blob/main/LICENSE)

![Flowable Actions CI](https://github.com/flowable/flowable-external-client-python/actions/workflows/main.yml/badge.svg?branch=main)

An _External Worker Task_ in BPMN or CMMN is a task where the custom logic of that task is executed externally to Flowable, i.e. on another server.
When the process or case engine arrives at such a task, it will create an **external job**, which is exposed over the REST API.
Through this REST API, the job can be acquired and locked.
Once locked, the custom logic is responsible for signalling over REST that the work is done and the process or case can continue.

This project makes implementing such custom logic in Python easy by not having the worry about the low-level details of the REST API and focus on the actual custom business logic.
Integrations for other languages are available, too.

## Authentication

The different ways to authenticate are explained in the [documentation of the underlying requests HTTP library which is used to connect to Flowable](https://requests.readthedocs.io/en/latest/user/authentication/).
The `ExternalWorkerClient` accepts as a parameter `auth` an implementation of `requests.auth.AuthBase`.
There are default implementations for example for basic authentication e.g. `HTTPBasicAuth("admin", "test")`.
Flowable offers a bearer token implementation `FlowableCloudToken` which allows to specify an access token to the Flowable Cloud offering.

## Sample

### Cloud

The usage with Flowable Cloud is simpler, since everything is pre-configured.
However, it's required to either use the user credentials or to pre-configure a personal access token.

```python
from flowable.external_worker_client import ExternalWorkerClient
from flowable.external_worker_client.cloud_token import FlowableCloudToken

client = ExternalWorkerClient(auth=FlowableCloudToken("<personal-access-token>"))

def my_callback(job, worker_result_builder):
    print('Executed job: ' + job.id)
    return worker_result_builder.success()

subscription = client.subscribe('myTopic', my_callback)
```

### Local

The following is an example how you can connect to a Flowable instance running at `http://host.docker.internal:8090` and process all messages retrieved on the topic `myTopic`:

```python
from flowable.external_worker_client import ExternalWorkerClient
from requests.auth import HTTPBasicAuth

client = ExternalWorkerClient('http://localhost:8090/flowable-work', auth=HTTPBasicAuth("admin", "test"))

def my_callback(job, worker_result_builder):
    print('Executed job: ' + job.id)
    return worker_result_builder.success()

subscription = client.subscribe('myTopic', my_callback)
```

