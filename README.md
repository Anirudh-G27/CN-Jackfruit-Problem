# 🔒 Secure Multi-Room Chat System with File Transfer

## 📌 Project Information

| **Project Name** | Secure Socket Chat System |
|-----------------|---------------------------------------------|
| **Language** | Python 3.9+ |
| **Protocol** | TCP (Transmission Control Protocol) |
| **Security** | SSL/TLS 1.2/1.3 (using provided `cert.pem` & `key.pem`) |
| **Architecture** | Client-Server Model |
| **Concurrency** | Multi-threading |

---

## 📋 Project Overview

This is a **secure, real-time chat application** built using **low-level socket programming**. The system demonstrates fundamental concepts of network programming, concurrency, security, and real-time communication. All communication is encrypted using SSL/TLS, ensuring complete privacy.

### What is Socket Programming?
Socket programming is a way for two computers to communicate over a network. A socket is like an **endpoint** that one program uses to send and receive data to another program. Think of it as a **door** through which data flows in and out.

---

## 🏗️ System Architecture

### Client-Server Model Diagram


The system follows a **Star Topology** where the central Server acts as the "Source of Truth":
1.  **Server:** Manages all client connections, maintains room memberships, and routes messages/files.
2.  **Clients:** Provide the user interface, handle input, and decode incoming data. 
3.  **Flow:** Client $\rightarrow$ SSL Wrap $\rightarrow$ Server Processing $\rightarrow$ Target Client(s).

### Concurrency Model
The server utilizes a **Thread-per-Client** model. [cite_start]When a new connection is accepted, a dedicated worker thread is spawned to handle that specific user's logic (`handle_client`), allowing the main thread to continue listening for new connections. 

---

## 🛠️ Setup & Installation

### 1. Prerequisites
* **Python 3.9+** installed.
* **SSL Files:** Ensure the `cert.pem` and `key.pem` files you provided are present in the same directory as `server.py`. 

### 2. Running the Server
* The server binds to `127.0.0.1:5000` and loads your SSL certificates to secure the line. 
```bash
python server.py
```

### 3. Running the Client
* Open a new terminal for every client you want to connect: 
```bash
python client.py
```

---

## 🚀 Usage Instructions

### Step 1: Authentication
Upon launching `client.py`, enter a **username**. 
Usernames are case-insensitive and spaces are removed automatically. 
If a username is already taken, the server will disconnect you. 

### Step 2: Commands Reference

| Command | Syntax | Description |
| :--- | :--- | :--- |
| **JOIN** | `JOIN room1` | Joins a room. [cite_start]Must match the format `room<number>`. |
| **MSG** | `MSG Hello!` | [cite_start]Broadcasts a message to everyone in your current room. |
| **PM** | `PM alice Hey` | [cite_start]Sends a private message to a specific user. |
| **SEND** | `SEND bob file.txt` | [cite_start]Requests to send a file (Max 10MB) to another user.  |
| **ACCEPT** | `ACCEPT alice` | [cite_start]Confirms and begins receiving a file from a sender. |
| **REJECT** | `REJECT alice` | [cite_start]Declines a pending file transfer.  |
| **EXIT** | `EXIT` | [cite_start]Safely disconnects from the server. |

---

## 🛡️ Security Features

**SSL/TLS Encryption**: Uses the `ssl` module and your `.pem` files to wrap raw sockets, preventing eavesdropping. 
**Base64 Encoding**: Files are encoded into Base64 during transit to ensure binary data doesn't interfere with text-based command parsing. 
**Thread Safety**: Uses `threading.Lock()` to prevent data corruption when multiple users update room lists simultaneously. 
