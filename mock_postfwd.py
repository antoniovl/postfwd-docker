#!/usr/bin/python3
#
# Mocks a PolicyD Service.
# This program it's useful to collect requests sent by Postfix to the Policy Server.
# Collected data will be saved into the file specified in --output-file, which is
# "captured_requests.jsonl" by default.
# The script replay_postfwd_requests.py can be used to send the request data to the
# postfwd instance to test the configured rules.
#
import argparse
import json
import socket
import threading

output_file = "captured_requests.jsonl"
default_response = "action=DUNNO\n\n"

def parse_policy_request(raw_data):
    """
    Convert raw request text into a Python dict.
    """
    lines = raw_data.strip().splitlines()
    result = {}
    for line in lines:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            result[key] = value
    return result

def handle_client(conn, addr):
    print(f"Connection from {addr}")
    try:
        data = b""
        while True:
            chunk = conn.recv(1024)
            if not chunk:
                break
            data += chunk
            if b"\n\n" in data:
                break

        decoded = data.decode("utf-8", errors="replace").strip()
        parsed_request = parse_policy_request(decoded)

        print(f"Captured Request: {parsed_request}")

        # Append JSON line to file
        with open(output_file, "a") as f:
            f.write(json.dumps(parsed_request) + "\n")

        conn.sendall(default_response.encode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def run_server(listen_ip: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((listen_ip, port))
        server.listen()
        print(f"Listening on {listen_ip}:{port} (mock Postfwd)")

        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Emulates the behavior of a PolicyD Server.")
    parser.add_argument("--listen-ip", default="0.0.0.0", help="IP address to listen network requests.")
    parser.add_argument("--port", type=int, default=10040, help="Port of the policy server.")
    parser.add_argument("--output-file", default="captured_requests.jsonl", help="Output file name.")
    args = parser.parse_args()

    output_file = args.output_file

    run_server(args.listen_ip, args.port)

