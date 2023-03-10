import string
from config import config

def pick_display(profile):
  
  if profile["nickname"]:
    name = sanitize(profile["nickname"])
    if name == "":
      name = profile["unique_id"]
      
  elif profile["unique_id"]:
    name = sanitize(profile["unique_id"])
    
  else:
    return None
  
  name = crop(name)
  return name
  
def sanitize(text):
    """Remove non-ASCII characters from string s"""
    return ''.join(filter(lambda x: x in string.printable, text))
  
def crop(text, max = config["crop_size"]):
    # Shorten text longer than 50 characters and end with '...'
    text = text[:max] + "..." if len(text) > max else text
    return text