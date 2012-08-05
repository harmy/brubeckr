import ujson as json
import logging
from brubeck.request import Request
from brubeck.connections import Mongrel2Connection
from brubeck.request_handling import MessageHandler, Brubeck

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
errors = {}
errors[PARSE_ERROR] = "Parse Error"
errors[INVALID_REQUEST] = "Invalid Request"
errors[METHOD_NOT_FOUND] = "Method Not Found"
errors[INVALID_PARAMS] = "Invalid Params"
errors[INTERNAL_ERROR] = "Internal Error"

class JsonRpcException(Exception):
    """
    >>> exc = JsonRpcException(1, INVALID_REQUEST)
    >>> str(exc)
    '{"jsonrpc": "2.0", "id": 1, "error": {"message": "Invalid Request", "code": -32600}}'

    """

    def __init__(self, rpc_id, code, data=None):
        self.rpc_id = rpc_id
        self.code = code
        self.data = data

    @property
    def message(self):
        return errors[self.code]

    def as_dict(self):
        if self.data:
            return {'jsonrpc': '2.0',
                    'id': self.rpc_id,
                    'error': {'code': self.code,
                              'message': self.message,
                              'data': self.data}}
        else:
            return {'jsonrpc': '2.0',
                    'id': self.rpc_id,
                    'error': {'code': self.code,
                              'message': self.message}}

    def __str__(self):
        return json.dumps(self.as_dict())


class JsonRpc(object):
    """
    """

    def __init__(self, methods=None, exception_cb=None):
        self.exception_cb = exception_cb
        if methods is not None:
            self.methods = methods
        else:
            self.methods = {}

    def process(self, data, extra_vars):
        if data.get('jsonrpc') != "2.0":
            raise JsonRpcException(data.get('id'), INVALID_REQUEST)

        if 'method' not in data:
            raise JsonRpcException(data.get('id'), INVALID_REQUEST)

        methodname = data['method']
        if not isinstance(methodname, basestring):
            raise JsonRpcException(data.get('id'), INVALID_REQUEST)

        if methodname not in self.methods:
            raise JsonRpcException(data.get('id'), METHOD_NOT_FOUND)

        method = self.methods[methodname]

        try:
            params = data.get('params', [])
            if isinstance(params, list):
                result = method(*params, **extra_vars)
            else:
                raise JsonRpcException(data.get('id'), INVALID_PARAMS)
            resdata = None
            if data.get('id'):
                resdata = {
                    'jsonrpc': '2.0',
                    'id': data.get('id'),
                    'result': result,
                    }
            return resdata
        except JsonRpcException, e:
            raise e
        except Exception, e:
            if self.exception_cb:
                self.exception_cb(e)
            raise JsonRpcException(data.get('id'), INTERNAL_ERROR, data=str(e))

    def _call(self, data, extra_vars):
        try:
            return self.process(data, extra_vars)
        except JsonRpcException, e:
            return e.as_dict()

    def __call__(self, data, **extra_vars):
        if isinstance(data, dict):
            resdata = self._call(data, extra_vars)
        elif isinstance(data, list):
            if len([x for x in data if not isinstance(x, dict)]):
                resdata = {'jsonrpc': '2.0',
                           'id': None,
                           'error': {'code': INVALID_REQUEST,
                                     'message': errors[INVALID_REQUEST]}}
            else:
                resdata = [d for d in (self._call(d, extra_vars) for d in data) if d is not None]

        return resdata

    def __getitem__(self, key):
        return self.methods[key]

    def __setitem__(self, key, value):
        self.methods[key] = value

    def __delitem__(self, key):
        del self.methods[key]


class JsonrpcHandler(MessageHandler):
    """
    """

    def initialize(self):
        client = self.application.rpc_conn
        remote_methods = client._zerorpc_inspect()["methods"]
        methods = dict(zip(remote_methods.keys(), [getattr(client, method_name) for method_name in remote_methods.keys()]))
        methods.update({"_zerorpc_inspect": getattr(client, "_zerorpc_inspect")})
        self.rpc = JsonRpc(methods)

    def __call__(self):
        try:
            data = self.message.data
            result = self.rpc(data)
        except ValueError, e:
            result = {'jsonrpc':'2.0',
                       'id':None,
                       'error':{'code':PARSE_ERROR,
                                'message':errors[PARSE_ERROR]}}
        return result

class JsonrpcConnection(Mongrel2Connection):
    """
    """

    def process_message(self, application, message):
        request = Request.parse_msg(message)
        if request.is_disconnect():
            return
        handler = application.route_message(request)
        response = handler()

        application.msg_conn.reply(request, json.dumps(response))


class Brubeckr(Brubeck):
    def __init__(self, msg_conn=None, handler_tuples=None, pool=None, no_handler=None, base_handler=None,
                 template_loader=None, log_level=logging.INFO, login_url=None, db_conn=None, cookie_secret=None,
                 api_base_url=None, *args, **kwargs):
        self.rpc_conn = kwargs.get("rpc_conn")
        super(Brubeckr, self).__init__(msg_conn, handler_tuples, pool, no_handler, base_handler, template_loader,
            log_level, login_url, db_conn, cookie_secret, api_base_url, *args, **kwargs)
