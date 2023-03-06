import string

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
  
def crop(text):
    # Shorten messages longer than 50 characters and end with '...'
    text = text[:50] + "..." if len(text) > 50 else text
    return text