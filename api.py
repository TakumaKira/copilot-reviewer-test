import subprocess

def run_command(user_input):
    result = subprocess.run(user_input, shell=True, capture_output=True)  # command injection
    return result.stdout.decode()

def get_secret():
    api_key = "sk-1234567890abcdef"  # hardcoded API key
    return api_key
