from requests.auth import AuthBase


class FlowableCloudToken(AuthBase):
    """Attaches HTTP Bearer Authentication to the given Request object."""

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return all([
            self.token == getattr(other, "token", None),
        ])

    def __ne__(self, other):
        return not self == other

    def __call__(self, request):
        request.headers["Authorization"] = "Bearer " + self.token
        return request
