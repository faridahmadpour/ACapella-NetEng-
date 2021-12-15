from threading import Thread
import os, tqdm, errno
from utils import BUFFER_SIZE, SEPARATOR 


class ClientHandler(Thread):
    def __init__(self, conn, ip, port):
        Thread.__init__(self)
        self.conn = conn
        self.ip = ip
        self.port = port
        print(
            "[+] New Server Socket Thread Started For Client: " + ip + ":" + str(port)
        )

    def run(self):
        # receive the file infos
        # receive using client socket, not server socket
        received = self.conn.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        completeDir = os.path.join(os.getcwd(), "files", filename)
        if not os.path.exists(os.path.dirname(completeDir)):
            try:
                os.makedirs(os.path.dirname(completeDir), exist_ok=True)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        # convert to integer
        filesize = int(filesize)
        progress = tqdm.tqdm(
            range(filesize),
            f"Receiving {filename}",
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )
        # Measure network Latency
        with open(completeDir, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = self.conn.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is received file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        # close the client socket
        self.conn.close()
