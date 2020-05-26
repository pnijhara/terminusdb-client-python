# from .errorMessage import ErrorMessage
from base64 import b64encode

import requests

from .api_endpoint_const import APIEndpointConst
from .errors import APIError
from .utils import Utils


class DispatchRequest:
    def __init__(self):
        pass

    @staticmethod
    def __get_call(url, headers, payload):
        url = Utils.addParamsToUrl(url, payload)

        return requests.get(url, headers=headers)

    @staticmethod
    def __post_call(url, headers, payload, file_dict=None):
        if file_dict:
            return requests.post(url, json=payload, headers=headers, files=file_dict)
        else:
            headers["content-type"] = "application/json"
            return requests.post(url, json=payload, headers=headers)

    @staticmethod
    def __delete_call(url, headers, payload):
        url = Utils.addParamsToUrl(url, payload)
        return requests.delete(url, headers=headers)

    @staticmethod
    def __autorization_header(key=None, jwt=None):
        headers = {}

        # if (payload and ('terminus:user_key' in  payload)):
        # Utils.encodeURIComponent(payload['terminus:user_key'])}
        if key:
            headers["Authorization"] = "Basic %s" % b64encode(
                (":" + key).encode("utf-8")
            ).decode("utf-8")
            if jwt:
                headers["HUB_AUTHORIZATION"] = "Bearer %s" % jwt
        # payload.pop('terminus:user_key')
        elif jwt:
            headers["Authorization"] = "Bearer %s" % jwt

        return headers

    # url, action, payload, basic_auth, jwt=null

    @classmethod
    def send_request_by_action(
        cls, url, action, key, payload={}, file_dict=None, jwt=None
    ):  # payload default as empty dict is against PEP
        print("Sending to URL____________", url)
        print("Send Request By Action_____________", action)

        try:
            request_response = None
            headers = cls.__autorization_header(key, jwt)

            if action in [
                APIEndpointConst.CONNECT,
                APIEndpointConst.GET_SCHEMA,
                APIEndpointConst.CLASS_FRAME,
                APIEndpointConst.WOQL_SELECT,
                APIEndpointConst.GET_DOCUMENT,
            ]:
                request_response = cls.__get_call(url, headers, payload)

            elif action in [
                APIEndpointConst.DELETE_DATABASE,
                APIEndpointConst.DELETE_DOCUMENT,
            ]:
                request_response = cls.__delete_call(url, headers, payload)

            elif action in [
                APIEndpointConst.CREATE_DATABASE,
                APIEndpointConst.UPDATE_SCHEMA,
                APIEndpointConst.CREATE_DOCUMENT,
                APIEndpointConst.WOQL_UPDATE,
            ]:
                request_response = cls.__post_call(url, headers, payload, file_dict)

            if request_response.status_code == 200:
                return request_response.json()  # if not a json not it raises an error
            else:
                # Raise an exception if a request is unsuccessful
                message = "Api Error"

                if type(request_response.text) is str:
                    message = request_response.text

                raise (
                    APIError(
                        message,
                        url,
                        request_response.json(),
                        request_response.status_code,
                    )
                )

        # to be reviewed
        # the server in the response return always content-type application/json
        except ValueError as err:
            # if the response type is not a json
            print("Value Error", err)
            return request_response.text

        """
        except Exception as err:
            print(type(err))
            print(err.args)

        except requests.exceptions.RequestException as err:
            print ("Request Error",err)
        except requests.exceptions.HTTPError as err:
            print ("Http Error:",err)
        except requests.exceptions.ConnectionError as err:
            print ("Error Connecting:",err)
        except requests.exceptions.Timeout as err:
            print ("Timeout Error:",err)
        """
