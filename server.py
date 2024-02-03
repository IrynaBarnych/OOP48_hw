import asyncio
import redis
import socket

async def handle_client(client_socket, address, redis_client):
    print(f"З'єднання встановлено з {address}")

    while True:
        message = client_socket.recv(1024).decode()
        if message.lower() == 'вихід':
            break
        print(f"Клієнт {address}: {message}")

        # Store message in Redis (Modify this part based on your Redis setup)
        redis_client.lpush('messages', f"{address}: {message}")

        response = input("Сервер: ")
        client_socket.send(response.encode())


    print(f"Розмову з {address} завершено")
    client_socket.close()

async def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 8057))
    server_socket.listen(1)
    print("Очікування з'єднань...")

    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    while True:
        client_socket, address = await loop.sock_accept(server_socket)
        loop.create_task(handle_client(client_socket, address, redis_client))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())