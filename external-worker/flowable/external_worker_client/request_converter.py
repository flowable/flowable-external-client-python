from flowable.external_worker_client.engine_rest_variable import EngineRestVariable


def convert_from_engine_rest_variable(o: EngineRestVariable) -> object:
    return {
        "name": o.name,
        "type": o.type,
        "value": o.value,
        "valueUrl": o.value_url
    }
