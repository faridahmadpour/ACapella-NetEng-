from clientHandler import *
from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_KEEPALIVE, TCP_KEEPIDLE, TCP_KEEPINTVL, TCP_KEEPCNT, IPPROTO_TCP, SO_REUSEADDR
from argparse import ArgumentParser
from multiCastSender import MultiCastSender
from utils import handler
import wave
from signal import signal, SIGINT


class serverClass:
    def __init__(self):
        # Stores all the clients connected
        self.clientList = []
        self.tcpServer = None  # TCP Socket Of The Server itself

    def listen(self, sock_addr):
        # Creates a listener socket
        self.sock_addr = sock_addr  # Is A Tuple (TCP_IP, TCP_PORT)
        self.tcpServer = socket(AF_INET, SOCK_STREAM)  # TCP Socket
        self.tcpServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.tcpServer.bind(sock_addr)
        # Enabling our server to accept connections
        # 5 here is the number of unaccepted connections that
        # The system will allow before refusing new connections
        self.tcpServer.listen(5)
        print("Socket %s:%d is In Listening State" %
              (self.tcpServer.getsockname()))

    def loop(self, max_clients: int):
        # Tell Python to run the handler() function when SIGINT is recieved
        signal(SIGINT, handler)
        # Server's main loop. Creates clientHandler's for each connecter
        print("Falling to Serving Loop, Press Ctrl+C To Terminate...")
        clients = []
        while True:
            if len(clients) == max_clients:
                break
            conn = None  # Each Client Socket To Be Stored In The Proper Object of Class ClientHandler
            print("Awaiting New Clients...")
            # accept connection if there is any
            # client_socket[Socket Object], client_address[Tuple Of Client (IP, PORT)]
            (conn, (ip, port)) = self.tcpServer.accept()
            # Set TCP KeepAlive Options
            after_idle_sec = 1
            interval_sec = 2
            max_fails = 3
            conn.setsockopt(
                SOL_SOCKET, SO_KEEPALIVE, 1
            )
            conn.setsockopt(
                IPPROTO_TCP, TCP_KEEPIDLE, after_idle_sec
            )
            conn.setsockopt(
                IPPROTO_TCP, TCP_KEEPINTVL, interval_sec
            )
            conn.setsockopt(
                IPPROTO_TCP, TCP_KEEPCNT, max_fails
            )
            client = ClientHandler(conn, ip, port)
            self.clientList.append(client)
            clients.append(conn)
            client.start()
        map(lambda x: x.join(), self.clientList)
        self.tcpServer.close()

    def merged_files(self, verbose=1):
        """
        Concatenates two or more audio files into one audio file using PyDub library
        and save it to `output_path`. A lot of extensions are supported, more on PyDub's doc.
        """
        def get_file_extension(filename):
            """A helper function to get a file's extension"""
            return os.path.splitext(filename)[1].lstrip(".")

        completeDir = os.path.join(os.getcwd(), "files")
        files = os.listdir(completeDir)
        files.sort()
        clips = []
        # wrap the audio clip paths with tqdm if verbose
        files = tqdm(files, "Reading audio file") if verbose else files
        for clip_path in files:
            # get extension of the audio file
            extension = get_file_extension(clip_path)
            # load the audio clip and append it to our list
            clip = AudioSegment.from_file(clip_path, extension)
            clips.append(clip)
    
        final_clip = clips[0]
        range_loop = tqdm(list(range(1, len(clips))), "Concatenating audio") if verbose else range(1, len(clips))
        for i in range_loop:
            # looping on all audio files and concatenating them together
            # ofc order is important
            final_clip = final_clip + clips[i]
        # export the final clip
        final_clip_extension = get_file_extension("merged.mp3")
        if verbose:
            print("Exporting resulting audio file to merged.mp3")
        final_clip.export("merged.mp3", format=final_clip_extension)

        # completeDir = os.path.join(os.getcwd(), "files")
        # files = os.listdir(completeDir)
        # files.sort()
        # data = []
        # for clip in files:
        #     clip = os.path.join("./files", clip)
        #     w = wave.open(clip, "rb")
        #     data.append([w.getparams(), w.readframes(w.getnframes())])
        #     w.close()
        # output = wave.open("merged.mp3")
        # output.setparams(data[0][0])
        # for i in range(len(data)):
        #     output.writeframes(data[i][1])
        # output.close()


    def multicast(self):
        mc_sender = MultiCastSender(
            host_ip=socket.gethostbyname(socket.getfqdn()),
            mcgrp_ip="",
            mc_port="",
            file_addr="merged.mp3",
            msg_buf=None
        )
        mc_sender.mc_send()


if __name__ == "__main__":
    parser = ArgumentParser(description="Tic tac toe game server")
    parser.add_argument(
        "-a",
        "--server-addr",
        help="Listening address. Default localhost.",
        default="0.0.0.0"
    )
    parser.add_argument("-p", "--port",
                        help="Port Number", default=8080)
    parser.add_argument("-c", "--max-clients",
                        help="Number of clients", default=2)
    args = parser.parse_args()
    server = serverClass()
    server.listen((args.server_addr, int(args.port)))
    server.loop(int(args.max_clients))
    server.merged_files()
    # server.multicast()
    print("Terminating...")
