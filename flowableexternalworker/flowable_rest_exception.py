class FlowableRestException(Exception):
    def __init__(self, status_code, content=None):
        if content is not None and content != '':
            super().__init__("Failed to call Flowable with status code " + str(status_code) + " and content '" + content + "'")
        else:
            super().__init__("Failed to call Flowable with status code " + str(status_code))
