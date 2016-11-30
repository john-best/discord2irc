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

    def data_received(self, data):
        data = data.decode()
        self.handle_data(data)

    def connection_lost(self, exc):
        print('IRC: Connection to the server has been lost.')
        self.relay_to_discord("IRC: Connection to the server has been lost.")

    def handle_data(self, data):
        # the first message received means a connection was successful
        # commence login operations
        if self.connected is False:
            self.login()
            self.irc_connected()
            self.connected = True

        #TODO: actually handle login response
        # hacky ping/pong response for now...

        message = format(data)

        print(message)

        if self.discord_connected:
            self.relay_to_discord(message)

        if message.startswith("PING"):
            self.send("PONG :" + message.split(":",1)[1])
    
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
        

