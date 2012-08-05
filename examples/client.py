#!/usr/bin/env python
import socket
import json
from base64 import b64decode
import sys

def remote_call(conn, method_name, params):
    msg = '@api %s\0' % (
        json.dumps({'jsonrpc': '2.0', 'method': method_name, 'params': params, 'id':1}))
    conn.send(msg)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: python client.py host port [method] [params]"
        exit(-1)

    host, port = sys.argv[1], int(sys.argv[2])
    conn = socket.socket()
    conn.connect((host, port))

    method = "_zerorpc_inspect" if len(sys.argv) == 3 else sys.argv[3]
    params = sys.argv[4:]
    remote_call(conn, method, params)

    resdata = conn.recv(2048)
    print json.dumps(json.loads(b64decode(resdata)), sort_keys = True, indent = 2)

    conn.close()
