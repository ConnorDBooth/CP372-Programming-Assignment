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
    client.send(message)
    # Receive and print the response from the server
    response = client.recv(1024).decode(FORMAT)
    print(f"Server: {response}")


print("successful server connection.")

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