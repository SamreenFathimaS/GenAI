# client.py
import socket

# Server configuration
HOST = '127.0.0.1'
PORT = 65432

# Create a socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Hello message to server
    message = "Hello Server! This is Client."
    s.sendall(message.encode())

    # Receive server reply
    data = s.recv(1024)
    print(f"Server replies: {data.decode()}")
