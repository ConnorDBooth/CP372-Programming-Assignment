
 #

 # -------------------------------------

 # Client File

 #

 # -------------------------------------

 # Software Authors

 # Filip Droca, 169032146, droc2146@mylaurier.ca

 # Connor Booth, 169038238, boot8238@mylaurier.ca

 #

 # @version 2024-10-21

 #

 #------------------------------------- */

import socket

#Constants
HEADER = 64 # size of the packet to be sent
PORT = 5050 # the port the client will send and receive information through
FORMAT = 'utf-8' # the encoding format used to send and receive data between the client and server
SERVER = socket.gethostbyname(socket.gethostname())  # Assuming the server is running on the same machine. Replace with actual IP if needed.
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send_message(msg):
    message = msg.encode(FORMAT) #encode message
    message_length = len(message) #encode length
    send_length = str(message_length).encode(FORMAT) #encode the encoded length of message to be sent
    send_length += b' ' * (HEADER - len(send_length)) # append byte header to pad message to be sent
    client.send(send_length)
    client.send(message) #send length of message to prepare server and message itself
    # Receive and print the response from the server
    response = client.recv(1024).decode(FORMAT)
    print(f"Server: {response}")
    #in response to "list" or "get {filename}"
    if "Sending file" in response or "Available files" in response:
        file_size = int(client.recv(HEADER).decode(FORMAT).strip()) #decode expected length of data
        transmitteddata = b'' #no space as we aren't sending this data, just decoding it for the client
        while file_size > len(transmitteddata):
            transmitteddata += client.recv(1024) # receive data until expected length is reached
        print(transmitteddata.decode(FORMAT)) # print decoded version of received data
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