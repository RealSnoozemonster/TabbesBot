import TabbesBot as tb
import json

with open('./config/config.json') as f:
  botConfig = json.load(f)

bot = tb.TabbesBot()

bot.run(botConfig[u'token'])