class EngineRestVariable(object):

    def __init__(self, name: str, type: str, value: object, value_url: str = None):
        self.name = name
        self.type = type
        self.value = value
        self.value_url = value_url
