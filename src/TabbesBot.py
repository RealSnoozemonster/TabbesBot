import discord
import asyncio
import status
import sqlite3

# A modified discord client class

class TabbesBot(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.prefix = kwargs.get('prefix') if (kwargs.get('prefix') != None) else '='
    self.out = status.out()
    self.db_connection = sqlite3.connect('./db/main_database.db')
    self.out.Log("Successfully connected to local database './db/main_database.db' using SQLite3")
    self.db_cursor = self.db_connection.cursor()
  
  def run(self, *args):
    self.db_cursor.execute('CREATE TABLE IF NOT EXISTS servers(serverid TEXT, servername TEXT)')
    self.loop.run_until_complete(self.start(*args))
  
  @asyncio.coroutine
  def on_ready(self):
    self.out.Success("Client Ready! Logged in as " + self.user.id)
  
  @asyncio.coroutine
  def on_server_join(server):
    pass
  
  @asyncio.coroutine
  def on_server_update(before, after):
    pass
  
  @asyncio.coroutine
  def on_server_remove(server):
    pass
  
  @asyncio.coroutine
  def on_message(self, message):
    if   (message.content.startswith(self.prefix + 'hello')):
      self.out.Log("'=hello' used in server " + message.server.id + " in channel " + message.channel.id + " by user " + message.author.id + ".")
      yield from self.send_message(message.channel, 'Hello, ' + message.author.name + '.')
    #elif (message.content.startswith(self.prefix + 'help')):