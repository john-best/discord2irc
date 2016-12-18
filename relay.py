import discordbot
import ircbot
import asyncio
import configparser
import logging


class relay():

    def __init__(self):
        
        self.config = configparser.ConfigParser() 
        self.config.read('settings.conf')

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)

        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)


        self.ircchannel = self.config['irc']['channel']        
        self.distoken = self.config['discord']['token'] 
        self.discordBot = discordbot.DiscordBot(self, self.config['discord']['channel'])
        
        self.ircBot = ircbot.IRCBot(self, self.config['irc']['network'], \
                self.config['irc']['port'])

        self.ircBot.init(self.config['irc']['nick'], \
                self.config['irc']['altnick'], \
                self.config['irc']['realname'], \
                self.ircchannel) 

    async def send_to_discord(self, message):
        await self.discordBot.i2d_send(message)

    async def send_to_irc(self, message):
        loop = asyncio.get_event_loop()
        loop.create_task(self.ircBot.d2i_send(message))

    async def set_irc_connection_status(self, status):
        loop = asyncio.get_event_loop()
        loop.create_task(self.discordBot.set_irc_connection_status(status))

    async def set_discord_connection_status(self, status):
        loop = asyncio.get_event_loop()
        loop.create_task(self.ircBot.set_discord_connection_status(status))

    async def privmsg_to_irc(self, message):
        loop = asyncio.get_event_loop()
        loop.create_task(self.ircBot.irc_privmsg(self.ircchannel, message))

    def start(self):
        loop = asyncio.get_event_loop()
        self.ircBot.start(loop) 
        self.discordBot.run(self.distoken)
        loop.run_forever()


if __name__ == '__main__':
    relayBot = relay()
    relayBot.start()
