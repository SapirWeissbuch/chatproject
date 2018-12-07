#============================================================================================== #
# @file     :     server_classes.py
# @purpose:     classes needed for sever code in chat interface project.
# @author :     Sapir Weissbuch
# @date     :     28/11/2018
# ============================================================================================== #
# == IMPORTS =================================================================================== #
import server_chat

# == CONSTANTS ================================================================================= #
PROTOCOL = "###[chat]###[username]###[hour]###[message]"
MES_FORMAT = "[time] - [name] - [mes]"


# == CLASSES =================================================================================== #
class User(object):
    """
    a class representing the user.
    """

    def __init__(self, username, conn):
        self.username = username
        self.current_chat = None
        self.connection_socket = conn

    def join(self, chat):
        """
        adding the user to a chat.
        arg: chat
        type: dict object
        """
        if self.current_chat is not None:
            self.connection_socket.sendall("Can't start a chat while already in a chat.")
        else:
            # add chat to user
            self.current_chat = chat
            # add user to chat
            chat.users.update({self.username: self})

    def contact(self, second_user):
        """
        creating a private chat with second_user
        :param second_user:
        type: user object
        :return:
        """
        if self.current_chat is not None:
            self.connection_socket.sendall("Can't start a chat while already in a chat.")
        elif second_user.current_chat is not None:
            self.connection_socket.sendall("User not available for chat.")
        else:
            self.current_chat = server_chat.Chat("&"+second_user.username+"&")
            self.current_chat.mode = "private"
            second_user.current_chat = self.current_chat
            second_user.connection_socket.sendall("Now connected to " + self.username)
            self.current_chat.users.update({self.username: self, second_user.username: second_user})

    def leave(self):
        """
        leaving current chat
        :return:
        """
        del self.current_chat.users[self.username]
        self.current_chat = None

    def __del__(self):
        """
        closing user sockets when it is deleted
        """
        self.connection_socket.close()
        print "disconnected from []".format(self.username)