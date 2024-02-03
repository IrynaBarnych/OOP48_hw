import socket
import threading
import redis

# Підключення до Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except:
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8081))

    response = client_socket.recv(1024).decode('utf-8')
    print(response)

    if response == "Введіть ваше ім'я користувача: ":
        username = input("Ім'я користувача: ")
        client_socket.send(username.encode('utf-8'))

    response = client_socket.recv(1024).decode('utf-8')
    print(response)

    if response == "Введіть ваш пароль: ":
        password = input("Пароль: ")
        client_socket.send(password.encode('utf-8'))

    login_status = client_socket.recv(1024).decode('utf-8')
    print(login_status)

    if login_status == "Успішний вхід!":
        print("Ви тепер у чаті.")
        print("Напишіть 'вийти', щоб залишити чат.")

        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.start()

        while True:
            message = input("Ви: ")
            client_socket.sendall(message.encode('utf-8'))

            if message.lower() == 'вийти':
                break

    client_socket.close()

if __name__ == "__main__":
    main()
