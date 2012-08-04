import socket
import simplejson as json
from base64 import b64decode
CONN = socket.socket()
CONN.connect(('127.0.0.1', 6767))

def remote_call(method_name, args):
    msg = '@api %s\0' % (
        json.dumps({'jsonrpc': '2.0', 'method': method_name, 'id':1}))
    CONN.send(msg)

if __name__ == "__main__":
    remote_call('get_all_users', [])
    reply = CONN.recv(1024)
    print json.loads(b64decode(reply))
    CONN.close()
