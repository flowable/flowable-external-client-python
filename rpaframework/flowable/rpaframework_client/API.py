import json
import os

from robot.api.deco import library, keyword


@library
class API:

    result = {}

    @keyword
    def flw_input(self, name: str):
        variables = os.environ["FLOWABLE_INPUT_VARIABLES"]
        obj = json.loads(variables)
        return obj[name]

    @keyword
    def flw_output(self, name: str, value: any):
        output_file_name = os.environ.get("FLOWABLE_OUTPUT_FILE")
        self.result[name] = value
        if output_file_name is not None:
            with open(output_file_name, "w") as f:
                f.write(json.dumps(self.result))
                f.close()
