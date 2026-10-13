
from db import init_db, register_user, authenticate_user, get_player

init_db()

username = "test_player_01"
password = "TestPass123!"

success, message = register_user(username, password)
print(message)

if success:
    user_id = authenticate_user(username, password)
    print("Login successful:", user_id is not None)

    if user_id is not None:
        print("Player profile:", get_player(user_id))
else:
    print("This username may already exist. Try a different one.")
