import socket
import threading
from datetime import datetime
import os

# Constants
HEADER = 64 # size of the packet to be sent
MAX_CONNECTIONS = 3
PORT = 5050 # the port the server will send and receive information through
SERVER = socket.gethostbyname(socket.gethostname()) # get ip address for device hosting server
ADDR = (SERVER, PORT)
FORMAT = 'utf-8' # the encoding format used to send and receive data between the client and server
FILE_DIR = os.path.dirname(os.path.abspath(__file__)) #directory to serve files from, default is where server file is located

#Ensure directory exists
if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR) #if it doesn't exist, create an empty one
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
    
    connection_time = datetime.now() #get time of connection
    
    print(f"New Connection: {addr} connected")
    
    with connections_lock:
        connections += 1
    
    with cache_lock: # add address, time of connection and time of disconnect to cache.
        cache[client_name] = {
            'address': addr,
            'connection_time': connection_time,
            'disconnection_time': None
        }
    connected = True
    while connected: #while user is connected.
        # Finds size of client message
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT) #receive the message from the expected length of the message
            # print client message
            print(f"Message from {client_name} : {msg}")
            
                
                
            if msg.lower() == "status": # If message == "status", print the contents of the cache
                response = "Cache contents:\n" + "\n".join(f"{k}: {v['address']} connected at {v['connection_time']}: Disconnected at {v['disconnection_time'] or 'Still Connected'}" for k, v in cache.items())
                conn.sendall(response.encode(FORMAT))
                
            elif msg.lower() == "list": # if message == "list", list server repository
                files = os.listdir(FILE_DIR) #store directory listing
                response = "Available files:"
                additionalresponse = "\n".join(files) if files else "No files available" #store all files as newline delimited string
                conn.sendall(response.encode(FORMAT)) # send response first to have client prepare for directory data
                # send byte length and pad rest of packet to avoid errors
                conn.sendall(str(len(additionalresponse)).encode(FORMAT)+ b' ' * (HEADER - len(str(len(additionalresponse))))) # send length of data to be sent to client
                conn.sendall(additionalresponse.encode(FORMAT)) # send encoded data to client
                
            elif msg.lower().startswith("get "): #if the client calls "get", fetch the appropriate file if it exists
                filename = msg[4:] #skip "get"
                file_path = os.path.join(FILE_DIR, filename) #get appropriate file path if possible
                
                if os.path.isfile(file_path):
                    #If file can be found, send to client
                    conn.sendall(f"Sending file: {filename}".encode(FORMAT))
                    # send expected number of bytes to client to have them receive whole transmission in one request.
                    conn.sendall(str(os.path.getsize(file_path)).encode(FORMAT) + b'' * (HEADER - len(str(os.path.getsize(file_path)))))
                    #open file in byte-read mode, and continue until no more file data can be read
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
    
    response = ("Echo from server: exit ACK") #since loop is escaped, simulate its normal output
    conn.sendall(response.encode(FORMAT))
    
    conn.close()
    print(f"Connection with {client_name} has been closed")
    with connections_lock:
        connections -= 1 #decrement connections to take new clients

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