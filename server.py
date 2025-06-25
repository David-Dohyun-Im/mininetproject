import socket

def server(bind_ip="0.0.0.0", port=12345, save_path="/tmp/received_file.txt"):
    s = socket.socket()
    s.bind((bind_ip, port))
    s.listen(1)
    print("[Server] Waiting for incoming connection...")

    conn, addr = s.accept()
    print("[Server] Connected to:", addr)

    with open(save_path, "wb") as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)

    print("[Server] File received successfully.")
    conn.close()
    s.close()

if __name__ == "__main__":
    server()
