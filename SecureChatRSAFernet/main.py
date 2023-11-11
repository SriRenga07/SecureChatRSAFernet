import socket
import threading
import rsa
from cryptography.fernet import Fernet

# Generate an RSA key pair for key exchange
(pub_key, priv_key) = rsa.newkeys(2048)

choice = input("Do you want to host (1) or to connect (2): ")

if choice == "1":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("192.168.1.6", 9999))    # give ip
    server.listen()
    client, _ = server.accept()

    # Send the server's public key to the client
    server_pub_key = pub_key.save_pkcs1()
    client.send(server_pub_key)

    # Generate a symmetric encryption key for Fernet
    encryption_key = Fernet.generate_key()
    client.send(encryption_key)

    print("Using encryption key:", encryption_key)

elif choice == "2":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.1.6", 9999))     # give ip

    # Receive the server's public key
    server_pub_key_data = client.recv(4096)
    server_pub_key = rsa.PublicKey.load_pkcs1(server_pub_key_data)

    # Receive the symmetric encryption key
    encryption_key = client.recv(4096)

    print("Using encryption key:", encryption_key)

else:
    exit()

# Create a Fernet cipher with the received encryption key
cipher_suite = Fernet(encryption_key)

def sending_messages(c):
    while True:
        message = input("")
        encrypted_message = cipher_suite.encrypt(message.encode())
        c.send(encrypted_message)
        print("you: " + message)

def receiving_messages(c):
    while True:
        encrypted_message = c.recv(4096)
        message = cipher_suite.decrypt(encrypted_message).decode()
        print("Partner: " + message)

threading.Thread(target=sending_messages, args=(client,)).start()

threading.Thread(target=receiving_messages, args=(client,)).start()
