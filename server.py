#!/usr/bin/env python

import socket
import threading
import os
import sys

def handle_client(conn, addr, save_path="/tmp/send_file.txt"):
    """Handle individual client connections"""
    try:
        print(f"[Server] Connection established with {addr}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Receive file data
        with open(save_path, "wb") as f:
            total_received = 0
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    f.write(data)
                    total_received += len(data)
                except socket.timeout:
                    print(f"[Server] Connection timeout with {addr}")
                    break
                except Exception as e:
                    print(f"[Server] Error receiving data from {addr}: {e}")
                    break
        
        print(f"[Server] File received successfully from {addr}")
        print(f"[Server] Total bytes received: {total_received}")
        print(f"[Server] File saved to: {save_path}")
        
    except Exception as e:
        print(f"[Server] Error handling client {addr}: {e}")
    finally:
        try:
            conn.close()
            print(f"[Server] Connection with {addr} closed")
        except:
            pass

def server(bind_ip="0.0.0.0", port=12345, save_path="/tmp/send_file.txt"):
    """TCP server that accepts multiple connections"""
    server_socket = None
    
    try:
        # Create server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind and listen
        server_socket.bind((bind_ip, port))
        server_socket.listen(5)  # Allow up to 5 queued connections
        
        print(f"[Server] TCP server started on {bind_ip}:{port}")
        print(f"[Server] Files will be saved to: {save_path}")
        print("[Server] Waiting for incoming connections...")
        print("[Server] Press Ctrl+C to stop the server")
        
        connection_count = 0
        
        while True:
            try:
                # Accept new connection
                conn, addr = server_socket.accept()
                connection_count += 1
                
                # Set socket timeout for individual connections
                conn.settimeout(30.0)  # 30 second timeout
                
                print(f"[Server] New connection #{connection_count} from {addr}")
                
                # Handle each connection in a separate thread for multiple connections
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(conn, addr, f"{save_path}.{connection_count}")
                )
                client_thread.daemon = True
                client_thread.start()
                
            except KeyboardInterrupt:
                print("\n[Server] Received interrupt signal, shutting down...")
                break
            except Exception as e:
                print(f"[Server] Error accepting connection: {e}")
                continue
                
    except Exception as e:
        print(f"[Server] Fatal error: {e}")
        return 1
    finally:
        if server_socket:
            try:
                server_socket.close()
                print("[Server] Server socket closed")
            except:
                pass
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = server()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[Server] Server stopped by user")
        sys.exit(0)