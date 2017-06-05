import discord
import asyncio
import status
import sqlite3
import spamometer

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
    yield from self.change_presence(game=discord.Game(name='=help for help'))
  
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
        warn_msg = yield from self.send_message(message.channel, self.db_cursor.fetchone()[2])
        yield from asyncio.sleep(3)
        yield from self.delete_message(warn_msg)
    
    # No-ascii detection
    self.db_cursor.execute("SELECT * FROM noascii_channels WHERE serverid = '" + message.server.id + "'")
    noascii_channels = []
    for rec in self.db_cursor.fetchall():
      noascii_channels.append(rec[1])
    if (message.channel.id in noascii_channels):
      if (spamometer.check(message.content)[0] < -15 and spamometer.check(message.content)[1]):
        yield from self.delete_message(message)
        self.db_cursor.execute("SELECT * FROM servers WHERE serverid = '" + message.server.id + "'")
        warn_msg = yield from self.send_message(message.channel, self.db_cursor.fetchone()[3])
        yield from asyncio.sleep(3)
        yield from self.delete_message(warn_msg)
    
    # Process command - hello
    if   (message.content.startswith(self.prefix + 'hello')):
      self.out.Log("'=hello' used in server " + message.server.id + " in channel " + message.channel.id + " by user " + message.author.id + ".")
      yield from self.send_message(message.channel, 'Hello, ' + message.author.name + '.')
    
    # Process command - nolink
    elif (message.content.startswith(self.prefix + 'nolink')):
      cmd_arg = message.content.replace(self.prefix + 'nolink ', '')
      if (cmd_arg == 'enable'):
        self.db_cursor.execute('INSERT INTO nolink_channels (serverid, channelid) VALUES(?, ?)', (message.server.id, message.channel.id))
        self.db_connection.commit()
        self.out.Log("Channel " + message.channel.id + " added to no-link censoring!")
        yield from self.send_message(message.channel, '**[NO-LINK]** Channel has been added to no-link censoring channels')
      elif (cmd_arg == 'disable'):
        try:
          self.db_cursor.execute("DELETE FROM nolink_channels WHERE channelid = '" + message.channel.id + "'")
          self.db_connection.commit()
          self.out.Log("Channel " + message.channel.id + " removed from no-link censoring!")
        except:
          self.out.Error("Channel " + message.channel.id + " could not be removed from no-link censoring! Maybe it did not exist!")
        yield from self.send_message(message.channel, '**[NO-LINK]** Channel has been removed from no-link censoring channels')                
      elif (cmd_arg.startswith('setmsg ')):
        warnmsg = cmd_arg.replace('setmsg ', '')
        self.db_cursor.execute("UPDATE servers SET nolinkmsg = '" + warnmsg + "' WHERE serverid = '" + message.server.id + "'")
        self.db_connection.commit()
        self.out.Log('Nolinkmsg updated for server ' + message.server.name)
        yield from self.send_message(message.channel, '**[NO-LINK]** Warn message for nolink updated!')
      else :
        yield from self.send_message(message.channel, '**[NO-LINK]** Unknown command!')
    
    # Process command - noascii
    elif (message.content.startswith(self.prefix + 'noascii')):
      cmd_arg = message.content.replace(self.prefix + 'noascii ', '')
      if (cmd_arg == 'enable'):
        self.db_cursor.execute('INSERT INTO noascii_channels (serverid, channelid) VALUES(?, ?)', (message.server.id, message.channel.id))
        self.db_connection.commit()
        self.out.Log("Channel " + message.channel.id + " added to no-ascii censoring!")
        yield from self.send_message(message.channel, '**[NO-ASCII]** Channel has been added to no-link censoring channels')
      elif (cmd_arg == 'disable'):
        try:
          self.db_cursor.execute("DELETE FROM noascii_channels WHERE channelid = '" + message.channel.id + "'")
          self.db_connection.commit()
          self.out.Log("Channel " + message.channel.id + " removed from no-ascii censoring!")
        except:
          self.out.Error("Channel " + message.channel.id + " could not be removed from no-ascii censoring! Maybe it did not exist!")
        yield from self.send_message(message.channel, '**[NO-ASCII]** Channel has been removed from no-ascii censoring channels')
      elif (cmd_arg.startswith('setmsg ')):
        warnmsg = cmd_arg.replace('setmsg ', '')
        self.db_cursor.execute("UPDATE servers SET noasciimsg = '" + warnmsg + "' WHERE serverid = '" + message.server.id + "'")
        self.db_connection.commit()
        self.out.Log('Noasciimsg updated for server ' + message.server.name)
        yield from self.send_message(message.channel, '**[NO-ASCII]** Warn message for nolink updated!')
      else :
        yield from self.send_message(message.channel, '**[NO-ASCII]** Unknown command!')
    
    # Process command - invite
    elif (message.content.startswith(self.prefix + 'invite')):
      invite_embed = discord.Embed(title = 'TabBot Invite', description = 'Invite TabBot to your server : https://discordapp.com/oauth2/authorize?client_id=320580918479683584&scope=bot&permissions=66186303', color = 0x4286f4)
      yield from self.send_message(message.channel, embed = invite_embed)
    
    # Process command - help
    elif (message.content.startswith(self.prefix + 'help')):
      cmd_arg = message.content.replace('help ', '')
      if   ('help' in cmd_arg):
        msg_embed = discord.Embed(title = 'TabBot Help', description = 'use `=help <command>` to get help about a specific command', color = 0xcb42f4)
        msg_embed.add_field(name = '=nolink', value = 'Censors links in the channel the command is used in! Look at =help nolink for usage of this command', inline = True)
        msg_embed.add_field(name = '=noascii', value = 'Censors ASCII-art spam in the channel the command is used in! Look at =help noascii for usage of this command', inline = True)
        msg_embed.add_field(name = '=invite', value = 'Gives you a link that you can use to invite TabBot into your server!', inline = True)
        msg_embed.add_field(name = '=help', value = 'Gives you information about the commands the bot offers! use `=help <command>` for help related to a perticular command', inline = True)
        yield from self.send_message(message.channel, embed = msg_embed)
      elif ('invite' in cmd_arg):
        msg_embed = discord.Embed(title = 'TabBot Help : =invite', description = 'Gives you a link that you can use to invite TabBot to your server!', color = 0xcb42f4)
        yield from self.send_message(message.channel, embed = msg_embed)
      elif ('nolink' in cmd_arg):
        msg_embed = discord.Embed(title = 'TabBot Help : =nolink', description = 'Censors links in the channel the command is used in!', color = 0xcb42f4)
        msg_embed.add_field(name = '=nolink enable', value = 'Enables no-link censoring in the perticular channel the command is used in', inline = True)
        msg_embed.add_field(name = '=nolink disable', value = 'Disables no-link censoring in the perticular channel the command is used in', inline = True)
        msg_embed.add_field(name = '=nolink setmsg <msg>', value = 'Sets custom warn message for when the bot deletes messages with links', inline = True)
        yield from self.send_message(message.channel, embed = msg_embed)
      elif ('noascii' in cmd_arg):
        msg_embed = discord.Embed(title = 'TabBot Help : =noascii', description = 'Censors ASCII-art spam in the channel the command is used in!', color = 0xcb42f4)
        msg_embed.add_field(name = '=noascii enable', value = 'Enables no-ascii censoring in the perticular channel the command is used in', inline = True)
        msg_embed.add_field(name = '=noascii disable', value = 'Disables no-ascii censoring in the perticular channel the command is used in', inline = True)
        msg_embed.add_field(name = '=noascii setmsg <msg>', value = 'Sets custom warn message for when the bot deletes messages with ASCII-art spam', inline = True)
        yield from self.send_message(message.channel, embed = msg_embed)
      else :
        msg_embed = discord.Embed(title = 'TabBot Help', description = 'ERROR: Failed to fetch help for this command', color = 0xcb42f4)
        yield from self.send_message(message.channel, embed = msg_embed)