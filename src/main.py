from TabbesBot import TabbesBot
import json
import atexit

with open('./config/config.json') as f:
  botConfig = json.load(f)

def main():
  bot = TabbesBot()
  atexit.register(bot.cleanup)
  bot.run(botConfig[u'token'])

if __name__ == '__main__':
  main()