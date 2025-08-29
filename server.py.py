# server.py
import socket

# Server configuration
HOST = '127.0.0.1'  # localhost
PORT = 65432        # non-privileged port

# Create a socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}...")

    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f"Client says: {message}")

            # Server reply
            reply = f"Hello Client! You said: {message}"
            conn.sendall(reply.encode())
