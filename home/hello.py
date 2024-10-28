import time
from django.core.cache import cache

def long_running_task():
    for i in range(101):  # Progress from 0 to 100
        time.sleep(0.1)  # Simulate work
        cache.set('task_progress', i)  # Update progress in cache
# for i in range(1, 50):
#     print(f'Number: {i}')
# user_input = sys.argv[1]
# print(f"Received input: {user_input}")

# Step 2: Check command-line arguments
# if len(sys.argv) != 2:
#     print("Usage: python script.py <number>")
#     sys.exit(1)

# # Step 3: Assign argument to variable
# try:
#     user_input = int(sys.argv[1])
# except ValueError:
#     print("Please enter a valid integer.")
#     sys.exit(1)

# # Step 4: Use while loop with argument
# count = 0
# while count < user_input:
#     print(f"Count is: {count}")
#     count += 1