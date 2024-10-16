import socket
import threading


# TODO
# - Update Cache to include accepted clients, date and time of connection, date and time of disconnection
# - BONUS: If client message == "list", list all files in repository
#   client can then request files by name 


# Constants
HEADER = 64
MAX_CONNECTIONS = 3
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) # get ip address for device hosting server
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

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
    
    print(f"New Connection: {addr} connected")
    with connections_lock:
        connections += 1
    
    connected = True
    while connected:
        # Finds size of client message
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            # print client message
            print(f"Message from {client_name} {msg}")
            
            with cache_lock:
                cache[client_name] = msg
                
            if msg.lower() == "status": # If message == "status", print the contents of the cache
                response = "Cache contents:\n" + "\n".join(f"{k}: {v}" for k, v in cache.items())
            elif msg.lower() == "exit": # if message == "exit", close connection
                connected = False
            else: # Append "ACK" to client message and echo back to client
                response = f"Echo from server: {msg} ACK"
                conn.sendall(response.encode('utf-8'))
        else:
            connected = False
            
        conn.close()
        print(f"Connection with {client_name} has been closed")
        with connections_lock:
            connections -= 1

def start():
    server.listen()
    print(f"Sever is listening on {SERVER}:{PORT}")
    while True:
        conn, addr = server.accept() # when a new connection occurs, store object that allows for communication back to the connection and address
        print(f"Attempting to connect: {addr}")
        
        # Checks the number of clients connected to the server. If maximum has already been reached, client is not connected
        if connections >= MAX_CONNECTIONS:
            conn.sendall(f"The server has reached the maximum number of connections, Max number is {MAX_CONNECTIONS}")
            conn.close()
            continue
        
        #Format client name
        with client_id_lock:
            client_name = f"Client{client_id:02d}"
            client_id += 1
            
        thread = threading.Thread(target = handle_client, args=(conn,addr,client_name))
        thread.start()
        print(f"Number of Active Connections: {threading.activeCount() - 1}") # since a new thread is made for each connection, this will show the number of current connection



print("server is starting...")
start()