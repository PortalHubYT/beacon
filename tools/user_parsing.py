from tools.sanitize import sanitize

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
        "nickname": event.user.nickname,
        "unique_id": event.user.unique_id,
        "userId": event.user.user_id,
        "role": role_parser(event),
        "comment": None if "comment" not in vars(event) else event.comment,
        "gift": None if "gift" not in vars(event) else event.gift.info.name,
    }
    
    return profile
