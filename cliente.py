import socket
import threading

username = input("Pon tu nombre de usuario: ")

host = '127.0.0.1'
port = 12000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(f"\n{message}")  # Mostrar el mensaje recibido con saltos de línea
        except Exception as e:
            print(f"\nHa ocurrido un error: {e}")
            client.close()
            break

def write_messages():
    while True:
        try:
            message = input(f'{username}: ')
            client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"\nError al enviar el mensaje: {e}")
            client.close()
            break

# Hilos para recibir y enviar mensajes
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

write_thread = threading.Thread(target=write_messages)
write_thread.start()
