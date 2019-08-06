#!/usr/bin/python3.6
import cgi, cgitb

header = "Content-type:text/plain \r\n\r\n"
print(str(header))

request = cgi.FieldStorage()
print("getting method val")
method = request.getvalue("method")

if method == "say_hello":
    body = "Hello, world."
elif method == "json":
    body = "{'stub':'no actual data'}"

print(str(body))
