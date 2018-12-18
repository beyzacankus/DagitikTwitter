#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 13:56:29 2018

@author: alyxvance
"""
import queue
import threading
import socket
import time
import uuid

class loggerThread (threading.Thread):
    def __init__(self, name, logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.logQueue = logQueue

    def run(self):
        print(self.name + " starting.")
        while True:
            msg = self.logQueue.get()
            if msg == "QUIT":
                print(self.name + ": QUIT received.")
                break
            print(str(time.ctime()) + " - " + str(msg))
        print(self.name + " exiting." )
    
    
class serverThread(threading.Thread):
    def __init__(self, name, socket, threadQ, logQueue, uuid):
        threading.Thread.__init__(self)
        self.name = name
        self.logQueue = logQueue
        self.uuid = uuid
        
    def run(self):
        self.logQueue.put(self.name + ": starting")
    
class clientThread(threading.Thread):
    def __init__(self, name, socket, threadQ, logQueue, uuid):
        threading.Thread.__init__(self)
        self.name = name
        self.logQueue = logQueue
        self.uuid = uuid
        
    def run(self):
        self.logQueue.put(self.name + ": starting")
    
    
def main():
    
    # create and run logger thread
    lQueue = queue.Queue()
    lThread = loggerThread("Logger", lQueue)
    lThread.start()
    
    # getting uuid of the computer
    peerUUID = uuid.uuid1();
    
    # start listening
    s = socket.socket()
    host = "0.0.0.0"
    port = 12345
    s.bind((host,port))
    s.listen(5)
    
    # give unique name to all of the threads
    sCounter = 0
    cCounter = 0
    
    while True:
        threadQueue = queue.Queue()
        
        # close the port gracefully
        try:
            c, addr = s.accept()
        except KeyboardInterrupt:
            s.close()
            lQueue.put('QUIT')
            break

        lQueue.put('Got new connection from' + str(addr))
    
        # create and run server thread
        sThread = serverThread('serverThread-' + str(sCounter), c, threadQueue, lQueue, peerUUID)
        sThread.start()
        sCounter += 1

        # create and run client thread
        cThread = clientThread('clientThread-' + str(sCounter), c, threadQueue, lQueue, peerUUID)
        cThread.start()
        cCounter += 1
    

    
if __name__ == '__main__':
    main() 
    
    
    
    
