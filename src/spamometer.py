import unicodedata

def score(char):
  if (unicodedata.category(char) == 'Ll'):
    return 1
  elif (unicodedata.category(char) == 'Lu'):
    return 0.5
  elif (unicodedata.category(char) == 'Nd'):
    return 1
  elif (char == '.' or char == '!' or char == '?'):
    return 1
  else:
    return -1

def check(msg):
  grade = 0
  isSpam = False
  for char in msg:
    grade += score(char)
    if (score(char) < 0):
      isSpam = True
  return [grade, isSpam]                              