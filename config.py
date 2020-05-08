import string



class InputType:
    INT = "1"
    STR = "2"
    CHAR = "3"

SUPPORTED_CHARACTERS = string.ascii_letters + string.digits + " "
NAMESPACE = "mips"

# changing the size needs a change in compiler.py:generateRam, addr assigment
RAM_BLOCK_SIZE = 16

# min 2
RAM_DEPTH = 2

DEBUG = True
