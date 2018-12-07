#============================================================================================== #
# @file     :     server_classes.py
# @purpose:     classes needed for sever code in chat interface project.
# @author :     Sapir Weissbuch
# @date     :     28/11/2018
# ============================================================================================== #
# == IMPORTS =================================================================================== #
import server_user

# == CONSTANTS ================================================================================= #
PROTOCOL = "[chat]###[username]###[hour]###[message]"
MES_FORMAT = "[time] - [name] - [mes]"


# == CLASSES =================================================================================== #
class Chat(object):
    """
    a class representing a chat.
    """

    def __init__(self, chatname):
        self.chatname = chatname
        self.users = {}
        self.mode = "public" # or private

    def send(self, message):
        """
        receives formatted message and sends it to all members of the chat.
        arg: message
        type: str
        """
        for username in self.users:
            self.users[username].connection_socket.sendall(message)
