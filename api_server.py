#!/usr/bin/env python
import zerorpc
from brubeckr import JsonrpcHandler, JsonrpcConnection, Brubeckr


###
### Configuration
###

# Routing config


handler_tuples = [
    ('@api', JsonrpcHandler),
]

# Application config
config = {
    'msg_conn': JsonrpcConnection('tcp://127.0.0.1:9997', 'tcp://127.0.0.1:9996'),
    'rpc_conn' : zerorpc.Client("tcp://127.0.0.1:4242", timeout=None, heartbeat=None),
    'handler_tuples': handler_tuples,
}


# Instantiate app instance
app = Brubeckr(**config)
app.run()