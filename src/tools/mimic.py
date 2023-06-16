import random
import datetime
import os

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Get the directory containing the current file
directory = os.path.dirname(current_file_path)

# Construct the absolute file path by joining the directory and the desired file name
file_path = os.path.join(directory, 'tools/')

def gen_fake_profiles(amount):
    with open(file_path + 'random_comments.txt', 'r') as f:
            random_comments = f.readlines()
            
    with open(file_path + 'random_pseudos.txt', 'r') as f:
        random_pseudos = f.readlines()
    
    random_gift = ["Diamond", "Gold", "Silver", "Bronze"]
    random_avatars = ["https://i.imgur.com/0Z0Z0Z0.png", "https://i.imgur.com/1Z1Z1Z1.png", "https://i.imgur.com/2Z2Z2Z2.png", "https://i.imgur.com/3Z3Z3Z3.png", "https://i.imgur.com/4Z4Z4Z4.png", "https://i.imgur.com/5Z5Z5Z5.png", "https://i.imgur.com/6Z6Z6Z6.png", "https://i.imgur.com/7Z7Z7Z7.png", "https://i.imgur.com/8Z8Z8Z8.png", "https://i.imgur.com/9Z9Z9Z9.png"]
    random_role = ["Moderator", "Top Gifter", "New Gifter", "Follower", None]
    
    profiles = []
    for i in range(amount):
        random_name = random.choice(random_pseudos).strip()
        profile = {
            "display": f'{i + 1}_{random_name}',
            "nickname": f'{i + 1}_{random_name}',
            "unique_id": f'{i + 1}_{random_name}',
            "user_id": random.randint(100000000, 999999999),
            "role": random.choice(random_role),
            "avatars": random_avatars,
            "followers": random.randint(0, 100000),
            "following": random.randint(0, 100000),
            "comment": random.choice(random_comments).strip(),
            "gift": random.choice(random_gift),
            "gift_value": random.randint(0, 100000),
        }
        profiles.append(profile)
        
    return profiles