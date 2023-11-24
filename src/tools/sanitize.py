import string

from .config import config

# from custom_skin import custom_skins



def pick_display(nickname, unique_id):
    if nickname:
        name = sanitize(nickname)
        if len(name) < len(nickname) / 4:
            name = "@" + unique_id

    elif unique_id:
        name = sanitize(unique_id)
        name = "@" + name

    else:
        return None

    name = crop(name)
    return name.replace("\\", "\\\\")


def sanitize(text):
    """Remove non-ASCII characters from string s"""
    return "".join(filter(lambda x: x in string.printable, text))


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
    display_name = pick_display(event.user.nickname, event.user.unique_id)
    # custom_skin = custom_skins.get(event.user.unique_id, None)
    custom_skin = display_name
    profile = {
        "display": display_name, # Curated display name between nickname and unique_id, shortened and sanitized
        "skin_display": display_name if custom_skin == None else custom_skin, # Actual skin to use for the display name
        "nickname": event.user.nickname, # Visual name seen in TikTok
        "unique_id": event.user.unique_id, # @name in TikTok
        "user_id": event.user.user_id, # Hidden to view, actual unique ID of the user (825582808 kinda stuff)
        "role": role_parser(event),
        "avatars": event.user.avatar.urls,
        "followers": event.user.info.followers,
        "following": event.user.info.following,
        "comment": None if "comment" not in vars(event) else event.comment,
        "gift": None if "gift" not in vars(event) else event.gift.info.name,
        "gift_value": None if "gift" not in vars(event) else event.gift.info.diamond_count,
        "gift_streakable": None if "gift" not in vars(event) else event.gift.streakable,
    }

    if profile["gift"] and profile["gift_streakable"]:
        profile["gift_streaking"] = event.gift.streaking
        profile["gift_count"] = event.gift.count
    
    return profile
