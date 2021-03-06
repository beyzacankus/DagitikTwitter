#!/usr/bin/env python

import socket
import threading
import queue
import time

class loggerThread(threading.Thread):
    def __init__(self, logQueue):
        threading.Thread.__init__(self)
        self.logQueue = logQueue

    def run(self):
        exitFlag = False
        file = open("log.txt", 'a+')
        file.write("-----------------------------------\n")
        file.write("Logger starting.\n")
        file.flush()
        while not exitFlag:

            if not self.logQueue.empty():
                msg = self.logQueue.get()
                if msg == "QUIT":
                    exitFlag = True
                    log = "Logger: QUIT received.\n"
                else:
                    log = str(time.ctime(time.time())) + " - " + str(msg) + "\n"
                file.write(log)
                file.flush()

        file.flush()
        file.write("Logger exiting.\n")
        file.close()
