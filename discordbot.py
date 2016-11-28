import asyncio
import discord

class DiscordBot(discord.Client):
    def __init__(self, relay):
        super().__init__()
        self.relay = relay
        print('initializing discord bot')

    async def on_ready(self):
        print('Logged in as %s : %s' % (self.user.name, self.user.id))
        await self.relay.set_discord_connected()

    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.relay.send_to_irc(message.content)

    async def i2d_send(self, message):
         await self.send(message)

    async def send(self, message):
        print('Sending message to discord: {}'.format(message))
        await self.send_message(self.get_channel('channel_id'), message)

