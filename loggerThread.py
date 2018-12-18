#!/usr/bin/env python

import socket
import threading
import queue
import time

logQueue = queue.Queue()
senderQueue = queue.Queue()

class loggerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        exitFlag = False
        file = open("log.txt", 'a')
        file.write("Logger starting.\n")
        while not exitFlag:
            if not logQueue.empty():
                msg = logQueue.get()
                if msg == "QUIT":
                    exitFlag = True
                    log = "Logger: QUIT received.\n"
                else:
                    log = str(time.ctime(time.time())) + " - " + str(msg) + "\n"
                file.write(log)

        file.write("Logger exiting.")
        file.close()
