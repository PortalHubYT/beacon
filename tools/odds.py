import random

def flip_coin():
    return random.choice([True, False])
  

def pick_from_queue(queues):
  
  # 80% chance to display a donator message
  # 15% chance to display a follower message
  # 5% chance to display a normal message

  # If there is no donator message, then 80% chance to display a follower message
  # and 20% chance to display a normal message

  # If there is no donator or follower message, then 100% chance to display a normal message

  normal_queue, follower_queue, priority_queue, bypass_queue = queues
  
  if bypass_queue:
    return bypass_queue.pop(0)
    
  elif priority_queue:
    
    randint = random.randint(0, 100)
    
    if 0 <= randint <= 80:
      return priority_queue.pop(0)
    elif 80 < randint <= 95:
      return follower_queue.pop(0)
    else:
      try:
        return normal_queue.pop(0)
      except:
        return None
    
  elif follower_queue:
    
    randint = random.randint(0, 100)
    
    if 0 <= randint <= 60:
      return follower_queue.pop(0)
    else:
      try:
        return normal_queue.pop(0)
      except:
        return None
    
  else:
    if normal_queue:
      try:
        return normal_queue.pop(0)
      except:
        return None
    else:
      return None
