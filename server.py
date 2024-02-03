import socket
import threading
import redis

# Підключення до Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def broadcast(message, sender_username):
    message = f"{sender_username}: {message}"

    # Збереження повідомлення в Redis
    redis_client.rpush('message_history', message)

    # Отримання активних клієнтів з Redis
    active_clients = redis_client.smembers('active_clients')

    # Розсилка повідомлення всім активним клієнтам
    for client_username in active_clients:
        if client_username != sender_username:
            client_socket = redis_client.hget('client_sockets', client_username)
            try:
                client_socket.send(message.encode('utf-8'))
            except:
                pass

def handle_client(client_socket, username):
    # Повідомлення клієнта про успішний вхід
    client_socket.send("Успішний вхід!".encode('utf-8'))

    # Додавання клієнта до множини активних клієнтів в Redis
    redis_client.sadd('active_clients', username)

    # Збереження сокету клієнта в Redis
    redis_client.hset('client_sockets', username, client_socket)

    # Відправлення історії повідомлень клієнту
    message_history = redis_client.lrange('message_history', 0, -1)
    for message in message_history:
        client_socket.send(message.encode('utf-8'))

    # Повідомлення інших клієнтів про нового користувача
    broadcast(f"{username} приєднався до чату.", username)

    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if message.lower() == 'вийти':
            break

        # Розсилка повідомлення всім клієнтам
        broadcast(message, username)

    # Видалення клієнта з множини активних клієнтів в Redis
    redis_client.srem('active_clients', username)

    # Видалення сокету клієнта з Redis
    redis_client.hdel('client_sockets', username)

    # Повідомлення інших клієнтів про виходження користувача
    broadcast(f"{username} залишив чат.", username)

    # Закриття сокету клієнта
    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 8081))
    server_socket.listen(5)
    print("Сервер чату запущено.")

    while True:
        client_socket, address = server_socket.accept()

        # Отримання імені користувача від клієнта
        username = client_socket.recv(1024).decode().strip()

        # Запуск нового потоку для обробки клієнта
        client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
        client_thread.start()

if __name__ == "__main__":
    main()
