# brubeckr


a jsonrpc2 handler for brubeck, a socket/ZeroRPC gateway, play as the bridge between brubeck and zerorpc.

there is a working server on my aws ec2, so feel free to check it out.

<pre>
(brubeck)vagrant@precise64:/vagrant/brubeckr/examples$ ./client.py build.cokecode.com 6767 hello
{
  "id": 1, 
  "jsonrpc": "2.0", 
  "result": "hello world!!"
}
(brubeck)vagrant@precise64:/vagrant/brubeckr/examples$ ./client.py build.cokecode.com 6767 hello harmy
{
  "id": 1, 
  "jsonrpc": "2.0", 
  "result": "hello harmy!"
}
</pre>
