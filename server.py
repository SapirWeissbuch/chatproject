#============================================================================================== #
# @file     :     server_classes.py
# @purpose:     classes needed for sever code in chat interface project.
# @author :     Sapir Weissbuch
# @date     :     28/11/2018
# ============================================================================================== #
# == IMPORTS =================================================================================== #
import socket
import select
import server_chat
import server_user

# == CONSTANTS ================================================================================= #
PROTOCOL = "###[chat]###[username]###[hour]###[message]"
MES_FORMAT = "[{time}] - [{name}] - [{mes}]"


# == CLASSES =================================================================================== #


class Server(object):
    """
    server class for chat interface. 
    """
    def __init__(self):
        # chat name: chat object
        self.chats = {}
        # user name: user object
        self.users = {}
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self, host, port):
        """
        connecting users and receiving messages from them.
        arg: host
        type: str
        arg: port
        type: str
        """
        self.listening_socket.bind((host, port))
        self.listening_socket.listen(10)
        self.sockets_list = [self.listening_socket]

        while True:
            readable, _, _ = select.select(self.sockets_list, [], [])
            for sock in readable:
                if self.listening_socket is sock:
                    conn, _ = self.listening_socket.accept()
                    self.sockets_list.append(conn)
                    while True:
                        name = conn.recv(2 ** 16)
                        if name in self.users:
                            conn.sendall("N")
                        else:
                            conn.sendall("Y")
                            self.users.update({name: server_user.User(name, conn)})
                            break

                else:
                    try:
                        user_input = sock.recv(2**16)
                        self.user_input_processor(user_input)

                    except:
                        self.user_disconnected(sock)

    def user_disconnected(self, sock):
        """
        when user disconnected searches for the user and deletes it from server and chat lists.
        :param sock:
        type: socket object
        """
        to_delete_username = ""
        for username, userobject in self.users.iteritems():
            # checks if this is the disconnected socket:
            if userobject.connection_socket == sock:
                to_delete_username = username

        # deleting user from current chat if exists:
        if to_delete_username != "":
            if self.users[to_delete_username].current_chat is not None:
                del self.users[to_delete_username].current_chat.users[to_delete_username]
            # deleting user from server's user list:
            del self.users[to_delete_username]
            self.sockets_list.remove(sock)

        sock.close()
        print "disconnected from " + to_delete_username

    def user_input_processor(self, user_input):
        """
        gets user input from run and calls the required functions
        arg: user_input
        type: str
        """
        input_list = user_input.split("###")
        username = input_list[1]
        message = input_list[3]
        if message[0] == '@':
            self.command_processor(input_list)
        else:
            # it means that this is a message.

            if self.users[username].current_chat is None:
                self.users[username].connection_socket.sendall("\nNot connected to a chat")
            else:
                final_message = MES_FORMAT.format(name=username, time=input_list[2], mes=message)
                self.users[username].current_chat.send(final_message)

    def command_processor(self, input_list):
        """
        gets a command (@join/@leave/@contact/@create) from user and excecutes it using funcitons.
        arg: input_list
        type: list
        arg: current_username
        type: str
        """
        user_name = input_list[1]
        message = input_list[3]
        command_end_index = message.find(" ")
        # extraction of the command itself (join/leave/contact/create)
        if command_end_index == -1:
            command = message[1:]
        else:
            command = message[1:command_end_index]
        # extraction of the commands details (name of chat or contact or None)
        details = message[command_end_index+1:]
        # a dictionary with the possible commands and the matching functions:
        if command == "join":
            self.users[user_name].join(self.chats[details])
        elif command == "leave":
            self.users[user_name].leave()
            self.del_empty_chats
        elif command == "contact":
            self.users[user_name].contact(self.users[details])
        elif command == "create":
            self.create_chat(details, self.users[user_name])
        elif command == "showusers":
            self.show_users(user_name)
        elif command == "showchats":
            self.show_chats(user_name)

        """
        meaning of commands:
        @join: joining a public chat
        @leave: leaving a chat
        @contact: starting a private chat with a user
        @create: creating a new public cha
        """

    def create_chat(self, chatname, first_user):
        """
        creates a chat with the first user in it.
        :param chatname: type: str
        :param first_user: type: user object
        :return:
        """
        if first_user.current_chat is not None:
            self.connection_socket.sendall("Can't start a chat while already in a chat.")
        else:
            new_chat = server_chat.Chat(chatname)
            self.chats.update({chatname: new_chat})
            first_user.join(new_chat)

    def del_empty_chats(self):
            """
            checks for empty chats and deletes them.
            """
            for chatname,chat_object in self.chats.iteritems():
                if len(chat_object.users) == 0:
                    # deleting the chat from the servers chats list
                    del self.chats[chatname]

    def show_users(self, username):
        """
        sends the list of people to the user.
        :param username:
        :type str:
        :return:
        """
        users_list = ["{"+i+"}" for i in self.users.iterkeys() if i != username and self.users[i].current_chat is None]
        output = " ".join(users_list)
        if output == "":
            self.users[username].connection_socket.sendall("No users")
        else:
            self.users[username].connection_socket.sendall(output)

    def show_chats(self, username):
        """
        sends the list of chats to the user.
        :param username:
        :type str:
        :return:
        """
        chats_list = ["{"+i+"}" for i in self.chats.iterkeys() if self.chats[i].mode == "public"]
        output = " ".join(chats_list)
        if output == "":
            self.users[username].connection_socket.sendall("No chats")
        else:
            self.users[username].connection_socket.sendall(output)


    def __del__(self):
        """
        closing the listening socket.
        """
        self.listening_socket.close()
        print "server socket disconnected"

