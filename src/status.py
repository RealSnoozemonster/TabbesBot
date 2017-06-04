from datetime import datetime

class out:
  def __init__(self):
    # ANSI Color definations
    self.HEADER = '\033[95m'
    self.OKBLUE = '\033[94m'
    self.OKGREEN = '\033[92m'
    self.WARNING = '\033[93m'
    self.FAIL = '\033[91m'
    self.ENDC = '\033[0m'
    self.BOLD = '\033[1m'
    self.UNDERLINE = '\033[4m'
  
  def getTimeStamp(self):
    return '[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())
  
  def Log(self, msg):
    print(self.BOLD + self.getTimeStamp() + self.OKBLUE  + ' [LOG]     | ' + self.ENDC + msg)
  
  def Success(self, msg):
    print(self.BOLD + self.getTimeStamp() + self.OKGREEN + ' [SUCCESS] | ' + self.ENDC + msg)
  
  def Warn(self, msg):
    print(self.BOLD + self.getTimeStamp() + self.WARNING + ' [WARNING] | ' + self.ENDC + msg)
    
  def Error(self, msg):
    print(self.BOLD + self.getTimeStamp() + self.FAIL    + ' [ERROR]   | ' + self.ENDC + msg)