#!/usr/bin/python3
#
# Sends sample data to a running postfwd instance.
#
import socket
import time

# Configuration
POSTFWD_HOST = "localhost"
POSTFWD_PORT = 10040
REPEAT = 10              # Number of requests per user/IP combo
INTERVAL = 0.5           # Delay between requests (seconds)
USERS = ["user1@example.com", "user2@example.com", "user3@example.com"]
IPS = ["192.168.1.10", "192.168.1.20", "192.168.1.30"]

def send_request(user, ip):
    request_lines = [
        "request=smtpd_access_policy",
        "protocol_state=RCPT",
        "protocol_name=SMTP",
        f"client_address={ip}",
        f"client_name=mail.{ip}.local",
        f"reverse_client_name=mail.{ip}.local",
        f"helo_name=mail.{ip}.local",
        f"sender={user}",
        "recipient=rcpt@example.com",
        f"sasl_username={user}",
        ""
    ]
    request = "\n".join(request_lines).encode("utf-8")

    try:
        with socket.create_connection((POSTFWD_HOST, POSTFWD_PORT), timeout=2) as sock:
            sock.sendall(request)
            response = sock.recv(4096).decode("utf-8")
            return response.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    for user in USERS:
        for ip in IPS:
            print(f"\n Simulating traffic: {user} from {ip}")
            for i in range(1, REPEAT + 1):
                print(f"  ➜ [{i}/{REPEAT}] {user}@{ip}")
                response = send_request(user, ip)
                if "action=" in response:
                    print(f"    {response}")
                else:
                    print(f"     No action received or error: {response}")
                time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
