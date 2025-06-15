from datetime import datetime
def log_message(message, filename="output/log.txt"):
    """Log messages to a file"""
    with open(filename, 'a') as f:
        f.write(f"{datetime.now().isoformat()}: {message}\n")