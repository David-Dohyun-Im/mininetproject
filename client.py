import socket

def client(server_ip="10.0.0.2", port=12345, file_path="/tmp/send_file.txt"):
    s = socket.socket()
    # Attempt to connect to the server
    # <Your codes here>

    # Open the file and send its contents
    # <Your codes here>

    print("[Client] File transfer complete.")
    s.close()

if __name__ == "__main__":
    client()
