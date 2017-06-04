from TabbesBot import TabbesBot
import json

with open('./config/config.json') as f:
  botConfig = json.load(f)

def main():
  bot = TabbesBot()
  bot.run(botConfig[u'token'])

if __name__ == '__main__':
  main()