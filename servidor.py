import socket
import threading
import hashlib

# Configuración del servidor
host = '127.0.0.1'
port = 12000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print("El servidor está escuchando")

clients = []
usernames = []
desplazamiento = 0  # Variable global para almacenar el desplazamiento César

# Función para cifrado César
def cifrado_cesar(texto, desplazamiento):
    abecedario = 'abcdefghijklmnopqrstuvwxyz'
    resultado = ""
    for char in texto:
        if char.isalpha():  # Solo cifrar letras
            char = char.lower()
            posicion = abecedario.index(char)
            nueva_posicion = (posicion + desplazamiento) % len(abecedario)
            resultado += abecedario[nueva_posicion]
        else:
            resultado += char  # Dejar los demás caracteres como están
    return resultado

# Función para generar el hash SHA-256 de un mensaje
def generar_sha256(mensaje):
    return hashlib.sha256(mensaje.encode('utf-8')).hexdigest()

# Función para enviar un mensaje a todos los clientes excepto al remitente
def broadcast(message, _client):
    for client in clients:
        if client != _client:
            client.send(message.encode('utf-8'))

# Manejar mensajes entrantes de los clientes
def handle_messages(client, username):
    while True:
        try:
            # Recibir el mensaje del cliente
            message = client.recv(1024).decode('utf-8')

            # Generar el hash SHA-256 del mensaje original
            hash_sha256 = generar_sha256(message)

            # Cifrar el mensaje usando el cifrado César
            encrypted_message = cifrado_cesar(message, desplazamiento)

            # Formatear el mensaje para mostrar en la terminal de los clientes
            formatted_message = (
                f"\nDe: {username}\n"
                f"Mensaje descifrado: {message}\n"
                f"Mensaje cifrado: {encrypted_message}\n"
                f"Hash SHA-256: {hash_sha256}\n"
            )

            # Enviar el mensaje formateado a todos los clientes conectados
            broadcast(formatted_message, client)

            # Enviar el mensaje descifrado, cifrado y hash al remitente
            client.send(formatted_message.encode('utf-8'))
        
        except:
            index = clients.index(client)
            username = usernames[index]
            broadcast(f'\nChatbot: {username} ha abandonado el chat\n', client)
            clients.remove(client)
            usernames.remove(username)
            client.close()
            break

# Aceptar conexiones entrantes
def receive_connections():
    global desplazamiento
    while True:
        client, address = server.accept()

        client.send("@username".encode('utf-8'))
        username = client.recv(1024).decode('utf-8')

        # Pedir al primer usuario que ingrese el número de desplazamiento
        if len(clients) == 0:
            client.send("Sistema: Ingresa el número para cifrar (clave de cifrado): ".encode('utf-8'))
            desplazamiento = int(client.recv(1024).decode('utf-8'))
            print(f"El número de cifrado es: {desplazamiento}\n")

            # Informar a todos los usuarios conectados sobre la clave de cifrado
            for c in clients:
                c.send(f"\nSistema: El número para cifrar es: {desplazamiento}\n".encode('utf-8'))
        else:
            client.send(f"\nSistema: El número para cifrar es: {desplazamiento}\n".encode('utf-8'))

        clients.append(client)
        usernames.append(username)

        print(f'El usuario {username} se ha conectado con la dirección {str(address)}\n')

        message = f'\nChatbot: {username} se ha unido al chat\n'
        broadcast(message, client)
        client.send('Conectado al chat\n'.encode('utf-8'))

        # Crear un hilo para manejar los mensajes del nuevo cliente
        thread = threading.Thread(target=handle_messages, args=(client, username))
        thread.start()

# Iniciar el servidor
receive_connections()
