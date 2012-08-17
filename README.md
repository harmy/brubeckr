## brubeckr

a jsonrpc2 handler for [brubeck][0], a socket [ZeroRPC][1] gateway, play as the bridge between [brubeck][0] and [zerorpc][1]. 

## Example

there is a working server on my aws ec2, so feel free to check it out.
    
```python
def hello(self, who = "world!"):
        return "hello %s!" % who
```
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

[0]: http://brubeck.io
[1]: https://github.com/dotcloud/zerorpc-python
