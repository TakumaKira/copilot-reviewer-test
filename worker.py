import os

def run_task(command):
    os.system(command)  # command injection via os.system

def store_token(token):
    with open("/tmp/token.txt", "w") as f:
        f.write(token)  # storing sensitive data in /tmp
