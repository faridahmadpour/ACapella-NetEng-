from sys import exit


# Try To Recive At Most 4096 byte Data From Buffer
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"


def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)
