import socket
import threading
from datetime import datetime
import os 


# TODO
#
# - BONUS: If client message == "list", list all files in repository
#   client can then request files by name 


# Constants
HEADER = 64
MAX_CONNECTIONS = 3
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) # get ip address for device hosting server
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FILE_DIR = "/Users/connorbooth/Documents/GitHub/CP372-Programming-Assignment" #directory to serve files from

#Ensure directory exists
if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)
# Number of connections counter
connections = 0
connections_lock = threading.Lock()
client_id = 1
client_id_lock = threading.Lock() #.Lock() avoids race conditions by ensuring that only one thread can modify a shared resource

# Create cache
cache = {}
cache_lock = threading.Lock()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creates socket and set family of address (Ipv4) we are looking for and the type (TCP)
server.bind(ADDR) # bind socket to address

def handle_client(conn, addr, client_name):
    global connections
    
    connection_time = datetime.now()
    
    print(f"New Connection: {addr} connected")
    
    with connections_lock:
        connections += 1
    
    with cache_lock:
        cache[client_name] = {
            'address': addr,
            'connection_time': connection_time,
            'disconnection_time': None
        }
    connected = True
    while connected:
        # Finds size of client message
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            # print client message
            print(f"Message from {client_name} : {msg}")
            
                
                
            if msg.lower() == "status": # If message == "status", print the contents of the cache
                response = "Cache contents:\n" + "\n".join(f"{k}: {v['address']} connected at {v['connection_time']}: Disconnected at {v['disconnection_time'] or 'Still Connected'}" for k, v in cache.items())
                conn.sendall(response.encode(FORMAT))
                
            elif msg.lower() == "list":
                files = os.listdir(FILE_DIR)
                response = "Available files:\n" + "\n".join(files) if files else "No files available"
                conn.sendall(response.encode(FORMAT))
                
            elif msg.lower().startswith("get "):
                filename = msg[4:] #skip "get"
                file_path = os.path.join(FILE_DIR, filename)
                
                if os.path.isfile(file_path):
                    #If file can be found, send to client
                    conn.sendall(f"Sending file: {filename}".encode(FORMAT))
                    with open(file_path, "rb") as f:
                        while True:
                                file_data = f.read(1024)
                                if not file_data:
                                    break
                                conn.sendall(file_data)
                    print(f"File '{filename}' sent to {client_name}.")
                else:
                    conn.sendall(f"Error: file '{filename}' not found".encode(FORMAT))
                    
            elif msg.lower() == "exit": # if message == "exit", close connection
                connected = False
                
            else: # Append "ACK" to client message and echo back to client
                response = f"Echo from server: {msg} ACK"
                conn.sendall(response.encode(FORMAT))
        else:
            connected = False
    
    disconnection_time = datetime.now()
    with cache_lock:
        cache[client_name]['disconnection_time'] = disconnection_time
    
    response = ("Echo from server: exit ACK")
    conn.sendall(response.encode(FORMAT))
    
    conn.close()
    print(f"Connection with {client_name} has been closed")
    with connections_lock:
        connections -= 1

def start():
    global client_id 
    
    server.listen()
    print(f"Server is listening on {SERVER}:{PORT}")
    
    while True:
        conn, addr = server.accept() # when a new connection occurs, store object that allows for communication back to the connection and address
        print(f"Attempting to connect: {addr}")
        
        # Checks the number of clients connected to the server. If maximum has already been reached, client is not connected
        with connections_lock:
            if connections >= MAX_CONNECTIONS:
                response = (f"The server has reached the maximum number of connections, Max number is {MAX_CONNECTIONS}")
                conn.sendall(response.encode(FORMAT))
                conn.close()
                continue
        
        #Format client name
        with client_id_lock:
            client_name = f"Client{client_id:02d}"
            client_id += 1
            
        thread = threading.Thread(target = handle_client, args=(conn,addr,client_name))
        thread.start()
        print(f"Number of Active Connections: {threading.active_count() - 1}") # since a new thread is made for each connection, this will show the number of current connection



print("server is starting...")
start()