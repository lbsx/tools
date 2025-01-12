import socket
import sys

SERVER_IP = '127.0.0.1'  # Replace with the server's IP address if not on the same machine
SERVER_PORT = 12345

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    command = " ".join(sys.argv[1:])
    sock.sendto(command.encode('utf-8'), (SERVER_IP, SERVER_PORT))

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            message = data.decode('utf-8')
            if message == "done":
                break
            print(message, end='') # 不换行打印，保持实时性
        except KeyboardInterrupt:
            print("end...")
            sock.sendto(b"TERMINATE", (SERVER_IP, SERVER_PORT))
    sock.close()

if __name__ == "__main__":
    main()