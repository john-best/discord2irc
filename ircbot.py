import asyncio
import functools
import re

class IRCProtocol(asyncio.Protocol):

    def __init__(self, relay, loop, nick, altnick, user, real):
        self.relay = relay
        self.loop = loop
        self.connected = False
        self.discord_connected = False

        self.nick = nick
        self.user = user
        self.real = real
        

    def connection_made(self, transport):
        print('IRC: Connection made!')
        self.transport = transport
        self.login()
        self.irc_connected()

    def data_received(self, data):
        data = data.decode()
        self.handle_data(data)

    def connection_lost(self, exc):
        print('IRC: Connection to the server has been lost.')
        self.relay_to_discord("IRC: Connection to the server has been lost.")

    def handle_data(self, data):
        message = format(data)


        # unfortunately data comes in blocks sometimes, which means this method
        # will not work unless we can set up some kind of list that handles
        # data split by \r\n per element while also being able to receive more
        # data by appending it to the end of the list
        # TODO: ^

        if not message.startswith(":"):
            self.handle_server_message(message)

        # so :nick!user@host COMMAND :text is what irc sends us
        # if command is a number e.g. 001-999 then it's a server rpl response

        elif (message.split()[1].isdigit()):
            self.handle_server_rpl(message.split()[1])
        # otherwise it's a message from an irc service or user
        else:    
            if self.discord_connected:
                self.relay_to_discord(message)
                print("recv: {}".format(message))
            else:
                # TODO: handle messages when connected to IRC but not discord
                pass
   
    def handle_server_message(self, message):

        # TODO: need a better way to handle server messages -- HIGH PRIORITY

        if message.startswith("PING"):
            print("PING recv: {}".format(message))
            self.send("PONG :" + message.split(":",1)[1])
        
        else:
            print("IRC: Received unknown message from server: {}".format(message))

    def handle_server_rpl(self, rpl):
        # TODO: need better way of handling rpl codes
        if value_rpl == '001':
            print("RPL_WELCOME Received.")
           
    
    def send(self, message):
        print("IRC: Sending: %s" % (message))
        self.transport.write("{}\r\n".format(message).encode())

    def relay_to_discord(self, message):
        loop = asyncio.get_event_loop()
        loop.create_task(self.relay.send_to_discord(message))

    def irc_connected(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.relay.set_irc_connected())

    def login(self):
        self.send("NICK %s" % (self.nick))
        self.send("USER %s 0 * :%s" % (self.user, self.real))

class IRCBot():
    def __init__(self, relay, server, port):
        print('IRC Bot initializing')
        self.relay = relay
        self.server = server
        self.port = port
        self.protocol = None

    def init(self, nick, altnick, real):
        self.nick = nick
        self.altnick = altnick
        self.user = nick
        self.real = real

    async def d2i_send(self, message):
        self.protocol.send(message)

    async def discord_connected(self):
        self.protocol.discord_connected = True

    def start(self, loop):
        ircProto = IRCProtocol(self.relay, loop, self.nick, self.altnick, self.user, self.real)
        connection = loop.create_connection(lambda: ircProto, self.server, self.port)
        self.protocol = ircProto
        loop.run_until_complete(connection)
        

