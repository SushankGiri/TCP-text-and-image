import socket
import threading
import struct
import os
# Constants
HOST = '71.202.182.76'
PORT = 5555
BUFFER_SIZE = 8192

def receive_messages(client_socket):
    """Receive messages from the server."""
    while True:
        try:
            # Receive the first 3 bytes to check if it's an image or a message
            header = client_socket.recv(3)
            if not header:
                print("Connection closed by the server.")
                break

            if header == b'IMG':
                print("Receiving image...")

                # First, receive the image size
                image_size_data = client_socket.recv(4)
                image_size = struct.unpack('!I', image_size_data)[0]

                # Receive the image data of the expected size
                image_data = bytearray()
                while len(image_data) < image_size:
                    chunk = client_socket.recv(min(image_size - len(image_data), BUFFER_SIZE))
                    if not chunk:
                        break
                    image_data.extend(chunk)

                # Save the image to a file
                filename = "received_image.png"
                with open(filename, 'wb') as f:
                    f.write(image_data)

                print(f"Image received and saved as {filename}.")

            elif header == b'MSG':
                # First, receive the length of the message
                message_length_data = client_socket.recv(4)
                message_length = struct.unpack('!I', message_length_data)[0]

                # Receive the message content
                message = client_socket.recv(message_length).decode('utf-8')
                print(f"Message: {message}")

        except Exception as e:
            print(f"An error occurred while receiving messages: {e}")
            break

def send_messages(client_socket):
    """Send messages or images to the server."""
    while True:
        msg = input("Enter message or 'img <file_path>' to send an image: ")

        if msg.startswith('img '):
            # Send image
            filepath = msg[4:]  # Remove 'img ' prefix
            if os.path.isfile(filepath):
                print(f"Sending image: {filepath}")
                try:
                    with open(filepath, 'rb') as f:
                        image_data = f.read()
                        image_size = len(image_data)

                        # Send the image header and size
                        client_socket.sendall(b'IMG')
                        client_socket.sendall(struct.pack('!I', image_size))  # Send image size (4 bytes)

                        # Now, send the image data in chunks
                        client_socket.sendall(image_data)
                    print(f"Image sent: {filepath}")
                except Exception as e:
                    print(f"Error sending image: {e}")
            else:
                print("File not found.")
        else:
            # Send text message
            message_data = msg.encode('utf-8')
            message_length = len(message_data)

            client_socket.sendall(b'MSG')
            client_socket.sendall(struct.pack('!I', message_length))  # Send message length (4 bytes)
            client_socket.sendall(message_data)

def start_client():
    """Start the TCP client."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        threading.Thread(target=receive_messages, args=(client_socket,)).start()
        send_messages(client_socket)
    except Exception as e:
        print(f"Could not connect to the server: {e}")

if __name__ == "__main__":
    start_client()
input()
