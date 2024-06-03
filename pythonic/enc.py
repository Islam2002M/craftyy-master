import bcrypt

passwords = [
    "Pass@word123",
    "PaSs321@Word",
    "Password@456",
    "Word@Pass123",
    "456@Password",
    "Pass654@word",
    "password789@",
    "789@passWord",
    "word789@Pass",
    "Pass789@word",
    "789@password",
    "word987@pass",
    "Pass987@word",
    "987@wordpass",
    "pass987@word",
    "987password@"
]

hashed_passwords = []

for password in passwords:
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    hashed_passwords.append(hashed_password)

print(hashed_passwords)
