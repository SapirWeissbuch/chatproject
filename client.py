#============================================================================================== #
# @file     :     client.py
# @purpose:     client class for internet messaging interface.
# @author :     Sapir Weissbuch
# @date     :     27/11/2018
# ============================================================================================== #
# == IMPORTS =================================================================================== #
import socket
import datetime
import threading
import select

# == CONSTANTS ================================================================================= #
protocol = "{chat}###{username}###{hour}###{message}"


# == CLASSES =================================================================================== #
class Client(object):
    """
    client class for internet messaging 
    """
    def __init__(self, host, port):
        self.username = ""
        self.current_chat = ""
        self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # thread for receiving data from server
        self.receive_server_thread = threading.Thread(target=self.receive_from_server)
        self.receive_server_thread.daemon = True

        # lock to protect the socket
        self.socket_lock = threading.Lock()
        # i want to recieve input one thread at a time
        self.input_lock = threading.Lock()

        # connecting the socket
        self.chat_socket.connect((host, port))

    def _input_format(self, command):
        """formatting the input in order to send to server
        arg = command
        type = str
        rtype = str
        """
        if command[0] == '@':
            return protocol.format(chat="&"+self.current_chat+"&", username=self.username, hour=datetime.datetime.now(), message=command)
        else:
            return protocol.format(chat="&&", username=self.username, hour=datetime.datetime.now(), message=command)

    def run(self):
        """
        recieves input from user and sends it to server.
        """
        # getting username until entering one that doesn't exist.
        self.username = self.enter_name()

        # initiating the receving thread
        self.receive_server_thread.start()

        print("Enter messages or commands: ")
        while True:
            with self.input_lock:
                input1 = raw_input("Input: ")
            command = self._input_format(input1)
            with self.socket_lock:
                self.chat_socket.sendall(command)

    def receive_from_server(self):
        """
        receiving messages from the server and printing them
        """
        while True:
            readable, _, _ = select.select([self.chat_socket], [], [])
            if self.chat_socket in readable:
                with self.socket_lock:
                    data = self.chat_socket.recv(5000)
                print(data)

    def enter_name(self):
        """
        getting username from user until it doesn't exist.
        returns the final name.
        :return name
        :rtype str
        """

        name = raw_input("Enter name: ")
        self.chat_socket.sendall(name)
        name_check = self.chat_socket.recv(50000)

        while name_check == "N":
            name = raw_input("Enter name again: ")
            self.chat_socket.sendall(name)
            name_check = self.chat_socket.recv(50000)

        return name

    def __del__(self):
        """
        closing the listening socket.
        """
        self.chat_socket.send("")
        self.chat_socket.close()
        print('disconnected from server')