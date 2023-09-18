import socket
import io
from PIL import Image

running = True

PORT = 4444

# recvall allows a large amount of data to be received from a socket without fragmentation
def recvall(sock, n_bytes):
    # Create byte array to store completed data
    data = bytearray()
    # Continuously receive data until expected size reached
    while len(data) < n_bytes:
        packet = sock.recv(n_bytes - len(data))
        if not packet:
            # EOF reached
            return None
        data.extend(packet)
    return data

# Create server socket
# Continuously accept new connections
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(("", PORT))
    sock.listen()
    print("Server started on port " + str(PORT))
    # Accept incoming connections
    while running:
        conn, addr = sock.accept()
        with conn:
            print(f"New connection from {addr}")
            # Receive image size
            n_bytes = int.from_bytes(conn.recv(4), "big")
            print(f"    - Expecting {n_bytes} bytes")
            # Now receive whole image
            img_bytes = recvall(sock, n_bytes)
            # Check an image was received
            if img_bytes is not None:
                print("    - Received")
                img = Image.open(io.BytesIO(img_bytes))
                print("    - Decoded")
            else:
                # Failed to receive image
                print("    X | FAILED")