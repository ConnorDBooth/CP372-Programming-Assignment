import socket

#To do:
# Receiving of file contents from server.
#

#Constants
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())  # Assuming the server is running on the same machine. Replace with actual IP if needed.
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send_message(msg):
    message = msg.encode(FORMAT)
    message_length = len(message)
    send_length = str(message_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    # Receive and print the response from the server
    response = client.recv(1024).decode(FORMAT)
    print(f"Server: {response}")
    #If the server is full, close the client
    if "maximum number of connections" in response:
        print("Closing the connection")
        client.close()
        exit()


print("successful server connection.")

# Main loop to send messages
while True:
    message = input("Enter message: ")

    # Check if the user wants to exit
    if message.lower() == "exit":
        send_message("exit")
        break
    elif message.lower() == "list":
        send_message("list")
        #receive file list
        file_list = client.recv(1024).decode(FORMAT)
        if file_list == "No files available":
            print("No files available")
        else:
            print(file_list)
    elif message.lower().startswith("get"):
        #get file from server
        send_message(message)
        response = client.recv(1024).decode(FORMAT)
        
        if "Sending file" in response:
            filename = message[4:]
            with open(filename, "wb") as f:
                while True:
                    file_data = client.recv(1024)
                    if not file_data:
                        break
                f.write(file_data)
            print(f"File '{filename}' received successfully")
        else:
            print(response)
    else:
        send_message(message)

# Close the client connection
client.close()