import discord
import asyncio

# A modified discord client class

class TabbesBot(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
  
  def run(self, *args):
    self.loop.run_until_complete(self.start(*args))
  
  @asyncio.coroutine
  def on_ready(self):
    print("Logged in")
  
  @asyncio.coroutine
  def on_message(self, message):
    print("Recieved messages")