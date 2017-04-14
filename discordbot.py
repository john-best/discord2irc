import asyncio
import discord

class DiscordBot(discord.Client):
    def __init__(self, relay, channel):
        super().__init__()
        self.relay = relay
        self.channel = channel
        self.irc_connected = False
        print('initializing discord connection')

    async def on_ready(self):
        print('Logged in as %s : %s' % (self.user.name, self.user.id))
        await self.relay.set_discord_connection_status(True)

    async def on_message(self, message):
        if self.irc_connected and message.channel == self.get_channel(self.channel):
            if message.author == self.user:
                return


            # raw was made for debugging purposes only. now removed by default
            '''if message.content.startswith("!raw"):
                await self.relay.send_to_irc(message.content.split(" ", 1)[1])
            else:'''

            await self.relay.privmsg_to_irc("<{}> {}".format(message.author, message.content))

    async def i2d_send(self, message):
         await self.send(message)

    async def set_irc_connection_status(self, status):
        self.irc_connected = status

    async def send(self, message):
        await self.send_message(self.get_channel(self.channel), message)

