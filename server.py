import sqlite3
import socket
import os
from _thread import *

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

Users = {}

# connect to the client
def connect(conn, addr):
	Users[conn] = addr
	conn.send(("Welcome to the chat room.").encode())

	while True:
		data = conn.recv(1024)
		if data:
			message = f"({addr[0]}, {addr[1]}): " + data.decode()
			broadcast(message, conn)
			print(message)
			#print(f"{line}\nThe client {addr[0]} is sending the message:\"{data.decode()}\" to all the users that are available.\n")
			store(Users)
		else:
			#del Users[conn]
			remove(conn)
			#Users.remove(conn)
# send the message to all the Users that are avaliable
def broadcast(message, conn):
	for user in list(Users.keys()):
		if user != conn:
			try:
				user.send(message.encode())
			except:
				#user.close()
				del Users[user]

# remove the user
def remove(conn):
	if conn in list(Users.keys()):
		#Users.remove(conn)
		del Users[conn]

def cre_table():
	if os.path.exists('data.db'):
		os.remove('data.db')
	
	connection = sqlite3.connect('data.db')
	cur = connection.cursor()
	cur.execute('CREATE TABLE Users(ClientNum INTEGER PRIMARY KEY AUTOINCREMENT, IP TEXT, Port INTEGER)')
	cur.execute('INSERT INTO Users VALUES ((SELECT MAX(ClientNum) + 1 FROM Users),"127.0.0.1", 1234)')
	
	connection.commit()
	connection.close()

# store the users into database
def store(Users):
	connection = sqlite3.connect('data.db')
	cur = connection.cursor()

	find = False
	print("\n---------------------------")
	for user in Users.values():
		for row in cur.execute(f'SELECT * FROM Users'):
			print(row)
			if(list(row[-2:]) == [str(user[0]), int(user[1])]):
				find = True
				break
			else:
				continue
		if(not find):
			cur.execute(f'INSERT INTO Users VALUES ((SELECT MAX(ClientNum) + 1 FROM Users),"{str(user[0])}", {int(user[1])})')
	print("---------------------------\n")
	connection.commit()
	connection.close()

cre_table()
while True:
	conn, addr = s.accept()
	# addr includes the ip address and the port of client
	#Users[conn] = addr
	print(f"Client ip:{addr[0]}, port:{addr[1]} is connected.\n")
	start_new_thread(connect,(conn, addr))

conn.close()
s.close()

