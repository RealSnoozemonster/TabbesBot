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
    self.db_cursor.execute('CREATE TABLE IF NOT EXISTS nolink_channels(serverid TEXT, channelid TEXT)')
    self.db_connection.commit()
    self.db_cursor.execute('CREATE TABLE IF NOT EXISTS noascii_channels(serverid TEXT, channelid TEXT)')
    self.db_connection.commit()  
    self.out.Success("Database initialise complete")
    self.out.Log("Starting discord client")
    self.loop.run_until_complete(self.start(*args))
  
  def cleanup(self, *args):
    self.db_cursor.close()
    self.db_connection.close()
    self.out.Success("Clean up complete! Shuting down!")
  
  @asyncio.coroutine
  def on_ready(self):
    self.out.Success("Client ready! Logged in as " + self.user.id)
  
  @asyncio.coroutine
  def on_server_join(self, server):
    self.db_cursor.execute('INSERT INTO servers (serverid, servername, nolinkmsg, noasciimsg) VALUES(?, ?, ?, ?)',
                           (server.id, server.name, self.default_msg_nolink, self.default_msg_noascii))
    self.db_connection.commit()
    self.out.Success("Successfully joined server : " + server.name)
      
  @asyncio.coroutine
  def on_server_update(self, before, after):
    self.db_cursor.execute("UPDATE servers SET servername = '" + after.name + "'WHERE serverid = '" + after.id + "'")
    self.db_connection.commit()
    self.out.Log("Updated server " + before.name + " to " + after.name)
  
  @asyncio.coroutine
  def on_server_remove(self, server):
    self.db_cursor.execute("DELETE FROM servers WHERE serverid = '" + server.id + "'")
    self.db_connection.commit()
    self.out.Success("Successfully left server : " + server.name)
  
  @asyncio.coroutine
  def on_message(self, message):
    # No-Link detection
    self.db_cursor.execute("SELECT * FROM nolink_channels WHERE serverid = '" + message.server.id + "'")
    nolink_channels = []
    for rec in self.db_cursor.fetchall():
      nolink_channels.append(rec[1])
    if (message.channel.id in nolink_channels):
      if ('http://' in message.content or 'https://' in message.content or 'discord.gg/' in message.content):
        yield from self.delete_message(message)
        self.db_cursor.execute("SELECT * FROM servers WHERE serverid = '" + message.server.id + "'")
        yield from self.send_message(message.channel, self.db_cursor.fetchone()[2])
    
    # Process commands - hello
    if   (message.content.startswith(self.prefix + 'hello')):
      self.out.Log("'=hello' used in server " + message.server.id + " in channel " + message.channel.id + " by user " + message.author.id + ".")
      yield from self.send_message(message.channel, 'Hello, ' + message.author.name + '.')
    
    # Process commands - nolink
    elif (message.content.startswith(self.prefix + 'nolink ')):
      cmd_arg = message.content.replace(self.prefix + 'nolink ')
      if (cmd_arg == 'true'):
        self.db_cursor.execute('INSERT INTO nolink_channels (serverid, channelid) VALUES(?, ?)', (message.server.id, message.channel.id))
        self.db_connection.commit()
        self.out.Log("Channel " + message.channel.id + " added to no-link censoring!")
        yield from self.send_message(message.channel, '**[NO-LINK]** Channel has been added to no-link censoring channels')
      elif (cmd_arg == 'false'):
        try:
          self.db_cursor.execute("DELETE FROM nolink_channels WHERE channelid = '" + message.channel.id + "'")
          self.db_connection.commit()
          self.out.Log("Channel " + message.channel.id + " removed from no-link censoring!")
        except:
          self.out.Error("Channel " + message.channel.id + " could not be removed from no-link censoring! Maybe it did not exist!")
        yield from self.send_message(message.channel, '**[NO-LINK]** Channel has been removed from no-link censoring channels')                
      else :
        yield from self.send_message(message.channel, '**[NO-LINK]** Unknown command!')
    
    #elif (message.content.startswith(self.prefix + 'help')):