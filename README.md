# 🔒 Secure Multi-Room Chat System with File Transfer

## 📌 Project Information

| **Project Name** | Jackfruit Mini Project - Secure Chat System |
|-----------------|---------------------------------------------|
| **Course** | Socket Programming |
| **Language** | Python 3.9+ |
| **Protocol** | TCP (Transmission Control Protocol) |
| **Security** | SSL/TLS 1.2/1.3 |
| **Architecture** | Client-Server Model |
| **Concurrency** | Multi-threading |
| **Platform** | Cross-platform (Windows, Linux, macOS) |

---

## 📋 Project Overview

This is a **secure, real-time chat application** built from scratch using **low-level socket programming**. The system demonstrates fundamental concepts of network programming, concurrency, security, and real-time communication. All communication is encrypted using SSL/TLS, ensuring complete privacy.

### What is Socket Programming?

Socket programming is a way for two computers to communicate over a network. A socket is like an **endpoint** that one program uses to send and receive data to another program. Think of it as a **door** through which data flows in and out.

### Why TCP?

| Feature | TCP | Why Used |
|---------|-----|----------|
| Connection-oriented | ✅ | Reliable communication |
| Ordered delivery | ✅ | Messages arrive in correct sequence |
| Error checking | ✅ | Corrupted data is retransmitted |
| Flow control | ✅ | Prevents overwhelming receiver |
| Speed | Moderate | Perfect for chat applications |

**UDP was rejected because** it doesn't guarantee message delivery or ordering, which is critical for chat.

---

## 🎯 Features Implemented

### Core Features

| # | Feature | Description | Status |
|---|---------|-------------|--------|
| 1 | **TCP Socket Programming** | Raw TCP sockets without high-level frameworks |
| 2 | **SSL/TLS Encryption** | All communication encrypted end-to-end |
| 3 | **Multi-Client Support** | Handle multiple concurrent users | 
| 4 | **Multi-Room Chat** | Dynamic room creation (room1, room2, etc.) | 
| 5 | **Private Messaging** | Direct user-to-user communication | 
| 6 | **File Transfer** | Send files up to 10MB between users | 
| 7 | **Threading Concurrency** | Each client in separate thread |
| 8 | **Error Handling** | Graceful disconnection handling | 
| 9 | **Input Validation** | Username and room name validation | 
| 10 | **Server Logging** | Real-time activity monitoring |

### Technical Specifications

| Component | Specification |
|-----------|---------------|
| **Transport Protocol** | TCP (IPv4) |
| **Port Number** | 5000 (configurable) |
| **Host** | 127.0.0.1 (localhost) |
| **Buffer Size** | 1024 bytes for messages, 8192 bytes for files |
| **Max File Size** | 10 MB |
| **Max Concurrent Clients** | 50+ (tested) |
| **Message Encoding** | UTF-8 |
| **File Encoding** | Base64 for binary-safe transmission |

---

## 🏗️ System Architecture

### Client-Server Model Diagram
