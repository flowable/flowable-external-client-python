import requests
from requests.auth import AuthBase


def deploy_process(base_url: str, auth: AuthBase, file: str) -> str:
    files = {'file': open(file, 'rb')}
    deployment_result = requests.post(base_url + '/process-api/repository/deployments', auth=auth, files=files)
    assert deployment_result.status_code == 201
    return deployment_result.json().get("id")


def delete_deployment(base_url: str, auth: AuthBase, process_deployment_id: str) -> None:
    delete_deployment_result = requests.delete(base_url + "/process-api/repository/deployments/" + process_deployment_id, auth=auth)
    assert delete_deployment_result.status_code == 204


def get_process_definition_id(base_url: str, auth: AuthBase, process_deployment_id: str) -> None:
    definition_search = requests.get(base_url + "/process-api/repository/process-definitions?deploymentId=" + process_deployment_id, auth=auth)
    assert definition_search.status_code == 200
    data = definition_search.json().get("data")
    assert len(data) == 1
    return data[0].get("id")


def start_process(base_url: str, auth: AuthBase, process_definition_id: str) -> str:
    start_result = requests.post(
        base_url + "/process-api/runtime/process-instances",
        auth=auth,
        json={"processDefinitionId": process_definition_id},
        headers={"Content-Type": "application/json"}
    )
    assert start_result.status_code == 201
    return start_result.json().get("id")


def terminate_process(base_url: str, auth: AuthBase, process_instance_id: str) -> None:
    delete_result = requests.delete(base_url + "/process-api/runtime/process-instances/" + process_instance_id, auth=auth)
    assert delete_result.status_code == 204


def get_process_variable(base_url: str, auth: AuthBase, process_instance_id: str, variable_name: str) -> dict | None:
    variable_result = requests.get(base_url + "/process-api/history/historic-variable-instances?processInstanceId=" + process_instance_id + "&variableName=" + variable_name, auth=auth)
    assert variable_result.status_code == 200
    data = variable_result.json().get("data")
    if len(data) == 1:
        return data[0].get("variable")
    else:
        return None


def executed_activity_ids(base_url: str, auth: AuthBase, process_instance_id: str) -> list[str]:
    activity_instances = requests.get(base_url + "/process-api/history/historic-activity-instances?processInstanceId=" + process_instance_id, auth=auth)
    assert activity_instances.status_code == 200
    data = activity_instances.json().get("data")
    return sorted(list(map(lambda o: o.get("activityId"), data)))
