#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 10:48:43 2021

GUI network scanner
based on https://stackoverflow.com/questions/207234/list-of-ip-addresses-hostnames-from-local-network-in-python

@author: lada
"""

import os
import socket    
import multiprocessing
import subprocess
from colorama import Fore, Back, Style
from math import ceil
import numpy as np
from datetime import datetime

rows = 24
ipAddr = "10.1.102.1" # if "" the current IP will be used as base

def pinger(job_q, results_q):
    """
    Do Ping
    :param job_q:
    :param results_q:
    :return:
    """
    DEVNULL = open(os.devnull, 'w')
    while True:

        ip = job_q.get()

        if ip is None:
            break

        try:
            subprocess.check_call(['ping', '-w4', ip],
                                  stdout=DEVNULL)
            results_q.put(int(ip.split(".")[3]))
        except:
            pass


def get_my_ip():
    """
    Find my IP address
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def map_network(base_ip, pool_size=255):
    """
    Maps the network
    :param pool_size: amount of parallel ping processes
    :return: list of valid ip addresses
    """
    ip_list = []
    
    # prepare the jobs queue
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    pool = [multiprocessing.Process(target=pinger, args=(jobs, results)) for i in range(pool_size)]

    for p in pool:
        p.start()

    # cue hte ping processes
    for i in range(1, 255):
        jobs.put(base_ip + '{0}'.format(i))

    for p in pool:
        jobs.put(None)

    for p in pool:
        p.join()

    # collect he results
    while not results.empty():
        ip = results.get()
        ip_list.append(ip)

    return ip_list

def clear():
    if(os.name == 'nt'):
        os.system('cls')
    else:
        os.system('clear')
        
first = True
history = -np.ones(255, dtype='int8')

def printTable(lst):
    global first
    for i in range(0,rows):
        line = ""
        for j in range(0,ceil(256/rows)):
            num = i*ceil(256/rows)+j+1
            if(num>255):
                break
            if(num in lst):
                col = Fore.WHITE
                if(first):
                    history[num-1] = 1
                if(history[num-1]<=0): # just appeared
                    history[num-1]=4
            else:
                col = Fore.BLACK
                if(first):
                    history[num-1] = 0
                if(history[num-1]>=1): # just disappeared
                    history[num-1]=-3
            historyStyle = [Style.DIM, Style.NORMAL, Style.BRIGHT]
            bg = ""
            if(history[num-1]>1): # green dimming background for appearing
                bg = historyStyle[history[num-1]-2]+Back.GREEN
                history[num-1]-=1
            if(history[num-1]<0): # red dimming background for disappearing
                bg = historyStyle[-history[num-1]-1]+Back.RED
                history[num-1]+=1
            line += col+bg+"{:3}".format(num)+Style.RESET_ALL+"\t"
        print(line)
    first = False


if __name__ == '__main__':
    print("Starting")
    # get my IP and compose a base like 192.168.1.xxx
    if(ipAddr != ""):
        ip_parts = ipAddr.split('.')
    else:
        ip_parts = get_my_ip().split('.')
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'
    while(True):
        lst = map_network(base_ip)
        clear()
        print(datetime.strftime(datetime.now(),"%H:%M:%S"))
        print(base_ip)
        printTable(lst)
