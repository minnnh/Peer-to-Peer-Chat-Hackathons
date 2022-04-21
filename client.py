import socket
import select
import sys
from _thread import *
import threading

IP = "127.0.0.1"  # Standard loopback interface address (localhost)
Port = 65432  # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, Port))
s.sendto(b'Hello!', (IP,Port))

while True:
	data = s.recv(1024).decode()
	print(f"Server>> {data}")
	if(data == "Welcome to the chat room."):
		break

def listen():
	while True:
		rec = s.recv(1024)
		print(f"Server>> {rec.decode()}")

listenThr = threading.Thread(target=listen, daemon=True)
listenThr.start()

while True:
	msg = input("You >> ")
	if msg:
		s.sendto(msg.encode('utf-8'), (IP,Port))



