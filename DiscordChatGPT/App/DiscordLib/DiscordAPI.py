from dotenv import load_dotenv
import discord
import os
from App.OpenAILib.OpenAI import chatgpt_response
import asyncio
load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")


class MyClient(discord.Client):
    def __init__(self, intents):
        self.__is_chatting = False
        super().__init__(intents=intents)

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        if message.author == self.user:# don't respond to themselves
            return
        bot_response = chatgpt_response(prompt=message.content)
        await self.reply_to_message(message, f"{bot_response}")

    async def direct_message(self, user, message):
        await user.send(message)

    async def reply_to_user(self, channel, user, message):
        await channel.send(f"{user.mention} {message}")

    async def reply_to_message(self, message, reply):
        await message.reply(reply)


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
