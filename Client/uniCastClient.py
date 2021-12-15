from argparse import ArgumentParser
import socket, tqdm, os


class UniCastClient:
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096  # send 4096 bytes each time step
    
    def __init__(self, remote_ip, remote_port, filename):
        # the ip address or hostname of the server, the receiver
        self.remote_ip = remote_ip
        # the port, let's use 5001
        self.remote_port = remote_port
        # the name of file we want to send, make sure it exists
        self.filename = filename
        self.filesize = os.path.getsize(filename)
        self.__socket = None
    
    def get_connected(self):
        # Connects to the server
        self.__socket = socket.socket()
        print(f"[+] Connecting to {self.remote_ip}:{self.remote_port}")
        self.__socket.connect((self.remote_ip, self.remote_port))
        print("[+] Connected.")

    def loop(self):
        # send the filename and filesize
        self.__socket.send(f"{self.filename}{UniCastClient.SEPARATOR}{self.filesize}".encode())
        # start sending the file
        progress = tqdm.tqdm(
            range(self.filesize), f"Sending {self.filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(self.filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(UniCastClient.BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in
                # busy networks
                self.__socket.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        # close the socket
        self.__socket.close()

if __name__ == "__main__":
     # setup argument parsing 
    parser = ArgumentParser(description="ACapella-NetEng UniCastClient")
    parser.add_argument(
        "-a",
        "--remote-ip",
        help="Server Socket IP Address",
    )
    parser.add_argument("-p", "--remote-port",
                        help="Server Socket Port Number", default=8080)
    parser.add_argument("-f", "--file",
                        help="Audio File To Be Send")
    args = parser.parse_args()
    client = UniCastClient(args.remote_ip, int(args.remote_port), args.file)
    client.get_connected()
    client.loop()