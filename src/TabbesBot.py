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
    self.default_msg_nolink  = kwargs.get('nolink_msg' ) if (kwargs.get('nolink_msg' ) != None) else 'Links and invites are not allowed in this channel!'
    self.default_msg_noascii = kwargs.get('noascii_msg') if (kwargs.get('noascii_msg') != None) else 'Ascii and emoji spam are not allowed in this channel'
    self.db_connection = sqlite3.connect('./db/main_database.db')
    self.out.Log("Successfully connected to local database './db/main_database.db' using SQLite3")
    self.db_cursor = self.db_connection.cursor()
  
  def run(self, *args):
    self.out.Log("Setting up database")
    self.db_cursor.execute('CREATE TABLE IF NOT EXISTS servers(serverid TEXT, servername TEXT, nolinkmsg TEXT, noasciimsg TEXT)')
    self.db_connection.commit()
    self.out.Success("Database initialise complete")
    self.out.Log("Starting discord client")
    self.loop.run_until_complete(self.start(*args))
  
  def close(self, *args):
    self.db_cursor.close()
    self.db_connection.close()
  
  @asyncio.coroutine
  def on_ready(self):
    self.out.Success("Client ready! Logged in as " + self.user.id)
  
  @asyncio.coroutine
  def on_server_join(self, server):
    self.db_cursor.execute('INSERT INTO servers (serverid, servername, nolinkmsg, noasciimsg) VALUES(?, ?, ?, ?)',
                           (server.id, server.name, self.default_msg_nolink, self.default_msg_noascii))
    self.db_connection.commit()
  
  @asyncio.coroutine
  def on_server_update(self, before, after):
    self.db_cursor.execute("UPDATE servers SET servername = '" + after.name + "'WHERE serverid = '" + after.id + "'")
    self.db_connection.commit()
  
  @asyncio.coroutine
  def on_server_remove(self, server):
    self.db_cursor.execute("DELETE FROM servers WHERE serverid = '" + server.id + "'")
    self.db_connection.commit()
  
  @asyncio.coroutine
  def on_message(self, message):
    if   (message.content.startswith(self.prefix + 'hello')):
      self.out.Log("'=hello' used in server " + message.server.id + " in channel " + message.channel.id + " by user " + message.author.id + ".")
      yield from self.send_message(message.channel, 'Hello, ' + message.author.name + '.')
    #elif (message.content.startswith(self.prefix + 'help')):