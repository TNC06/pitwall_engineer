import socket

class Receiver:

    def __init__(self):
        self.ip = "192.168.1.125"
        self.port = 20777
        self.socket = None
    
    def start(self):
        """
        Create and bind the UDP socket.
        """
        if self.socket is None:
            udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            udp_socket.bind((self.ip, self.port))
            self.socket = udp_socket
    
    def receive(self):
        """
        Wait for a single UDP packet.
        """
        if self.socket is None:
            self.start()
        
        data, _ = self.socket.recvfrom(2048)
        return data
    
    def stop(self):
        """
        Close the socket.
        """
        # Close socket if it exists
        if self.socket:
            self.socket.close()
            self.socket = None