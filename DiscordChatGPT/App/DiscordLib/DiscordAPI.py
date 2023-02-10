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
        # don't respond to themselves
        if message.author == self.user:
            return
        # all message forward to OpenAI
        bot_response = chatgpt_response(prompt=message.content)
        # try:
        #     bot_response = await asyncio.wait_for(chatgpt_response(prompt=message.content), timeout=1.0)
        # except asyncio.TimeoutError:
        #     bot_response = "Sorry, OpenAI Sever is too busy, my brain can't reply you. 对不起，OpenAI服务器太忙了，我的智商无法回答你。"
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
