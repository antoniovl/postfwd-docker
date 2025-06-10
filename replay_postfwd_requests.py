
#!/usr/bin/python3
#
# Reads the content of the captured Postfix request file and sends it to a running
# postfwd instance. This is useful to test the ruleset.
#
import socket
import argparse
import json
import time

def send_policy_request(policy_dict, host, port):
    # 1) Build each "key=value\r\n"
    body = "".join(f"{key}={value}\r\n" for key, value in policy_dict.items())
    # 2) Append the blank line to signal end-of-request
    body += "\r\n"
    data = body.encode("utf-8")

    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            # Send everything
            sock.sendall(data)
            # Tell the server we're done writing so it will process
            sock.shutdown(socket.SHUT_WR)
            # Now read its response
            resp = sock.recv(4096).decode("utf-8", errors="ignore")
            return resp.strip()
    except Exception as e:
        return f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Replay Postfix policy requests to a Postfwd server.")
    parser.add_argument("jsonl_file", nargs="?", default="captured_requests.jsonl", help="Path to JSONL file of captured policy requests.")
    parser.add_argument("--host", default="localhost", help="Hostname or IP of the Postfwd server.")
    parser.add_argument("--port", type=int, default=10040, help="Port of the Postfwd server.")
    args = parser.parse_args()

    try:
        with open(args.jsonl_file, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Failed to read {args.jsonl_file}: {e}")
        return

    print(f"Replaying {len(lines)} requests to {args.host}:{args.port}")
    for i, line in enumerate(lines, 1):
        try:
            data = json.loads(line.strip())
        except json.JSONDecodeError as e:
            print(f"[{i}] Skipped invalid JSON: {e}")
            continue

        print(f"[{i}] Sending request from {data.get('client_address')} → {data.get('recipient')}")
        response = send_policy_request(data, args.host, args.port)
        print(f"    ↪ Response: {response}")
        time.sleep(0.2)

if __name__ == "__main__":
    main()
