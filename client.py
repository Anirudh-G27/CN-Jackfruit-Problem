import socket
import ssl
import threading
import os
import base64

HOST = "127.0.0.1"
PORT = 5000

context = ssl._create_unverified_context()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

conn = context.wrap_socket(sock, server_hostname="localhost")

username = input("Enter username: ")
conn.send((username + "\n").encode())


def receive():
    receiving_file = False
    file_buffer = []
    
    while True:
        try:
            msg = conn.recv(4096).decode()
            if not msg:
                print("Server disconnected")
                break
            
            # Handle file transfer notifications
            if msg.startswith("[FILE]"):
                print(f"\n{msg.strip()}")
                print("Type ACCEPT <username> or REJECT <username> to respond")
            
            # Handle file transfer start
            elif msg.startswith("[FILESTART]"):
                print(f"\n{msg.strip()}")
                receiving_file = True
                file_buffer = []
            
            # Handle file chunks
            elif msg.startswith("[FILECHUNK]") and receiving_file:
                chunk_data = msg.replace("[FILECHUNK] ", "").strip()
                file_buffer.append(chunk_data)
            
            # Handle file transfer end
            elif msg.startswith("[FILEEND]") and receiving_file:
                print(f"\n{msg.strip()}")
                receiving_file = False
                file_buffer = []
            
            # Regular messages
            else:
                print(msg)
                
        except:
            print("Connection closed")
            break


threading.Thread(target=receive, daemon=True).start()

print("\nCommands:")
print("JOIN room1")
print("use command MSG to message something")
print("PM username message")
print("SEND username filename")
print("ACCEPT username")
print("REJECT username")
print("EXIT\n")

while True:
    msg = input()
    
    # Check if file exists for SEND command
    parts = msg.split()
    if parts and parts[0].upper() == "SEND" and len(parts) >= 3:
        filename = parts[2]
        if not os.path.exists(filename):
            print(f"File '{filename}' not found")
            continue
    
    try:
        conn.send((msg + "\n").encode())
        if msg.upper() == "EXIT":
            break
    except:
        break

conn.close()