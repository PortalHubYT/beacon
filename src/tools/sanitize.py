import string
from .config import config

def pick_display(nickname, unique_id):
  
  if nickname:
    name = sanitize(nickname)
    if len(name) < len(nickname) / 4:
      name = unique_id
      
  elif unique_id:
    name = sanitize(unique_id)
    
  else:
    return None
  
  name = crop(name)
  return name
  
def sanitize(text):
    """Remove non-ASCII characters from string s"""
    return ''.join(filter(lambda x: x in string.printable, text))
  
def crop(text, max=config.crop_size):
    # Shorten text longer than (config.crop_size) characters and end with '...'
    text = text[:max] + "..." if len(text) > max else text
    return text

# =================================================================================================

def role_parser(event):

    role = None
    
    if event.user.is_moderator:
        role = "Moderator"
    elif event.user.is_top_gifter:
        role = "Top Gifter"
    elif event.user.is_new_gifter:
        role = "New Gifter"
    elif event.user.is_following:
        role = "Follower"
                    
    return role


def get_profile(event):
    profile = {
        "display": pick_display(event.user.nickname, event.user.unique_id),
        "nickname": event.user.nickname,
        "unique_id": event.user.unique_id,
        "user_id": event.user.user_id,
        "role": role_parser(event),
        "avatars": event.user.avatar.urls,
        "followers": event.user.info.followers,
        "following": event.user.info.following,
        "comment": None if "comment" not in vars(event) else event.comment,
        "gift": None if "gift" not in vars(event) else event.gift.info.name,
        "gift_value": None if "gift" not in vars(event) else event.gift.info.diamond_count
    }
    
    return profile