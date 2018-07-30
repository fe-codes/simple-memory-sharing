# -*- coding: cp936 -*-
import socket
def get_image_tcp(key):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(('127.0.0.1',8000))
    s.send(key)
    data = ''
    buf = s.recv(10*1024*1024)
    while buf:
        data += buf
        buf = s.recv(10*1024*1024)
    s.close()
    return data# By default, if function fetch_data(key) is not implemented, the server will cache the key as the data.

print(get_image_tcp('hello world'))
print(get_image_tcp('hello world'))
print(get_image_tcp('hello world'))
