#!/usr/bin/python3.6
import cgi, cgitb

header = "Content-type:text/plain \r\n\r\n"

try:
    request = cgi.FieldStorage()
    method = request.getvalue("method")

    if method == "say_hello":
        body = "Hello, world."
    elif method == "json":
        body = "{'stub':'no actual data'}"

    print(str(header))
    print(str(body))
except Exception as err:
    print(f"Error in realtime script!")
    err_file = open("./python_errors.log", "a")
    err_file.write(f"{str(err)}\n")
