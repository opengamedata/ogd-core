#!/usr/bin/python
import cgi, cgitb

header = "Content-type:text/plain \r\n\r\n"

request = cgi.FieldStorage()
method = request.getvalue("method")

if method == "say_hello":
    body = "Hello, world."
elif method == "json":
    body = "{'stub':'no actual data'}"

print(str(header))
print(str(body))
