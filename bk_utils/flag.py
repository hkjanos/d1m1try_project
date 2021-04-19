import hashlib


def flag(input):
    # This function creates flags for notifying the player that she succeeded in a challenge.
    print('<FLAG>' + hashlib.sha256(input).hexdigest() + '</FLAG>')