import socket


class MultiCastSender:
    host_ip = None
    mcgrp_ip = None
    mc_port = None
    file_addr = None
    msg_buf = None

    def __init__(self, host_ip, mcgrp_ip, mc_port, file_addr, msg_buf):
        self.host_ip = host_ip
        self.mcgrp_ip = mcgrp_ip
        self.mc_port = mc_port
        self.file_addr = file_addr
        self.msg_buf = self.read_file(
            file_addr) if msg_buf is None else msg_buf

    def mc_send(self):
        # Creating a UDP socket
        sender = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
            proto=socket.IPPROTO_UDP,
            fileno=None,
        )
        # Create a multi cast Endpoint (group ip addr , send-to port number)
        mcgrp = (self.mcgrp_ip, self.mc_port)

        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sender.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.host_ip)
        )

        sender.sendto(self.msg_buf, mcgrp)

        sender.close()

    def read_file(self, file_addr):
        with open(file_addr, "rb") as merged_file:
            return merged_file.read()
