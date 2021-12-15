import socket, wave, pyaudio, time, math

class MultiCastSender:
    BUFF_SIZE = 65536
    CHUNK = 10*1024

    def __init__(self, host_ip, mcgrp_ip, mc_port):
        self.host_ip = host_ip
        self.mcgrp_ip = mcgrp_ip
        self.mc_port = mc_port

    def mc_send(self):
         # This creates a UDP socket
        sender = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
            proto=socket.IPPROTO_UDP,
            fileno=None,
        )
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, MultiCastSender.BUFF_SIZE)
        # This defines how many hops a multicast datagram can travel. 
        # The IP_MULTICAST_TTL's default value is 1 unless we set it otherwise. 
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        # This defines to which network interface (NIC) is responsible for
        # transmitting the multicast datagram; otherwise, the socket 
        # uses the default interface (ifindex = 1 if loopback is 0)
        # If we wish to transmit the datagram to multiple NICs, we
        # ought to create a socket for each NIC. 
        sender.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.host_ip)
        )
        # This defines a multicast end point, that is a pair
        # (multicast group ip address, send-to port nubmer)
        mcgrp = (self.mcgrp_ip, self.mc_port)
        wf = wave.open("merged.wav")
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    input=True,
                    frames_per_buffer=MultiCastSender.CHUNK)
        data = None
        sample_rate = wf.getframerate()
        DATA_SIZE = math.ceil(wf.getnframes()/MultiCastSender.CHUNK)
        DATA_SIZE = str(DATA_SIZE).encode()
        print('[Sending data size]...', wf.getnframes()/sample_rate)
        sender.sendto(DATA_SIZE, mcgrp)
        cnt = 0
        while True:
                data = wf.readframes(MultiCastSender.CHUNK)
                sender.sendto(data, mcgrp)
                time.sleep(0.001) # Here you can adjust it according to how fast you want to send data keep it > 0
                print(cnt)
                if cnt > (wf.getnframes()/MultiCastSender.CHUNK):
                    break
                cnt += 1
        print('SENT...')
        sender.close()
