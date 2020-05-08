import config
import ops
from mcfunction import McFunction



def generateLoad():
    func = McFunction()

    #if config.DEBUG:
    func.addLine("gamerule sendCommandFeedback true")
    #else:
    #    func.addLine("gamerule sendCommandFeedback false")
    
    func.addLine("data modify storage " + config.NAMESPACE + " ram set value []")
    for i in range(config.RAM_DEPTH - 1):
        func.addLine("data modify storage " + config.NAMESPACE + " ram_cache" + str(i + 1) + " set value []")

    func.addLine("data modify storage " + config.NAMESPACE + " input_string set value []")
    func.addLine("data modify storage " + config.NAMESPACE + " tmp_string set value []")
    func.addLines(ops.generateRegs())

    # name max length 16
    helpers = [ "next", "tmp", "addr_offset", "bin_tmp", "bin_tmp2", "bitmask",
                "ram_addr",
                "output_char", 
                "input_char", "input_maxlength", "input_length", "input_type", "input_next" ] # type: 1 - int; 2 - str; 3 - char

    helpers += ["bin1_" + str(i) for i in range(32)]
    helpers += ["bin2_" + str(i) for i in range(32)]
    helpers += ["bin3_" + str(i) for i in range(32)]
    helpers += ["ram_addr_" + str(i) for i in range(config.RAM_DEPTH)]

    for h in helpers:
        func.addLine("scoreboard objectives add " + h + " dummy")
        func.addLine("scoreboard players set " + config.NAMESPACE + " " + h + " 0")

    return func
    

def generateInputs():
    functions = {}

    keyboard = [
        [ "q", "w", "e", "r", "t", "y", "u", "i", "o", "p" ],
        [ "a", "s", "d", "f", "g", "h", "j", "k", "l", "enter"],
        [ "z", "x", "c", "v", "b", "n", "m"],
    ]

    func = McFunction()
    func.addLine("data modify storage " + config.NAMESPACE + " input_string set value []")
    keyboardTellraw = "tellraw @p [\"\","
    for line in keyboard:
        for c in line:
            keyboardTellraw += "{\"text\":\"" + c + "\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/function " + config.NAMESPACE + ":input/input_" + c + "\"}},\" \","
        
        keyboardTellraw += "\"\\n\","

    keyboardTellraw += "\"\"]"
    func.addLine(keyboardTellraw)
    functions["input/input_keyboard"] = func

    chars = [
        "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
        "a", "s", "d", "f", "g", "h", "j", "k", "l", 
        "z", "x", "c", "v", "b", "n", "m"
    ]

    for c in chars:
        func = McFunction()
        func.addLine("scoreboard players set " + config.NAMESPACE + " input_char " + str(ord(c)))
        func.addLine("execute if score " + config.NAMESPACE + " input_type matches 1.. run function " + config.NAMESPACE + ":input/input_key")
        functions["input/input_" + c] = func

    func = McFunction()
    func.addLine("scoreboard players set " + config.NAMESPACE + " input_char 0")
    func.addLine("scoreboard players set " + config.NAMESPACE + " input_maxlength -1")
    func.addLine("execute if score " + config.NAMESPACE + " input_type matches 1.. run function " + config.NAMESPACE + ":input/input_key")
    functions["input/input_enter"] = func

    func = McFunction()
    func.addLine("execute if score " + config.NAMESPACE + " input_type matches " + config.InputType.INT + " run function " + config.NAMESPACE + ":input/input_int")
    func.addLine("execute if score " + config.NAMESPACE + " input_type matches " + config.InputType.STR + " run function " + config.NAMESPACE + ":input/input_str")
    func.addLine("execute if score " + config.NAMESPACE + " input_type matches " + config.InputType.CHAR + " run function " + config.NAMESPACE + ":input/input_char")
    func.addLines(["execute if score " + config.NAMESPACE + " input_char matches " + str(ord(c)) + " run data modify storage minecraft:" + config.NAMESPACE + " input_string append value \"" + c + "\"" for c in config.SUPPORTED_CHARACTERS ])
    func.addLine("title @p actionbar [\"\",{\"text\":\"Input: \"},{\"nbt\":\"input_string\",\"storage\":\"minecraft:" + config.NAMESPACE + "\",\"interpret\":true}]")
    func.addLine("scoreboard players add " + config.NAMESPACE + " input_length 1")
    func.addLine("execute if score " + config.NAMESPACE + " input_length >= " + config.NAMESPACE + " input_maxlength run function " + config.NAMESPACE + ":input/input_end")
    functions["input/input_key"] = func
    
    func = McFunction()
    func.addLine("scoreboard players set " + config.NAMESPACE + " input_char 0")
    func.addLine("execute if score " + config.NAMESPACE + " input_type matches " + config.InputType.STR + " run function " + config.NAMESPACE + ":input/input_str")
    func.addLine("scoreboard players set " + config.NAMESPACE + " input_type 0")
    func.addLine("scoreboard players operation " + config.NAMESPACE + " next = " + config.NAMESPACE + " input_next")
    func.addLine("scoreboard players set " + config.NAMESPACE + " input_next 0")
    functions["input/input_end"] = func
    
    func = McFunction()
    func.addLines(ops.sb(ops.Arg(ops.ArgType.REGISTER, "input_char"), ops.Arg(ops.ArgType.ADDRESS, "0", "a0")))
    func.addLine("scoreboard players add " + config.NAMESPACE + " a0 1")
    functions["input/input_str"] = func

    func = McFunction()
    functions["input/input_int"] = func

    func = McFunction()
    func.addLine("scoreboard players operation " + config.NAMESPACE + " v0 = " + config.NAMESPACE + " input_char")
    functions["input/input_char"] = func

    return functions
