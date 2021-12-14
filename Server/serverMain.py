from clientHandler import *
from socket import AF_INET, SOCK_STREAM, socket
from argparse import ArgumentParser
from multiCastSender import MultiCastSender


class serverClass:
    def __init__(self):
        # stores all the clients connected
        self.clientList = []
        self.tcpServer = None  # TCP Socket Of The Server itself

    def listen(self, sock_addr):
        # Creates a listener socket
        self.sock_addr = sock_addr  # Is A Tuple (TCP_IP, TCP_PORT)
        self.tcpServer = socket(AF_INET, SOCK_STREAM)  # TCP Socket
        self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.tcpServer.bind(sock_addr)

        # enabling our server to accept connections
        # 5 here is the number of unaccepted connections that
        # the system will allow before refusing new connections
        self.tcpServer.listen(5)
        print("Socket %s:%d is In Listening State" %
              (self.tcpServer.getsockname()))

    def loop(self, clients: list, max_clients: int):
        # server's main loop. Creates clientHandler's for each connecter
        print("Falling to Serving Loop, Press Ctrl+C To Terminate ...")
        clients = []
        try:
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
                    socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1
                )
                conn.setsockopt(
                    socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec
                )
                conn.setsockopt(
                    socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec
                )
                conn.setsockopt(
                    socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails
                )

                client = ClientHandler(conn, ip, port)
                self.clientList.append(client)
                client.start()
        except KeyboardInterrupt:
            print("Ctrl+C Issued Closing Server...")
        finally:
            if conn is not None:
                conn.close()
            self.tcpServer.close()

        map(lambda x: x.join(), clients)

    def merge_files(self):
        completeDir = os.path.join(os.getcwd(), "files")
        files = os.listdir(completeDir)
        files.sort()

        with open("merged.mp3", "wb") as merged_file:
            for fs in files:
                with open(fs, "rb") as received_file:
                    merged_file.write(received_file.read())

    def multicast(self):
        mc_sender = MultiCastSender(
            host_ip=socket.gethostbyname(socket.getfqdn()),
            mcgrp_ip="",
            mc_port="",
            file_addr="merged.mp3",
            msg_buf=None,
        )
        mc_sender.mc_send()


if __name__ == "__main__":
    parser = ArgumentParser(description="Tic tac toe game server")
    parser.add_argument(
        "-a",
        "--server-addr",
        help="Listening address. Default localhost.",
        default="0.0.0.0",
    )
    parser.add_argument("-c", "--clients", help="List of clients", nargs="+")
    parser.add_argument("-c", "--max_clients",
                        help="Number of clients", default=2)
    args = parser.parse_args()
    server = serverClass()
    server.listen((args.server_addr, 8080))
    server.loop(args.clients, args.max_clients)
    server.merged_file()
    server.multicast()
    print("Terminating...")
