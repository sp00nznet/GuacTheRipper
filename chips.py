"""
chips.py  --  The free chips basket.

Every Chipotle order starts with chips. Before we bother Pepper (and spend
burrito budget), we munch through a small built-in basket of the passwords
people actually use. Combined with Toppings, this cracks a shocking number of
weak archives for **zero orders placed**.

It's a curated starter basket, not a 14-million-line rockyou. Want the big bag?
That's what `--doordash rockyou.txt` is for.
"""

BASKET = [
    "password", "123456", "12345678", "123456789", "1234567890",
    "qwerty", "qwerty123", "abc123", "letmein", "admin", "root",
    "welcome", "monkey", "dragon", "iloveyou", "football", "baseball",
    "sunshine", "princess", "password1", "000000", "111111", "121212",
    "123123", "secret", "changeme", "trustno1", "master", "hello",
    "freedom", "whatever", "ninja", "login", "starwars", "superman",
    "passw0rd", "zaq12wsx", "shadow", "michael", "guacamole", "chipotle",
    "burrito", "extraguac",
]
