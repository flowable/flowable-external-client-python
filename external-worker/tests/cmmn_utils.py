import requests
from requests.auth import AuthBase


def deploy_case(base_url: str, auth: AuthBase, file: str) -> str:
    files = {'file': open(file, 'rb')}
    deployment_result = requests.post(base_url + '/cmmn-api/cmmn-repository/deployments', auth=auth, files=files)
    assert deployment_result.status_code == 201
    return deployment_result.json().get("id")


def delete_case_deployment(base_url: str, auth: AuthBase, deployment_id: str) -> None:
    delete_deployment_result = requests.delete(base_url + "/cmmn-api/cmmn-repository/deployments/" + deployment_id, auth=auth)
    assert delete_deployment_result.status_code == 204


def get_case_definition_id(base_url: str, auth: AuthBase, deployment_id: str) -> None:
    definition_search = requests.get(base_url + "/cmmn-api/cmmn-repository/case-definitions?deploymentId=" + deployment_id, auth=auth)
    assert definition_search.status_code == 200
    data = definition_search.json().get("data")
    assert len(data) == 1
    return data[0].get("id")


def start_case(base_url: str, auth: AuthBase, case_definition_id: str) -> str:
    start_result = requests.post(
        base_url + "/cmmn-api/cmmn-runtime/case-instances",
        auth=auth,
        json={"caseDefinitionId": case_definition_id},
        headers={"Content-Type": "application/json"}
    )
    assert start_result.status_code == 201
    return start_result.json().get("id")


def terminate_case(base_url: str, auth: AuthBase, case_instance_id: str) -> None:
    delete_result = requests.delete(base_url + "/cmmn-api/cmmn-runtime/case-instances/" + case_instance_id, auth=auth)
    assert delete_result.status_code == 204


def get_case_variable(base_url: str, auth: AuthBase, case_instance_id: str, variable_name: str) -> dict | None:
    variable_result = requests.get(base_url + "/cmmn-api/cmmn-history/historic-variable-instances?caseInstanceId=" + case_instance_id + "&variableName=" + variable_name, auth=auth)
    assert variable_result.status_code == 200
    data = variable_result.json().get("data")
    if len(data) == 1:
        return data[0].get("variable")
    else:
        return None


def executed_plan_item_instance_ids(base_url: str, auth: AuthBase, case_instance_id: str) -> list[str]:
    activity_instances = requests.get(base_url + "/cmmn-api/cmmn-history/historic-planitem-instances?caseInstanceId=" + case_instance_id, auth=auth)
    assert activity_instances.status_code == 200
    data = activity_instances.json().get("data")
    return sorted(list(map(lambda o: o.get("planItemDefinitionId"), data)))
