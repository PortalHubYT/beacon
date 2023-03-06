import string

def sanitize(text):
    """Remove non-ASCII characters from string s"""
    return ''.join(filter(lambda x: x in string.printable, text))
  
def crop(text):
    # Shorten messages longer than 50 characters and end with '...'
    text = text[:50] + "..." if len(text) > 50 else text