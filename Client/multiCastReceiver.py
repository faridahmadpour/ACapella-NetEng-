from argparse import ArgumentParser
import socket, os, struct
import threading, pyaudio, time, queue

class MultiCastReceiver:
    BUFF_SIZE = 65536
    CHUNK = 10*1024

    def __init__(self, fromnicip, mcgrpip, mcport):
        self.fromnicip = fromnicip
        self.mcgrpip = mcgrpip
        self.mcport = mcport
        # This creates a UDP socket
        self.__receiver = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
            proto=socket.IPPROTO_UDP,
            fileno=None,
        )

    def mc_recv(self):
        # This configure the socket to receive datagrams sent to this multicast
        # end point, i.e., the pair of
        #   (multicast group ip address, mulcast port number)
        # that must match that of the sender
        bindaddr = (self.mcgrpip, self.mcport)
        self.__receiver.bind(bindaddr)
        # This joins the socket to the intended multicast group. The implications
        # are two. It specifies the intended multicast group identified by the
        # multicast IP address.  This also specifies from which network interface
        # (NIC) the socket receives the datagrams for the intended multicast group.
        # It is important to note that socket.INADDR_ANY means the default network
        # interface in the system (ifindex = 1 if loopback interface present). To
        # receive multicast datagrams from multiple NICs, we ought to create a
        # socket for each NIC. Also note that we identify a NIC by its assigned IP
        # address.
        if self.fromnicip == "0.0.0.0":
            mreq = struct.pack("=4sl", socket.inet_aton(
                self.mcgrpip), socket.INADDR_ANY)
        else:
            mreq = struct.pack(
                "=4s4s", socket.inet_aton(self.mcgrpip), socket.inet_aton(self.fromnicip)
            )
        self.__receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.__receiver.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, MultiCastReceiver.BUFF_SIZE)
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True,
                    frames_per_buffer=MultiCastReceiver.CHUNK)
        # Receive the mssage
        DATA_SIZE, _= self.__receiver.recvfrom(MultiCastReceiver.BUFF_SIZE)
        DATA_SIZE = int(DATA_SIZE.decode())
        q = queue.Queue(maxsize=DATA_SIZE)
        def getAudioData():
            while True:
                frame, _= self.__receiver.recvfrom(MultiCastReceiver.BUFF_SIZE)
                q.put(frame)
                print('[Queue size while loading]...', q.qsize())
        t1 = threading.Thread(target=getAudioData, args=())
        t1.start()
        time.sleep(5)
        DURATION = DATA_SIZE*MultiCastReceiver.CHUNK/44100
        print('[Now Playing]... Data', DATA_SIZE, '[Audio Time]:', DURATION , 'seconds')
        try:
            while True:
                frame = q.get()
                stream.write(frame)
                print('[Queue size while playing]...', q.qsize(), '[Time remaining...]', round(DURATION), 'seconds')
                DURATION -= MultiCastReceiver.CHUNK / 44100
        except:
            self.__receiver.close()
            t1.join()
            print('Audio closed')
            os._exit(1)


if __name__ == "__main__":
     # setup argument parsing 
    parser = ArgumentParser(description="ACapella-NetEng MultiCastReceiver")
    parser.add_argument(
        "-hip",
        "--fromnicip",
        help="Server Socket IP Address",
    )
    parser.add_argument("-gip", "--mcgrpip",
                        help="Server Socket Port Number", default=8080)
    parser.add_argument("-gp", "--mcport",
                        help="Audio File To Be Send")
    args = parser.parse_args()
    receiver = MultiCastReceiver(args.fromnicip, args.mcgrpip, int(args.mcport))
    receiver.mc_recv()
