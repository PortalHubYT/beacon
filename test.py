import time

# This file will repeadetly write to test.log incrementing numbers
i = 0
while True:
    i += 1
    with open("test.log", "a") as f:
        f.write(f"{i}\n")
    time.sleep(1)