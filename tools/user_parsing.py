def role_parser(event):
    if event.user.details.follow_role:
        role = "Follower"

    if event.user.badges:
        for badge in event.user.badges:
            if badge.badge_scene_type == 8:
                continue

            for text_badge in badge.text_badges:
                if text_badge.name == "Moderator":
                    role = "Moderator"

                elif text_badge.name == "New gifter":
                    role = "New Gifter"

            for image_badge in badge.image_badges:
                if "top_gifter" in image_badge.url:
                    role = "Top Gifter"
                    
    return role


def get_profile(event):
    profile = {
        "nickname": event.user.nickname,
        "unique_id": event.user.unique_id,
        "userId": event.user.user_id,
        "role": role_parser(event),
        "comment": event.comment,
        "event": event,
    }
    
    return profile
