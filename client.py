#!/usr/bin/env python

import socket
import os
import sys

def client(server_ip="10.0.0.2", port=12345, file_path="/tmp/send_file.txt"):
    """TCP client that reads a file and sends it to the server"""
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"[Client] ERROR: File not found: {file_path}")
            return 1
        
        # Get file size for progress tracking
        file_size = os.path.getsize(file_path)
        print(f"[Client] Preparing to send file: {file_path}")
        print(f"[Client] File size: {file_size} bytes")
        
        # Create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10.0)  # 10 second timeout
        
        print(f"[Client] Connecting to server {server_ip}:{port}...")
        
        # Attempt to connect to the server
        try:
            s.connect((server_ip, port))
            print(f"[Client] Connected successfully to {server_ip}:{port}")
        except socket.timeout:
            print("[Client] ERROR: Connection timeout")
            return 1
        except ConnectionRefusedError:
            print("[Client] ERROR: Connection refused - is the server running?")
            return 1
        except Exception as e:
            print(f"[Client] ERROR: Connection failed: {e}")
            return 1
        
        # Open the file and send its contents
        try:
            with open(file_path, "rb") as f:
                bytes_sent = 0
                chunk_size = 4096
                
                print("[Client] Starting file transfer...")
                
                while True:
                    # Read chunk from file
                    data = f.read(chunk_size)
                    if not data:
                        break
                    
                    # Send chunk to server
                    try:
                        s.sendall(data)
                        bytes_sent += len(data)
                        
                        # Show progress for larger files
                        if file_size > 1024:
                            progress = (bytes_sent / file_size) * 100
                            print(f"[Client] Progress: {bytes_sent}/{file_size} bytes ({progress:.1f}%)")
                    
                    except socket.timeout:
                        print("[Client] ERROR: Send timeout")
                        return 1
                    except Exception as e:
                        print(f"[Client] ERROR: Failed to send data: {e}")
                        return 1
                
                print(f"[Client] File transfer complete. Sent {bytes_sent} bytes")
                
        except IOError as e:
            print(f"[Client] ERROR: Failed to read file: {e}")
            return 1
        
    except Exception as e:
        print(f"[Client] ERROR: Unexpected error: {e}")
        return 1
    
    finally:
        try:
            s.close()
            print("[Client] Connection closed")
        except:
            pass
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = client()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[Client] Transfer interrupted by user")
        sys.exit(1)