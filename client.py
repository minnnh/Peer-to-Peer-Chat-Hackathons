import socket
import sqlite3
import threading

class Client:
	def __init__(self):
		self.IP = "127.0.0.1"
		self.PORT = 60410
		self.server_IP = "127.0.0.1"
		self.server_port = 65432
		self.create_table()
		self.create_socket()
		self.create_client_socket()

	def __init__(self, IP, port, server_IP, server_port):
		self.IP = IP
		self.PORT = port
		self.PORT_CLIENT_REV = port + 1
		self.PORT_CLIENT_SEND = port + 2
		self.server_IP = server_IP
		self.server_port = server_port
		self.create_table()
		self.create_socket()
		self.create_client_socket()

	# Create unique table for the client
	def create_table(self):
		conn = sqlite3.connect('client.db')
		self.tb_name = 'client_' + self.IP + '_' + str(self.PORT)
		self.tb_name = self.tb_name.replace('.', '_')
		try:
			create_tb_cmd = 'CREATE TABLE IF NOT EXISTS ' + self.tb_name + ' (CLIENT_ID INTEGER PRIMARY KEY AUTOINCREMENT, IP TEXT, Port INTEGER)'
			conn.execute(create_tb_cmd)
			conn.close()
			return True
		except:
			conn.close()
			return False
	
	# Socket connecting to Server
	def create_socket(self):
		self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.tcp_socket.bind((self.IP, self.PORT))

	# Socket connecting to another client
	def create_client_socket(self):
		self.client_socket_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket_recv.bind((self.IP, self.PORT_CLIENT_REV))
		self.client_socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket_send.bind((self.IP, self.PORT_CLIENT_SEND))
	
	# Close all the sockets in client
	def close_all_socket(self):
		try:
			self.tcp_socket.close()
			self.client_socket_recv.close()
			self.client_socket_send.close()
		except Exception as e:
			print('Close client socket connection error, ', e)

	# Start the listening to one other client
	def client_listen_to_client(self):
		self.listenThr = threading.Thread(target=self.listen, daemon=True)
		self.listenThr.start()

	# Update client list from the server
	def update_clients_from_server(self):
		self.create_socket()
		self.tcp_socket.connect((self.server_IP, self.server_port))
		print('-----------------------------------------')
		print('Connect to Server to fetch client lists. ')

		try:
			rows = []
			# Receive clients data from server
			data = self.tcp_socket.recv(1024).decode()
			while data:
				rows.append(data)
				data = self.tcp_socket.recv(1024).decode()

			# Connect to database and insert data
			conn = sqlite3.connect('client.db')
			conn.execute('DELETE FROM ' + self.tb_name)
			cur = conn.cursor()
			for row in rows:
				client_data = row.split(',')
				insert_tb_cmd = 'INSERT INTO ' + self.tb_name + ' (IP, Port) VALUES (\'' + client_data[0] + '\', ' + client_data[1] + ')'
				cur.execute(insert_tb_cmd)
			conn.commit()
			conn.close()
			print('Finish updating client lists.')
		except:
			print('Error. Close connection to Server. ')
			print('-----------------------------------------')
		finally:
			self.tcp_socket.close()

	# Select all the clients from the database of client
	def select_clients_from_database(self):
		conn = sqlite3.connect('client.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM ' + self.tb_name)
		rows = cur.fetchall()
		conn.close()
		return rows

	# Listening to other client and receive messages
	# Input 'exit' to end listening
	# Receive '#' to end receiving messages from one other client
	def listen(self):
		self.client_socket_recv.listen(5)
		while True:
			if_exit = input('Input anything to continue, or \'exit\' if want to exit >> ')
			if if_exit and if_exit == 'exit':
				break
			print(self.client_socket_recv.getsockname(), 'is listening... ')

			conn, addr = self.client_socket_recv.accept()
			print('Receive connection from ', addr)
			while True:
				rec = conn.recv(1024)
				if rec and rec.decode() != '#':
					print('(' + self.IP + ', ' + str(self.PORT_CLIENT_REV) + ') Receive >>', rec.decode())
				elif rec and rec.decode() == '#':
					print('(' + self.IP + ', ' + str(self.PORT_CLIENT_REV) + ') Message from ' + str(addr) + ' ends. ')
					break
			conn.close()
	
	# Send message to another client
	# Send message of '#' to end the input
	def connect_and_send(self, IP, Port):
		self.client_socket_send.connect((IP, Port))
		while True:
			msg = input('(' + self.IP + ', ' + str(self.PORT_CLIENT_SEND) + ') Send >> ')
			if msg and msg != '#':
				self.client_socket_send.send(msg.encode('utf-8'))
			elif msg and msg == '#':
				self.client_socket_send.send(msg.encode('utf-8'))
				break

	# Connect to the first client that is not itself in the client list in database
	def connect_to_first_client(self):
		clients = self.select_clients_from_database()
		found = False
		for client in clients:
			if client[1] != self.IP or client[2] != self.PORT_CLIENT_REV:
				client_2_IP = client[1]
				client_2_PORT = client[2]
				found = True
				break
		
		if found:
			try:
				print('Connecting to (' + client_2_IP + ', ' + str(client_2_PORT) + ')')
				self.connect_and_send(client_2_IP, client_2_PORT)
			except Exception as e:
				print('Client (' + self.IP + ', ' + str(self.PORT) + ') existed with error ', e)
		else:
			print('No other clients. ')



# IP = "127.0.0.1"  # Standard loopback interface address (localhost)
# Port = 65432  # Port to listen on (non-privileged ports are > 1023)

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((IP, Port))
# s.sendto(b'Hello!', (IP,Port))

# connection = sqlite3.connect('data.db')
# cur = connection.cursor()
# for row in cur.execute(f'SELECT * FROM Users'):
# 	print("======\n",row)

# while True:
# 	data = s.recv(1024).decode()
# 	if(data == "Welcome to the chat room."):
# 		print(f"Server >> {data}")
# 		break

# def listen():
# 	while True:
# 		rec = s.recv(1024)
# 		if rec:
# 			print("\n", rec.decode())

# while True:
# 	msg = input("You >> ")
# 	if msg:
# 		s.sendto(msg.encode('utf-8'), (IP,Port))
# 	try:
# 		listenThr = threading.Thread(target=listen, daemon=True)
# 		listenThr.start()
# 	except:
# 		print("pending.......")