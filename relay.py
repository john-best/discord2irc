import discordbot
import ircbot
import asyncio
import configparser


class relay():

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('settings.conf');
        self.ircBot = ircbot.IRCBot(self, self.config['settings']['network'], self.config['settings']['port'])
        self.ircBot.init(self.config['settings']['nick'], self.config['settings']['altnick'], self.config['settings']['realname']) 
        self.discordBot = discordbot.DiscordBot(self, self.config['discord']['channel'])
        self.ircchannel = self.config['settings']['channel']
        self.distoken = self.config['discord']['token']

    async def send_to_discord(self, message):
        await self.discordBot.i2d_send(message)

    async def send_to_irc(self, message):
        loop = asyncio.get_event_loop()
        loop.create_task(self.ircBot.d2i_send(message))

    async def set_irc_connected(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.discordBot._irc_connected())

    async def set_discord_connected(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.ircBot.discord_connected())

    async def privmsg_to_irc(self, message):
        loop = asyncio.get_event_loop()
        future = asyncio.Future()
        asyncio.ensure_future(self.ircBot.d2i_send("PRIVMSG {} :{}".format(self.ircchannel, message)))

    def start(self):
        loop = asyncio.get_event_loop()
        self.ircBot.start(loop) 
        self.discordBot.run(self.distoken)
        loop.run_forever()

relayBot = relay()
relayBot.start()
