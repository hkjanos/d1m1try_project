################CONSTANTS###################################
# to ease readability of code, there are the constant values defined
# security level constants
def DEFAULT():
    return 1

def ELEVATED():
    return 2

def NONE():
    return 3

# diagnostic response constants
# NOTE: the goal here was not to comply with ISO 14299 nor any other standard,
#       but rather to create some dummy protocol
# Positive response for the request.
def POS_R_PERM_GRANTED():
    return 10

# Negative response, the request is not permitted with
# the current conditions.
def NEG_R_PERMISSION_DENIED():
    return 21

# Negative response, the input structure did not match
# to the request input structure.
def NEG_R_MALFORMED_INPUT():
    return 22

# Negative response, the value you are looking for is not present
# in the memory or not known by the tester
def NEG_R_INCORRECT_KEYWORD():
    return 23

# Negative response, brute force protection is active.
def NEG_R_BRUTE_FORCE_PROTECTION():
    return 24

# decoding info from tuples lists belonging to diag and xcp
# 0 - readPermission classifications
def ACCESS_RD():
    return 0

# 1 - writePermission classifications
def ACCESS_WR():
    return 1

# 2 - value of the actual variable
def VAR_VALUE():
    return 2

# 3 - value of the variable address
def VAR_ADDRESS():
    return 3

# Vehicle lights types - might be useful for some use cases
# but currently they are not used.
# IDEA: you need to change headlight but with another type. That one needs to be adjusted in the computer.
# Halogen
def HALOGEN():
    return 1

# Xenon
def XENON():
    return 2

# LED
def LED():
    return 3

# Vehicle maneuver directions (not used currently)
def LEFT():
    return -1

def RIGHT():
    return 1