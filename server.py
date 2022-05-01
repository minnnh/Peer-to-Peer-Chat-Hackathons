import sqlite3

import socketserver

class P2PServer(socketserver.BaseRequestHandler):
	def __init__(self, *args):
		self.clients = []
		self.create_database()
		self.fetch_clients_from_database()
		super(P2PServer, self).__init__(*args)

	def handle(self):
		try:
			self.update_current_client(self.client_address[0], self.client_address[1])
			for row in self.clients:
				self.request.sendall(bytes(row[0] + ',' + str(row[1]), 'utf-8'))
			
		except Exception as e:
			print(self.client_address, "Connection closed with exception ", e)
	
	def setup(self):
		print("Setup connection: ", self.client_address)
	
	def finish(self):
		print("Finish running, disconnect client", self.client_address)
		# self.remove_current_client(self.client_address[0], self.client_address[1])
		self.request.close()

	def create_database(self):
		conn = sqlite3.connect('server.db')
		cur = conn.cursor()
		cur.execute('CREATE TABLE IF NOT EXISTS client(ID INTEGER PRIMARY KEY AUTOINCREMENT, IP TEXT, Port INTEGER)')
		conn.commit()
		conn.close()

	def select_clients_from_database(self):
		conn = sqlite3.connect('server.db')
		cur = conn.cursor()
		cur.execute('SELECT IP, Port FROM client')
		rows = cur.fetchall()
		conn.close()
		return rows
	
	def fetch_clients_from_database(self):
		rows = self.select_clients_from_database()
		self.clients = []
		for row in rows:
			self.clients.append((row[0], row[1]))

	def update_current_client(self, client_address, client_port):
		found = False
		for client in self.clients:
			if client[0] == client_address and client[1] == client_port + 1:
				found = True
				break
		if not found:
			try:
				conn = sqlite3.connect('server.db')
				cur = conn.cursor()
				insert_cmd = 'INSERT INTO client (IP, Port) VALUES (\'' + client_address + '\', ' + str(client_port + 1) + ')'
				cur.execute(insert_cmd)
				conn.commit()
				conn.close()
				self.clients.append((client_address, client_port + 1))

			except Exception as e:
				print(e)

	def remove_current_client(self, client_address, client_port):
		found = False
		for client in self.clients:
			if client[0] == client_address and client[1] == client_port + 1:
				found = True
				break

		if found:
			conn = sqlite3.connect('server.db')
			cur = conn.cursor()
			cur.execute('DELETE FROM client WHERE IP = \'' + client_address + '\' AND Port = ' + str(client_port + 1))
			conn.commit()
			conn.close()
			self.fetch_clients_from_database()


# HOST, PORT = "127.0.0.1", 65432

# with socketserver.ThreadingTCPServer((HOST,PORT), P2PServer) as server:
# 	server.serve_forever()

# HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
# PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))
# s.listen()

# Users = {}

# # connect to the client
# def connect(conn, addr):
# 	Users[conn] = addr
# 	conn.send(("Welcome to the chat room.").encode())

# 	while True:
# 		data = conn.recv(1024)
# 		if data:
# 			message = f"({addr[0]}, {addr[1]}): " + data.decode()
# 			broadcast(message, conn)
# 			print(message)
# 			#print(f"{line}\nThe client {addr[0]} is sending the message:\"{data.decode()}\" to all the users that are available.\n")
# 			store(Users)
# 		else:
# 			#del Users[conn]
# 			remove(conn)
# 			#Users.remove(conn)
# # send the message to all the Users that are avaliable
# def broadcast(message, conn):
# 	for user in list(Users.keys()):
# 		if user != conn:
# 			try:
# 				user.send(message.encode())
# 			except:
# 				#user.close()
# 				del Users[user]

# # remove the user
# def remove(conn):
# 	if conn in list(Users.keys()):
# 		#Users.remove(conn)
# 		del Users[conn]

# def cre_table():
# 	if os.path.exists('data.db'):
# 		os.remove('data.db')
	
# 	connection = sqlite3.connect('data.db')
# 	cur = connection.cursor()
# 	cur.execute('CREATE TABLE Users(ClientNum INTEGER PRIMARY KEY AUTOINCREMENT, IP TEXT, Port INTEGER)')
# 	cur.execute('INSERT INTO Users VALUES ((SELECT MAX(ClientNum) + 1 FROM Users),"127.0.0.1", 1234)')
	
# 	connection.commit()
# 	connection.close()

# # store the users into database
# def store(Users):
# 	connection = sqlite3.connect('data.db')
# 	cur = connection.cursor()

# 	find = False
# 	print("\n---------------------------")
# 	for user in Users.values():
# 		for row in cur.execute(f'SELECT * FROM Users'):
# 			print(row)
# 			if(list(row[-2:]) == [str(user[0]), int(user[1])]):
# 				find = True
# 				break
# 			else:
# 				continue
# 		if(not find):
# 			cur.execute(f'INSERT INTO Users VALUES ((SELECT MAX(ClientNum) + 1 FROM Users),"{str(user[0])}", {int(user[1])})')
# 	print("---------------------------\n")
# 	connection.commit()
# 	connection.close()

# cre_table()
# while True:
# 	conn, addr = s.accept()
# 	# addr includes the ip address and the port of client
# 	#Users[conn] = addr
# 	print(f"Client ip:{addr[0]}, port:{addr[1]} is connected.\n")
# 	start_new_thread(connect,(conn, addr))

# conn.close()
# s.close()