import asyncio
import re
import logging

MESSAGE_REGEX = re.compile(":(?P<nick>[^ ]*)!(?P<user>[^@]*)(?P<address>[^ ]*)\s(?P<command>[^ ]*)\s(?P<target>[^ ]*)\s:(?P<text>.*)")

class IRCProtocol(asyncio.Protocol):

    def __init__(self, relay, loop, nick, altnick, user, real, channel):
        self.relay = relay
        self.loop = loop
        self.irc_connected = False
        self.discord_connected = False
        self.nick = nick
        self.user = user
        self.real = real
        self.channel = channel

    def connection_made(self, transport):
        logging.info('IRC: Connection made!')
        self.transport = transport
        self.login()
        self.irc_connected = True
        self.set_connection_status(True)

    def data_received(self, data):
        data = data.decode()
        self.handle_data(data)

    def connection_lost(self, exc):
        self.irc_connected = False
        self.set_connection_status(False)
        logging.info('IRC: Connection to the server has been lost.')
        if self.discord_connected:
            self.relay_to_discord("IRC: Connection to the server has been lost.")

    def handle_data(self, data):

        messages = format(data).split('\r\n')

        # might have some major lag i'm not sure if this is the best solution

        for message in messages:

            if message == '':
                break

            # actually servers sometimes send messages with : so...
            # TODO: fix this

            if not message.startswith(":"):
                self.handle_server_message(message)

            # the numerics only exist at the second 'word'
            elif len(message.split()) > 2 and message.split()[1].isdigit():
                self.handle_server_rpl(message.split()[1])

            # otherwise it's a message from something else
            else:    
                self.handle_normal_message(message)

    def handle_normal_message(self, message):

        match = re.match(MESSAGE_REGEX, message)

        # TODO: logging module soon(tm)
        if not match:
            logging.debug("Unhandled message sent {}".format(message))

        else:
            nick = match.group('nick')
            user = match.group('user')
            host = match.group('address')
            command = match.group('command').lower()
            target = match.group('target')
            text = match.group('text')

            message_ = None

            if target == self.nick:
                # let's not support private messages for now
                return

            # TODO: there must be a fancier way of handling this

            if command == 'notice':
                message_ = "-{}- {}".format(nick, text)

            elif command == 'privmsg':
                message_ = "<{}> {}".format(nick, text)

            if self.discord_connected and message_ is not None:
                self.relay_to_discord(message_)

            else:
                pass
                # TODO: handle messages when not connected to discord
                # probably put them in a list for keeping until reconnected
   
    def handle_server_message(self, message):

        # TODO: need a better way to handle server messages -- HIGH PRIORITY

        if message.startswith("PING"):
            logging.debug("PING recv: {}".format(message))
            self.send("PONG :" + message.split(":",1)[1])
        
        else:
            logging.debug("IRC: Received unknown message from server: {}".format(message))

    def handle_server_rpl(self, rpl):

        # TODO: need better way of handling rpl codes
        
        if rpl == '001':
            logging.debug("RPL_WELCOME Received")
            if self.discord_connected:
                self.relay_to_discord("Connected to IRC!")

        # end of motd or no motd; join channels
        if rpl == '376' or rpl == '422':
            if self.discord_connected:
                self.relay_to_discord("Joining channel: {}".format(self.channel))
            self.join(self.channel)

           
    def join(self, target):
        self.send("JOIN {}".format(target))
    
    def send(self, message):
        self.transport.write("{}\r\n".format(message).encode())

    def privmsg(self, target, message):
        self.send("PRIVMSG {} :{}".format(target, message))

    def relay_to_discord(self, message):
        loop = asyncio.get_event_loop()
        loop.create_task(self.relay.send_to_discord(message))

    def set_connection_status(self, status):
            loop = asyncio.get_event_loop()
            loop.create_task(self.relay.set_irc_connection_status(status))

    def set_discord_connection_status(self, status):
        if self.irc_connected and status:
            self.privmsg(self.channel, "Connected to Discord!")
        elif self.irc_connected and not status:
            self.privmsg(self.channel, "Disconnected from Discord")
        self.discord_connected = status

    def login(self):
        self.send("NICK {}".format(self.nick))
        self.send("USER {} 0 * :{}".format(self.user, self.real))

class IRCBot():
    def __init__(self, relay, server, port):
        logging.info('IRC Bot initializing')
        self.relay = relay
        self.server = server
        self.port = port
        self.protocol = None

    def init(self, nick, altnick, real, channel):
        self.nick = nick
        self.altnick = altnick
        self.user = nick
        self.real = real
        self.channel = channel

    async def irc_privmsg(self, target, message):
        self.protocol.privmsg(target, message)
    
    async def d2i_send(self, message):
        self.protocol.send(message)

    async def set_discord_connection_status(self, status):
        self.protocol.set_discord_connection_status(status)

    def start(self, loop):
        ircProto = IRCProtocol(self.relay, loop, self.nick, self.altnick, self.user, self.real, self.channel)
        connection = loop.create_connection(lambda: ircProto, self.server, self.port)
        self.protocol = ircProto
        loop.run_until_complete(connection)
        

