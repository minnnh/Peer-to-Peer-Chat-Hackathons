import socket
import select
import sys
import sqlite3
from _thread import *
import threading

IP = "127.0.0.1"  # Standard loopback interface address (localhost)
Port = 65432  # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, Port))
s.sendto(b'Hello!', (IP,Port))

connection = sqlite3.connect('data.db')
cur = connection.cursor()
for row in cur.execute(f'SELECT * FROM Users'):
	print("======\n",row)

while True:
	data = s.recv(1024).decode()
	if(data == "Welcome to the chat room."):
		print(f"Server >> {data}")
		break

def listen():
	while True:
		rec = s.recv(1024)
		if rec:
			print("\n", rec.decode())

while True:
	msg = input("You >> ")
	if msg:
		s.sendto(msg.encode('utf-8'), (IP,Port))
	try:
		listenThr = threading.Thread(target=listen, daemon=True)
		listenThr.start()
	except:
		print("pending.......")



