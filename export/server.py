import socket
import threading
import struct

# Constants
HOST = '0.0.0.0'
PORT = 5555
BUFFER_SIZE = 8192

# List to keep track of connected clients
clients = []

def broadcast(data, client_socket):
    """Broadcast data to all clients except the sender."""
    for client in clients:
        if client != client_socket:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"Error sending message to client: {e}")
                client.close()
                clients.remove(client)

def receive_fixed_length_data(client_socket, size):
    """Receive a fixed amount of data from the client."""
    data = bytearray()
    while len(data) < size:
        packet = client_socket.recv(min(size - len(data), BUFFER_SIZE))
        if not packet:
            return None  # Connection closed
        data.extend(packet)
    return data

def handle_client(client_socket, address):
    """Handle communication with a connected client."""
    print(f"Connection from {address} has been established.")

    while True:
        try:
            # Receive the first 3 bytes to determine the message type
            header = client_socket.recv(3)
            if not header:
                print(f"Connection closed by client {address}.")
                break

            if header == b'IMG':
                print(f"Receiving image from {address}")

                # Receive the image size (4 bytes as an unsigned int)
                image_size_data = client_socket.recv(4)
                if not image_size_data:
                    break

                image_size = struct.unpack('!I', image_size_data)[0]

                # Now, receive the image data of the expected size
                image_data = receive_fixed_length_data(client_socket, image_size)
                if image_data is None:
                    print("Failed to receive the full image data.")
                    break

                # Save the image to a file
                filename = f"received_image_{address[1]}.png"
                with open(filename, 'wb') as f:
                    f.write(image_data)

                print(f"Image received from {address} and saved as {filename}.")
                # Broadcast the image to other clients
                broadcast(b'IMG' + image_size_data + image_data, client_socket)

            elif header == b'MSG':
                # Handle text message
                message_length_data = client_socket.recv(4)
                if not message_length_data:
                    break
                message_length = struct.unpack('!I', message_length_data)[0]

                message = receive_fixed_length_data(client_socket, message_length).decode('utf-8')
                print(f"Message from {address}: {message}")

                # Broadcast the text message to all clients
                broadcast(b'MSG' + message_length_data + message.encode('utf-8'), client_socket)

        except Exception as e:
            print(f"Error while handling client {address}: {e}")
            break

    client_socket.close()
    clients.remove(client_socket)
    print(f"Connection from {address} closed.")

def start_server():
    """Start the TCP server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Server is listening...")

    while True:
        try:
            client_socket, address = server_socket.accept()
            clients.append(client_socket)
            threading.Thread(target=handle_client, args=(client_socket, address)).start()
        except Exception as e:
            print(f"Error accepting connections: {e}")

if __name__ == "__main__":
    start_server()
