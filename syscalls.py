import ops
import config
from mcfunction import McFunction



"""
#define syscall1(i) \
asm volatile ( \
    "li $v0, 1\n\t" \
    "move $a0, %0\n\t" \
    "syscall\n\t" \
    :: "ri" (i) : "$2", "$4" \
); \

#define syscall4(str) \
asm volatile ( \
    "li $v0, 4\n\t" \
    "move $a0, %0\n\t" \
    "syscall\n\t" \
    :: "r" (str) : "$2", "$4" \
); \
"""


def syscall1():
    return [ "tellraw @p [\"\", {\"score\":{\"name\":\"" + config.NAMESPACE + "\", \"objective\":\"a0\"}}]" ]


def syscall10():
    return [ "tellraw @p [\"exit\"]" ]


def syscall4():
    return [ "data modify storage minecraft:" + config.NAMESPACE + " tmp_string set value []", "function " + config.NAMESPACE + ":syscalls/syscall4_1" ]


def syscall4_1():
    loop = ops.lb(ops.Arg(ops.ArgType.REGISTER, "output_char"), ops.Arg(ops.ArgType.ADDRESS, "0", "a0"))
    loop.append("scoreboard players add " + config.NAMESPACE + " a0 1")

    for c in config.SUPPORTED_CHARACTERS:
        loop.append("execute if score " + config.NAMESPACE + " output_char matches " + str(ord(c)) + " run data modify storage minecraft:" + config.NAMESPACE + " tmp_string append value \"" + c + "\"")

    loop.append("execute if score " + config.NAMESPACE + " output_char matches 0 run tellraw @p {\"nbt\":\"tmp_string\",\"storage\":\"minecraft:" + config.NAMESPACE + "\",\"interpret\":true}")
    loop.append("execute if score " + config.NAMESPACE + " output_char matches 1.. run function " + config.NAMESPACE + ":syscalls/syscall4_1")

    return loop


def syscall11():
    return [ "execute if score " + config.NAMESPACE + " a0 matches " + str(ord(c)) + " run tellraw @p \"" + c + "\"" for c in config.SUPPORTED_CHARACTERS ]


def syscall8():
    return [ "scoreboard players operation " + config.NAMESPACE + " input_next = " + config.NAMESPACE + " next",
             "scoreboard players set " + config.NAMESPACE + " next 0",
             "scoreboard players set " + config.NAMESPACE + " input_type " + config.InputType.STR,
             "scoreboard players operation " + config.NAMESPACE + " input_maxlength = " + config.NAMESPACE + " a1",
             "scoreboard players set " + config.NAMESPACE + " input_length 0",
             "function " + config.NAMESPACE + ":input/input_keyboard" ]


def syscall12():
    return [ "scoreboard players operation " + config.NAMESPACE + " input_next = " + config.NAMESPACE + " next",
             "scoreboard players set " + config.NAMESPACE + " next 0",
             "scoreboard players set " + config.NAMESPACE + " input_type " + config.InputType.CHAR,
             "scoreboard players set " + config.NAMESPACE + " input_maxlength 0",
             "scoreboard players set " + config.NAMESPACE + " input_length 0",
             "function " + config.NAMESPACE + ":input/input_keyboard" ]


syscalls = {
    "1": syscall1, # print int
    "10": syscall10, # exit
    "4": syscall4, # print str
    "4_1": syscall4_1, # print str loop
    "11": syscall11, # print char
    "8": syscall8, # read str
    "12": syscall12 # read char
}


def generateSyscalls():
    functions = {}

    func = McFunction()
    for k, v in syscalls.items():
        if k.find("_") == -1:
            func.addLine("execute if score " + config.NAMESPACE + " v0 matches " + k + " run function " + config.NAMESPACE + ":syscalls/syscall" + k)

    functions["syscalls/syscall"] = func

    for k, v in syscalls.items():
        func = McFunction()
        func.addLines(v())
        functions["syscalls/syscall" + k] = func

    return functions
