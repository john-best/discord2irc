import asyncio
import discord
import re

EMOJI_REGEX = re.compile('<:[^ ]*:[0-9]*>')
MENTION_REGEX = re.compile('<@[0-9]*>')
CHANNEL_REGEX = re.compile('<#[0-9]*>')


class DiscordBot(discord.Client):
    def __init__(self, relay, channel):
        super().__init__()
        self.relay = relay
        self.channel = channel
        print('initializing discord connection')

    async def on_ready(self):
        print('Logged in as %s : %s' % (self.user.name, self.user.id))
        await self.relay.set_discord_connection_status(True)

    async def on_message(self, message):
        if self.relay.irc_connected and message.channel.id == self.channel:
            if message.author == self.user:
                return

            # raw was made for debugging purposes only. now removed by default
            '''if message.content.startswith("!raw"):
                await self.relay.send_to_irc(message.content.split(" ", 1)[1])
            else:'''

            emojis = re.findall(EMOJI_REGEX, message.content)
            for emoji in emojis:
                emoji_name = emoji.split(':')
                message.content = message.content.replace(emoji, ':' + emoji_name[1] + ':', 1)

            mentions = re.findall(MENTION_REGEX, message.content)
            for mention in mentions:
                mention_id = re.sub('[^0-9,.]', '', mention)

                # i don't know if there's a rate limit for this but yeah
                userinfo = await self.get_user_info(mention_id)
                mention_name = userinfo.name
                message.content = message.content.replace(mention, '@' + mention_name, 1)

            channels = re.findall(CHANNEL_REGEX, message.content)
            for channel in channels:
                channel_id = re.sub('[^0-9,.]', '', channel)
                
                channel_name = self.get_channel(channel_id).name
                message.content = message.content.replace(channel, '#' + channel_name, 1)
            
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    await self.relay.privmsg_to_irc("<{}> {}".format(message.author, attachment['url']))
            
            if message.content != '':
                await self.relay.privmsg_to_irc("<{}> {}".format(message.author, message.content))

    async def i2d_send(self, message):
        await self.send(message)

    async def send(self, message):
        await self.send_message(self.get_channel(self.channel), message)

    async def send_embed(self, title, description, color):
        embed = discord.Embed(title=title, description=description, color=color)
        await self.send_message(self.get_channel(self.channel), embed=embed)

