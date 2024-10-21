import socket

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
    if "Sending file" in response or "Available files" in response:
        file_size = int(client.recv(HEADER).decode(FORMAT).strip())
        transmitteddata = b''
        while file_size > len(transmitteddata):
            transmitteddata += client.recv(1024)
        print(transmitteddata.decode(FORMAT))
    #If the server is full, close the client
    if "maximum number of connections" in response:
        print("Closing the connection")
        client.close()
        exit()


print("Successful server connection!")

# Main loop to send messages
while True:
    message = input("Enter message: ")
    # Check if the user wants to exit
    if message.lower() == "exit":
        send_message("exit")
        break
    else:
        send_message(message)

# Close the client connection
client.close()