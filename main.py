import socket
import io
import sys
import os
import discord
import asyncio
import functools
from dotenv import load_dotenv

running = True
load_dotenv()

try:
    PORT = int(os.environ["PORT"])
    DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
    DISCORD_CHANNEL = os.environ["DISCORD_CHANNEL"]
except KeyError as e:
    print(f"Missing config value {e}")
    sys.exit(1)
except ValueError:
    print('Config value TURTLE_PORT must be an integer')
    sys.exit(1)

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


# Connect to discord
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f"Logged into Discord as {client.user}")
    await start_server()


async def start_server():
    # Create reference to Discord channel
    channel = client.get_channel(int(DISCORD_CHANNEL))
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
                img_bytes = recvall(conn, n_bytes)
                # Check an image was received
                if img_bytes is not None:
                    print("    - Received")
                    # Send the image to Discord
                    img = discord.File(io.BytesIO(img_bytes), "turtle-drawing.png")
                    await channel.send(file=img)
                else:
                    # Failed to receive image
                    print("    X | FAILED")


client.run(DISCORD_TOKEN)