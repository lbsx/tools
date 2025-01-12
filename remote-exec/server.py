import logging
import os
import selectors
import socket
import subprocess
import shlex
import sys
import time

HOST = '0.0.0.0'  # 监听所有可用接口
PORT = 12345


def run_command(command, client_address, sock):
    try:
        """
        使用 selectors 模块实现更现代的实时输出，解决可执行文件缓冲问题。
        """
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # bufsize=1, 
            universal_newlines=False
        )

        stdout_fd = process.stdout.fileno()
        stderr_fd = process.stderr.fileno()

        selector = selectors.DefaultSelector()
        selector.register(stdout_fd, selectors.EVENT_READ, "STDOUT")
        selector.register(stderr_fd, selectors.EVENT_READ, "STDERR")
        selector.register(sock, selectors.EVENT_READ, "CLIENT")

        while True:
            events = selector.select()  
            for key, _ in events:
                try:
                    if key.data == "CLIENT":
                        data, _ = sock.recvfrom(1024)
                        if data == b"TERMINATE":
                            process.send_signal(subprocess.signal.SIGTERM)
                            break
                        else:
                            continue
                    else:
                        output = os.read(stdout_fd, 1024)
                        if output:
                            sock.sendto(output, client_address)
                except BlockingIOError:
                    continue

            if process.poll() is not None:
                break

        

        return_code = process.returncode
        if return_code != 0:
            sock.sendto(
                f"Command failed with return code: {return_code}".encode('utf-8'), client_address)
        else:
            sock.sendto("Command finished successfully.".encode('utf-8'), client_address)
        sock.sendto(b"done", client_address)
        selector.close()

    except Exception as e:
        logging.exception(f"Error: {e}".encode('utf-8'), client_address)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        data, address = sock.recvfrom(1024)
        command = data.decode('utf-8').strip()
        if command:
            print(f"Received command: {command} from {address}")
            run_command(command, address, sock)


if __name__ == "__main__":
    main()
