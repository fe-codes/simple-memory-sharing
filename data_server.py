# -*- coding: cp936 -*-
import SocketServer
import sys

# Below are packages that are optional
import os
from skimage import io
import psutil # Used to control memory usage
import threading# Used to control memory usage
import time# Used to control memory usage
import gc# Used to control memory usage

# This module provides a way to cache data in the memory for mutiple processes,
# it should be run independently from the processes that use the cached data.
# the data are cached in a dictionary, and accessed by the keys in it via tcp-ip protocol.
# The typical scenario for using this module is that,
# 1. mutiple processes need to load same data into the RAM, so it is not memory-efficient if they load a copy for them each
# 2. the loading(Heavy I/O) or pre-processing of data is time consuming and the program need to be started many times, i.e. tuning hyperparameters for a NN.
# 3. if the memory of one host is not enough and there are multiple hosts available, then it is convenient to load data on one host and use them on another.

MAX_KEY_SIZE = 4096 # the upper bound of the size of each key
data_dic = {} # the dictionary that cache the data
req_counter = {}# record the request count for each key, then release the least used items when memory is low
IP = "0.0.0.0" # ip address of the host, '0.0.0.0' binds to all addresses available
PORT = 8000 # port used to listen for request
MAX_MEMORY_PORTION = 0.85 # if the global memory used is above this ratio, then the cache is limited from growing
req = 0.0 # total request count
hit = 0.0 # hit count
TERMINATE = False # indicate the termination

def fetch_data(key): #To the simplest form, you only need to implement this function, it takes a key as input and returns the data associated with the key.
    return key

class data_server(SocketServer.BaseRequestHandler):# the request handler that listens the port specified, and handle the request
    def handle(self):
        global req
        global hit
        conn = self.request
        client_data = conn.recv(MAX_KEY_SIZE)#max key size 
        key = client_data#.decode('utf-8') # you can implement a commad response here
        req += 1
        if key not in req_counter:
            req_counter[key] = 1
        else:
            req_counter[key] += 1
        hit_this = 'Not'  
        if key in data_dic:
            hit += 1
            hit_this = 'Yes'
            conn.sendall(data_dic[key])
        else:
            data = fetch_data(key)
            conn.sendall(data)
            data_dic[key] = data
        conn.close()
        sys.stdout.write(str(key) + ' requested from:' + str(self.client_address) + ' Hit:'+ hit_this + ' Overall hit rate is:' + str( hit / req) +'\r\n')

def init():# in this function you can do some initialization, such as loading the data into the cache in prior
##    data_dic['example_key'] = io.imread(image_file_path).dumps()
    pass

class memory_deamon(threading.Thread):
    def run(self):# Thread.start() will call this automatically in a new thread
        while True:
            if TERMINATE:
                sys.stdout.write('Memory deamon exit...\r\n')
                return
            while psutil.virtual_memory().used > psutil.virtual_memory().total * MAX_MEMORY_PORTION:
                if TERMINATE:
                    sys.stdout.write('Memory deamon exit...\r\n')
                    return
                if len(data_dic) > 0:                    
                    lst_counter = sorted(zip(req_counter.values(),req_counter.keys()))#sorted list of (req_count,key) tuples
                    for i in range(len(lst_counter)):
                        if lst_counter[i][1] in data_dic:
                            key = lst_counter[i][1]
                            break                        
                    data_dic.pop(key)# alternatively you can use popitem() to randomly pop one item
                    sys.stdout.write('Item ' + str(key) + ' is popped\r\n')
                gc.collect()# even if no items are in the dictionary, gc can be triggered
                time.sleep(0.001)
            time.sleep(1)


try:
    md = memory_deamon()
    md.start()
    init()
    server = SocketServer.ThreadingTCPServer((IP, PORT),data_server) 
    server.allow_reuse_address = True
    sys.stdout.write('Server is ready...\r\n')
    server.serve_forever()
finally:
    TERMINATE = True
'''
For the client side, request data in the following form

def get_tcp_data(key):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(('127.0.0.1',51013))
    s.send(key)
    data = ''
    buf = s.recv(10*1024*1024)
    while buf:
        data += buf
        buf = s.recv(10*1024*1024)
    s.close()
    return np.loads(data)
'''

