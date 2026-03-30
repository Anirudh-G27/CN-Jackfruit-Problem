import socket
import ssl
import threading
import re
import os
import base64

HOST = "127.0.0.1"
PORT = 5000

clients = {}        # conn -> username
rooms = {}          # room -> set of connections
client_room = {}    # conn -> room

lock = threading.Lock()

# File transfer variables
pending_transfers = {}  # (sender_conn, receiver_conn) -> filename
BUFFER_SIZE = 8192


def broadcast(room, message, sender=None):
    """Send message to all clients in a room"""
    if room in rooms:
        for client in list(rooms[room]):
            if client != sender:
                try:
                    client.send((message + "\n").encode())
                except:
                    pass


def send_private(target_user, message, sender_conn):
    """Send private message to specific user"""
    target_user = target_user.lower().replace(" ", "")
    found = False

    for conn, user in clients.items():
        if user == target_user:
            try:
                conn.send((message + "\n").encode())
                found = True
            except:
                pass
            break

    if not found:
        sender_conn.send(f"User '{target_user}' not found\n".encode())


def send_private_to_conn(target_conn, message):
    """Send private message directly to a connection"""
    try:
        target_conn.send((message + "\n").encode())
        return True
    except:
        return False


def handle_file_transfer(sender_conn, target_user, filename):
    """Handle file transfer request - PRIVATE only"""
    target_user = target_user.lower().replace(" ", "")
    sender_name = clients[sender_conn]
    
    # Check if file exists
    if not os.path.exists(filename):
        sender_conn.send(f"File '{filename}' not found\n".encode())
        return
    
    # Check file size (limit to 10MB)
    file_size = os.path.getsize(filename)
    if file_size > 10 * 1024 * 1024:
        sender_conn.send(f"File too large (max 10MB)\n".encode())
        return
    
    # Find target connection
    target_conn = None
    for conn, user in clients.items():
        if user == target_user:
            target_conn = conn
            break
    
    if not target_conn:
        sender_conn.send(f"User '{target_user}' not found\n".encode())
        return
    
    # Send file transfer notification - PRIVATE to target only
    try:
        # Send to target user only (NOT broadcast)
        target_conn.send(f"[FILE] {sender_name} wants to send '{filename}' ({file_size} bytes). Type 'ACCEPT {sender_name}' or 'REJECT {sender_name}'\n".encode())
        
        # Send confirmation to sender
        sender_conn.send(f"File transfer request sent to {target_user}. Waiting for response...\n".encode())
        
        # Store pending transfer
        global pending_transfers
        pending_transfers[(sender_conn, target_conn)] = filename
        
        print(f"[FILE TRANSFER] {sender_name} -> {target_user}: {filename} (PRIVATE)")
        
    except Exception as e:
        sender_conn.send(f"Failed to send file request\n".encode())


def send_file(sender_conn, receiver_conn, filename):
    """Send file - PRIVATE between sender and receiver only"""
    try:
        sender_name = clients[sender_conn]
        receiver_name = clients[receiver_conn]
        
        file_size = os.path.getsize(filename)
        file_name = os.path.basename(filename)
        
        # Send file metadata - PRIVATE to receiver only
        receiver_conn.send(f"[FILESTART] {sender_name} is sending '{file_name}' ({file_size} bytes)\n".encode())
        
        # Send file in chunks - PRIVATE to receiver only
        with open(filename, 'rb') as f:
            sent_bytes = 0
            while sent_bytes < file_size:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                encoded_chunk = base64.b64encode(chunk).decode()
                receiver_conn.send(f"[FILECHUNK] {encoded_chunk}\n".encode())
                sent_bytes += len(chunk)
                threading.Event().wait(0.01)
        
        # Send completion messages - PRIVATE
        receiver_conn.send(f"[FILEEND] File '{file_name}' sent successfully\n".encode())
        sender_conn.send(f"File '{file_name}' sent successfully to {receiver_name}\n".encode())
        
        print(f"[FILE TRANSFER COMPLETE] {sender_name} -> {receiver_name}: {filename} (PRIVATE)")
        
    except Exception as e:
        sender_conn.send(f"File transfer failed\n".encode())
        receiver_conn.send(f"File transfer failed\n".encode())


def handle_client(conn, addr):
    print(f"New connection attempt from: {addr}")

    try:
        username = conn.recv(1024).decode().strip()
    except:
        conn.close()
        return

    # CLEAN USERNAME
    username = username.lower().replace(" ", "")

    with lock:
        if username in clients.values():
            conn.send("Username already taken. Try another.\n".encode())
            conn.close()
            return

        clients[conn] = username

    # ADD THIS LINE HERE:
    print(f"User '{username}' has successfully connected from {addr}")

    conn.send("Welcome! Use JOIN <room>\n".encode())
    conn.send("Commands: JOIN, MSG, PM, SEND, ACCEPT, REJECT, EXIT\n".encode())

    exited_normally = False

    while True:
        try:
            msg = conn.recv(1024).decode().strip()

            if not msg:
                break

            parts = msg.split()
            command = parts[0].upper()

            # JOIN
            if command == "JOIN":
                if len(parts) < 2:
                    conn.send("Usage: JOIN <room>\n".encode())
                    continue

                raw_room = "".join(parts[1:]).lower()

                # VALIDATION
                if not re.fullmatch(r"room\d+", raw_room):
                    conn.send("Invalid room name. Use format: room<number>\n".encode())
                    continue

                room = raw_room

                with lock:
                    old_room = client_room.get(conn)

                    if old_room and conn in rooms.get(old_room, set()):
                        rooms[old_room].remove(conn)
                        broadcast(old_room, f"{username} left the room")

                    client_room[conn] = room

                    if room not in rooms:
                        rooms[room] = set()

                    rooms[room].add(conn)

                conn.send(f"You joined {room}\n".encode())
                broadcast(room, f"{username} joined the room", conn)

            # MESSAGE
            elif command == "MSG":
                if len(msg.split(" ", 1)) < 2:
                    conn.send("Usage: MSG <message>\n".encode())
                    continue

                room = client_room.get(conn)

                if not room:
                    conn.send("Join a room first!\n".encode())
                    continue

                message = msg.split(" ", 1)[1]
                broadcast(room, f"{username}: {message}", conn)

            # PRIVATE MESSAGE
            elif command == "PM":
                parts = msg.split(" ", 2)

                if len(parts) < 3:
                    conn.send("Usage: PM <user> <message>\n".encode())
                    continue

                raw_target = parts[1]
                message = parts[2]

                target = raw_target.lower().replace(" ", "")

                send_private(target, f"[PM]{username}: {message}", conn)

            # SEND FILE - PRIVATE
            elif command == "SEND":
                parts = msg.split(" ", 2)
                
                if len(parts) < 3:
                    conn.send("Usage: SEND <user> <filename>\n".encode())
                    continue
                
                target_user = parts[1]
                filename = parts[2]
                
                handle_file_transfer(conn, target_user, filename)

            # ACCEPT FILE - PRIVATE
            elif command == "ACCEPT":
                if len(parts) < 2:
                    conn.send("Usage: ACCEPT <user>\n".encode())
                    continue
                
                sender_name = parts[1].lower().replace(" ", "")
                
                # Find sender connection
                sender_conn = None
                for c, name in clients.items():
                    if name == sender_name:
                        sender_conn = c
                        break
                
                if not sender_conn:
                    conn.send(f"User '{sender_name}' not found\n".encode())
                    continue
                
                transfer_key = (sender_conn, conn)
                if transfer_key in pending_transfers:
                    filename = pending_transfers[transfer_key]
                    del pending_transfers[transfer_key]
                    
                    file_thread = threading.Thread(target=send_file, args=(sender_conn, conn, filename))
                    file_thread.start()
                    conn.send(f"Accepting file from {sender_name}\n".encode())
                else:
                    conn.send(f"No pending file transfer from {sender_name}\n".encode())

            # REJECT FILE - PRIVATE
            elif command == "REJECT":
                if len(parts) < 2:
                    conn.send("Usage: REJECT <user>\n".encode())
                    continue
                
                sender_name = parts[1].lower().replace(" ", "")
                
                sender_conn = None
                for c, name in clients.items():
                    if name == sender_name:
                        sender_conn = c
                        break
                
                if sender_conn:
                    # Send rejection ONLY to sender
                    sender_conn.send(f"{clients[conn]} rejected your file transfer\n".encode())
                    conn.send(f"Rejected file from {sender_name}\n".encode())
                    pending_transfers.pop((sender_conn, conn), None)

            # EXIT
            elif command == "EXIT":
                exited_normally = True
                break

            else:
                conn.send("Invalid command. Use JOIN / MSG / PM / SEND / ACCEPT / REJECT / EXIT\n".encode())

        except:
            break

    # DISCONNECT HANDLING
    with lock:
        room = client_room.get(conn)

        if room and conn in rooms.get(room, set()):
            rooms[room].remove(conn)

            if exited_normally:
                broadcast(room, f"{username} left the chat")
            else:
                broadcast(room, f"{username} terminated")

        clients.pop(conn, None)
        client_room.pop(conn, None)
        
        # Clean up pending transfers
        to_remove = [k for k in pending_transfers.keys() if conn in k]
        for k in to_remove:
            del pending_transfers[k]

    conn.close()
    print(f"{username} disconnected")


# SSL SETUP
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("cert.pem", "key.pem")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(5)

print("Server started...")

while True:
    try:
        client, addr = sock.accept()
        conn = context.wrap_socket(client, server_side=True)

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        break

sock.close()