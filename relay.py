import discordbot
import ircbot
import asyncio

class relay():

    def __init__(self):
        self.ircBot = ircbot.IRCBot(self, 'irc.network.org', 6667)
        self.discordBot = discordbot.DiscordBot(self)

    async def send_to_discord(self, message):
        await self.discordBot.i2d_send(message)

    async def send_to_irc(self, message):
        loop = asyncio.get_event_loop()
        future = asyncio.Future()
        asyncio.ensure_future(self.ircBot.d2i_send(message))

    async def set_discord_connected(self):
        loop = asyncio.get_event_loop()
        future = asyncio.Future()
        asyncio.ensure_future(self.ircBot.disc_connected())

    def start(self):
        loop = asyncio.get_event_loop()
        self.ircBot.start(loop) 
        self.discordBot.run('token')
        #loop.run_until_complete((self.discordBot.start()))
        loop.run_forever()

relayBot = relay()
relayBot.start()
