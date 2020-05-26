import json

from woqlclient import APIEndpointConst


def mocked_requests(*args, **kwargs):
    class MockResponse:
        def json(self):
            if self._json_data is None:
                raise ValueError("EXCEPTION NO JSON OBJECT")
            return self._json_data

        @property
        def status_code(self):
            return self._status_code

        @property
        def url(self):
            return self._url

        @property
        def text(self):
            return self._text

        def __init__(self, url, status, action_type):

            # set status code and content
            self._json_data = None
            self._text = None
            self._status_code = status
            self._content = "cont"
            self._url = url
            # add json data if provided
            print("ACTION TYPE", action_type) #why print?
            if action_type == APIEndpointConst.CONNECT:
                with open("tests/capabilitiesResponse.json") as json_file:
                    json_data = json.load(json_file)
                    self._json_data = json_data
                    json_file.close()

            elif action_type == APIEndpointConst.GET_SCHEMA:
                with open("tests/getSchemaTurtleResponse.txt") as text_file:
                    self._text = text_file.read()
                    text_file.close()

            elif action_type == APIEndpointConst.WOQL_SELECT:
                with open("tests/getAllClassQueryResponse.json") as json_file:
                    json_data = json.load(json_file)
                    self._json_data = json_data
                    json_file.close()

            elif (
                action_type == APIEndpointConst.CREATE_DATABASE
                or action_type == APIEndpointConst.DELETE_DATABASE
                or action_type == APIEndpointConst.UPDATE_SCHEMA
            ):
                self._json_data = {"terminus:status": "terminus:success"}

    if (
        args[0]
        == "http://localhost:6363/myFirstTerminusDB/schema?terminus%3Aencoding=terminus%3Aturtle"
    ):
        return MockResponse(args[0], 200, APIEndpointConst.GET_SCHEMA)

    elif args[0] == "http://195.201.12.87:6363/myFirstTerminusDB/schema":
        return MockResponse(args[0], 200, APIEndpointConst.UPDATE_SCHEMA)

    elif args[0].find("http://localhost:6363/myFirstTerminusDB/woql") != -1:
        return MockResponse(args[0], 200, APIEndpointConst.WOQL_SELECT)

    elif args[0] == "http://localhost:6363/myFirstTerminusDB":
        return MockResponse(args[0], 200, APIEndpointConst.DELETE_DATABASE)

    return MockResponse(args[0], 200, APIEndpointConst.CONNECT)
