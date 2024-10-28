<<<<<<< HEAD
import sys
import time
# print("HELLO")

# user_input = sys.argv[1]
# print(f"Received input: {user_input}")


user_input = sys.argv[1]
print(f"Received input: {user_input}", flush=True)  # Ensure immediate output

# Simulate real-time output
for i in range(5):
    print(f"Output {i}", flush=True)  # Ensure immediate output
    time.sleep(2)
# # Step 2: Check command-line arguments
# if len(sys.argv) != 2:
#     print("Usage: python script.py <number>")
#     sys.exit(1)

# # Step 3: Assign argument to variable
# try:
#     user_input = int(sys.argv[1])
# except ValueError:
#     print("Please enter a valid integer.")
#     sys.exit(1)

=======
import time
print("HELLO")
for i in range(1, 5000):
    print(f'Number: {i}')
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

>>>>>>> output_form_real_time
# # Step 4: Use while loop with argument
# count = 0
# while count < user_input:
#     print(f"Count is: {count}")
#     count += 1