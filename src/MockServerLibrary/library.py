import requests
import json
from urllib.parse import urljoin
from robot.api import logger

from .version import VERSION

__version__ = VERSION


class MockServerLibrary(object):
    """Robot Framework library for interacting with [http://www.mock-server.com|MockServer]

    The purpose of this library is to provide a keyword-based API
    towards MockServer to be used in robot tests. The project is hosted in
    [https://github.com/frankvanderkuur/robotframework-mockserverlibrary|GitHub],
    and packages are released to PyPI.

    = Installation =

    | pip install robotframework-mockserverlibrary

    = Importing =

    The library does not currently support any import arguments, so use the
    following setting to take the library into use:

    | Library | MockServerLibrary |

    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def create_mock_session(self, base_url):
        """Creates an HTTP session towards mockserver.

        `base_url` is the full url (including port, if applicable) of the mockserver,
        e.g. http://localhost:1080.
        """
        logger.debug("robotframework-wiremock libary version: {}".format(__version__))
        self.base_url = base_url
        self.session = requests.Session()

    def create_mock_request_matcher(self, method, path, body_type='JSON', body=None, exact=True, queryparams=None):
        """Creates a mock request matcher to be used by mockserver.

        Returns the request matcher in a dictionary format.

        `method` is the HTTP method of the mocked endpoint

        `path` is the url of the mocked endpoint, e.g. /api

        `body_type` is the type of the request body, e.g. JSON

        `body` is a dictionary or string of the json attribute(s) to match

        `exact` is a boolean value which specifies whether the body should match fully (=true),
        or if only specified fields should match (=false)
        
        `queryparams` expects a dictionary or queryparameters that should match

        """
        req = {}
        req['method'] = method
        req['path'] = path

        if(queryparams):
            req['queryStringParameters'] = queryparams

        if isinstance(body, str):
            json_string = body
        else:
            json_string = json.dumps(body)

        if body_type == 'JSON' and body:
            match_type = 'STRICT' if exact else 'ONLY_MATCHING_FIELDS'
            req['body'] = {'type': body_type, 'json': json_string, 'matchType': match_type}

        if body_type == 'JSON_SCHEMA' and body:
            req['body'] = {'type': body_type, 'jsonSchema': json_string}

        return req

    def create_mock_response(self, status_code, headers=None, body_type='JSON', body=None, delay=0, unit='SECONDS'):
        """Creates a mock response to be used by mockserver.

        Returns the response in a dictionary format.

        `status_code` is the HTTP status code of the response

        `headers` is a dictionary of headers to be added to the response

        `body_type` is the type of the response body, e.g. JSON

        `body` is either a string that contains the full body or a dictonary of JSON attribute(s) to be added to the
        response body

        `delay` is the delay that is used for the response 

        `unit` is the unit of the delay time (default "SECONDS")
        """
        rsp = {}
        rsp['statusCode'] = int(status_code)

        if headers:
            rsp['headers'] = []

            for key, value in headers.items():
                header = {'name': key, 'values': value.split(",")}
                rsp['headers'].append(header)
                logger.debug("Add header - header: {}".format(header))

        if body_type == 'JSON' and body:
            # Check if body is a dict or a plain file and process accordingly
            if isinstance(body, dict):
                rsp['body'] = json.dumps(body)
            else:
                rsp['body'] = body
                
        if delay > 0:
            rsp['delay'] = {'timeUnit': unit, 'value': delay}

        return rsp

    def create_mock_http_forward(self, rewrite_path="", forward_host="", forward_port="",
                                 forward_scheme="", delay=0, unit='SECONDS'):
        """Creates a mock http override forward to be used by mockserver.

        Returns the http forward in a dictionary format.

        `rewrite_path` is the new path you want to use for the forwarded request

        `forward_host` is the new hostname to where you want to forward the request

        `forward_port` the different port you want to forward the request to

        `forward_scheme` the different schema you want to forward the request to (e.g. HTTP or HTTPS)

        `delay` is the delay of the forward action (default 0)

        `unit` is the unit of the delay time (default "SECONDS")
        """
        fwd = {}
        fwd['httpRequest'] = {}
        if rewrite_path:
            fwd['httpRequest']['path'] = rewrite_path

        forward_headers = {}
        if forward_host:
            forward_headers["Host"] = forward_host

        if forward_port:
            forward_headers["Port"] = forward_port

        if forward_scheme:
            forward_headers["Scheme"] = forward_scheme

        if forward_headers:
            fwd['httpRequest']['headers'] = forward_headers

        if delay > 0:
            fwd['delay'] = {'timeUnit': unit, 'value': delay}

        return fwd

    def create_mock_expectation_with_http_forward(self, request, forward, id="", count=0):
        """Creates a mock expectation with request and forward action to be used by mockserver.

        `request` is a mock request matcher in a dictionary format.

        `forward` is a mock forward in a dictionary format.

        `id` is a self-appointed unique identifier for the expectation.

        `count` the number of requests mockserver will serve this expectation. Unlimited when set to 0 (default)
        """
        data = {}
        data['httpRequest'] = request
        data['httpOverrideForwardedRequest'] = forward
        if id != "":
            data['id'] = id
        if count > 0:
            data['times'] = {'remainingTimes': int(count), 'unlimited': False}
        else:
            data['times'] = {'unlimited': True}

        self.create_mock_expectation_with_data(data)

    def create_mock_expectation(self, request, response, id="", count=0, priority=0):
        """Creates a mock expectation to be used by mockserver.

        `request` is a mock request matcher in a dictionary format.

        `response` is a mock response in a dictionary format.

        `id` is a self-appointed unique identifier for the expectation.

        `count` the number of requests mockserver will serve this expectation. Unlimited when set to 0 (default)

        `priority` matching is ordered by priority (highest first) then creation (earliest first)
        """
        data = {}
        data['httpRequest'] = request
        data['httpResponse'] = response
        if id != "":
            data['id'] = id
        if count > 0:
            data['times'] = {'remainingTimes': int(count), 'unlimited': False}
        else:
            data['times'] = {'unlimited': True}
        if priority > 0:
            data['priority'] = priority
        self.create_mock_expectation_with_data(data)

    def create_default_mock_expectation(self, method, path, response_code=200,
                                        response_headers=None, body_type='JSON',
                                        response_body=None):
        """Creates a default expectation to be used by mockserver.

        `method` is the HTTP method of the mocked endpoint

        `path` is the url of the mocked endpoint, e.g. /api

        `response_code` is the HTTP status code of the response

        `response_headers` is a dictionary of headers to be added to the response

        `body_type` is the type of the response body, e.g. JSON

        `response_body` is a dictonary of JSON attribute(s) to be added to the response body
        """
        req = self.create_mock_request_matcher(method, path, exact=False)
        rsp = self.create_mock_response(response_code, response_headers, body_type, response_body)
        self.create_mock_expectation(req, rsp, unlimited=True)

    def create_mock_expectation_with_data(self, data):
        """Creates a mock expectation with defined data to be used by mockserver.

        `data` is a dictionary or JSON string with mock data. Please see
        [https://app.swaggerhub.com/apis/jamesdbloom/mock-server_api|MockServer documentation]
        for the detailed API reference.
        """
        self._send_request("/expectation", data)

    def verify_mock_expectation(self, request, count=1, exact=True):
        """Verifies that the mockserver has received a specific request.

        `request` is a request expectation created using the keyword `Create Mock Request Matcher`

        `count` is the minimum expected number of requests

        `exact` specifies whether the expected count should match the actual received count
        """
        data = {}
        data['httpRequest'] = request
        if exact:
            data['times'] = {'atLeast': int(count), 'atMost': int(count)}
        else:
            data['times'] = {'atLeast': int(count)}

        self.verify_mock_expectation_with_data(data)

    def verify_mock_expectation_by_id(self, id, count=1, exact=True):
        """Verifies that the mockserver has received a specific request.

        `id` is a self-appointed unique identifier for the expectation when creating the expectation.

        `count` is the minimum expected number of requests

        `exact` specifies whether the expected count should match the actual received count
        """
        data = {}
        data['expectationId'] = {'id': id}
        if exact:
            data['times'] = {'atLeast': int(count), 'atMost': int(count)}
        else:
            data['times'] = {'atLeast': int(count)}

        self.verify_mock_expectation_with_data(data)

    def verify_mock_expectation_with_data(self, data):
        """Verifies a mock expectation with specified data.

        `data` is a dictionary or JSON string with mock data. Please see
        [https://app.swaggerhub.com/apis/jamesdbloom/mock-server_api|MockServer documentation]
        for the detailed API reference.
        """
        self._send_request("/verify", data)

    def verify_mock_sequence(self, requests):
        """Verifies that the mockserver has received a specific ordered request sequence.

        `requests` is a list of request expectations created using the keyword
        `Create Mock Request Matcher`
        """
        body = {}
        body["httpRequests"] = requests
        data = json.dumps(body)
        self._send_request("/verifySequence", data)

    def retrieve_requests(self, path):
        """Retrieves requests from the mockserver

        `path` is the url of the endpoint for which to retrieve requests, e.g. /api
        """
        body = {}
        body['path'] = path
        data = json.dumps(body)
        return self._send_request("/retrieve", data)

    def retrieve_expectations(self, path):
        """Retrieves expectations from the mockserver.

        `path` is the url of the endpoint for which to retrieve expectations, e.g. /api
        """
        body = {}
        body['path'] = path
        data = json.dumps(body)
        return self._send_request("/retrieve?type=active_expectations", data)

    def clear_requests(self, path):
        """Clears expectations and requests for a specific endpoint from the mockserver.

        `path` is the url of the endpoint for which to clean expectations and requests, e.g. /api
        """
        body = {}
        body['path'] = path
        data = json.dumps(body)
        self._send_request("/clear", data)

    def clear_requests_by_id(self, id, type="all"):
        """Clears expectations and recorded requests that match the given id.

        `id` is the id of the expectation you wish to clear

        `type` specifies the type of information to clear (all, log or expectation)
        """
        possible_types = ['all', 'log', 'expectation']

        body = {}
        body['id'] = id
        data = json.dumps(body)
        if type.lower() not in possible_types:
            raise RuntimeError("Type must be one of these values: all, log or expectation")

        try:
            self._send_request("/clear?type=" + type.lower(), data)
        except Exception as e:
            message="Clearing expectation with id " + id + " was unseccesfull!"
            raise Warning(message)

    def reset_all_requests(self):
        """Clears all expectations and received requests from the mockserver.
        """
        self._send_request("/reset")

    def dump_to_log(self):
        """Dumps logs at the mockserver.
        """
        # self._send_request("/dumpToLog")
        pass

    def _send_request(self, path, data=None):
        if isinstance(data, dict):
            data_dump = json.dumps(data)
        else:
            data_dump = data

        url = urljoin(self.base_url, path)

        logger.debug("url: {}, data: {}".format(url, data_dump))
        rsp = self.session.put(url, data=data_dump, timeout=5.0)

        if rsp.status_code >= 400:
            raise AssertionError("Mock server failed with {}: {}".format(rsp.status_code, rsp.text))

        return rsp
