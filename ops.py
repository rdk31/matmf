import config
from enum import Enum
from enum import auto
import re



class ArgType(Enum):
    REGISTER = auto()
    IMMEDIATE = auto()
    LABEL = auto()
    ADDRESS = auto()


class Arg:

    def __init__(self, argType, *args):
        self.argType = argType
        if len(args) == 1:
            self.offset = "0"
            self.value = args[0]
        elif len(args) == 2:
            self.offset = args[0]
            self.value = args[1]

    def __str__(self):
        return self.value


def parseArgs(args):
    argTypes = {
        ArgType.REGISTER : r"(^\$(?:\d?\d|[a-z]\d|[a-z][a-z])$)",
        ArgType.IMMEDIATE : r"(^\-?\d+$)", 
        ArgType.LABEL : r"(^[a-zA-Z]\w*$)", 
        ArgType.ADDRESS : r"^(\-?\d*)\((\$(?:\d?\d|[a-z]\d|[a-z][a-z]))\)$"
    }

    ret = []

    for arg in args:
        parsed = False
        for k, v in argTypes.items():
            m = re.match(v, arg)
            if m:
                parsed = True
                ret.append(Arg(k, *m.groups()))
                print("parsed:", arg, "as", k)
                break
        
        if not parsed:
            raise Exception("cannot parse argument:", arg)

    return ret


class Op:
    argTypes = []
    branchOut = False
    generator = None

    def __init__(self, argTypes, generator, branchOut = False):
        self.argTypes = argTypes
        self.branchOut = branchOut
        self.generator = generator

    def generate(self, args):
        return self.generator(*args)


def move(dst_reg, src_reg):
    ret = []

    if config.DEBUG:
        ret.append("#move: " + str(dst_reg) + " " + str(src_reg))

    ret.append("scoreboard players operation " + config.NAMESPACE + " " + dst_reg.value + " = " + config.NAMESPACE + " " + src_reg.value)

    return ret


def add(dst_reg, src_reg1, src_reg2):    
    ret = []
    if config.DEBUG:
        ret.append("#add: " + str(dst_reg) + " " + str(src_reg1) + " " + str(src_reg2))
        
    ret += move(dst_reg, src_reg1)
    ret.append("scoreboard players operation " + config.NAMESPACE + " " + dst_reg.value + " += " + config.NAMESPACE + " " + src_reg2.value)

    return ret


def sub(dst_reg, src_reg1, src_reg2):
    ret = []
    if config.DEBUG:
        ret.append("#sub: " + str(dst_reg) + " " + str(src_reg1) + " " + str(src_reg2))

    ret += move(dst_reg, src_reg1)
    ret.append("scoreboard players operation " + config.NAMESPACE + " " + dst_reg.value + " -= " + config.NAMESPACE + " " + src_reg2.value)

    return ret


def li(dst_reg, imm):
    ret = []
    if config.DEBUG:
        ret.append("#li: " + str(dst_reg) + " " + str(imm))

    ret.append("scoreboard players set " + config.NAMESPACE + " " + dst_reg.value + " " + imm.value)

    return ret


def blt(reg1, reg2, label):
    ret = []
    if config.DEBUG:
        ret.append("#blt: " + str(reg1) + " " + str(reg2) + " " + str(label))

    ret.append("execute if score " + config.NAMESPACE + " " + reg1.value + " < " + config.NAMESPACE + " " + reg2.value + " run scoreboard players set " + config.NAMESPACE + " next " + label.value)

    return ret


def ble(reg1, reg2, label):
    ret = []
    if config.DEBUG:
        ret.append("#ble: " + str(reg1) + " " + str(reg2) + " " + str(label))

    ret.append("execute if score " + config.NAMESPACE + " " + reg1.value + " <= " + config.NAMESPACE + " " + reg2.value + " run scoreboard players set " + config.NAMESPACE + " next " + label.value)

    return ret


def beq(reg1, reg2, label):
    ret = []
    if config.DEBUG:
        ret.append("#beq: " + str(reg1) + " " + str(reg2) + " " + str(label))

    ret.append("execute if score " + config.NAMESPACE + " " + reg1.value + " = " + config.NAMESPACE + " " + reg2.value + " run scoreboard players set " + config.NAMESPACE + " next " + label.value)

    return ret


def bgt(reg1, reg2, label):
    ret = []
    if config.DEBUG:
        ret.append("#bgt: " + str(reg1) + " " + str(reg2) + " " + str(label))

    ret.append("execute if score " + config.NAMESPACE + " " + reg1.value + " > " + config.NAMESPACE + " " + reg2.value + " run scoreboard players set " + config.NAMESPACE + " next " + label.value)

    return ret


def bge(reg1, reg2, label):
    ret = []
    if config.DEBUG:
        ret.append("#bge: " + str(reg1) + " " + str(reg2) + " " + str(label))

    ret.append("execute if score " + config.NAMESPACE + " " + reg1.value + " >= " + config.NAMESPACE + " " + reg2.value + " run scoreboard players set " + config.NAMESPACE + " next " + label.value)

    return ret


def j(label):
    ret = []
    if config.DEBUG:
        ret.append("#j: " + str(label))

    ret.append("scoreboard players set " + config.NAMESPACE + " next " + label.value)

    return ret
  

def la(dst_reg, datalabel):
    ret = []
    if config.DEBUG:
        ret.append("#la: " + str(dst_reg) + " " + str(datalabel))

    ret.append("scoreboard players set " + config.NAMESPACE + " " + dst_reg.value + " " + datalabel.value)

    return ret


def addi(dst_reg, src_reg, imm):
    ret = []
    if config.DEBUG:
        ret.append("#addi: " + str(dst_reg) + " " + str(src_reg) + " " + str(imm))

    ret += move(dst_reg, src_reg)
    ret.append("scoreboard players add " + config.NAMESPACE + " " + dst_reg.value + " " + imm.value)

    return ret


def subi(dst_reg, src_reg, imm):
    ret = []
    if config.DEBUG:
        ret.append("#subi: " + str(dst_reg) + " " + str(src_reg) + " " + str(imm))

    ret += move(dst_reg, src_reg)
    ret.append("scoreboard players remove " + config.NAMESPACE + " " + dst_reg.value + " " + imm.value)

    return ret


def lb(dst_reg, src_addr):
    ret = []
    if config.DEBUG:
        ret.append("#lb: " + str(dst_reg) + " " + str(src_addr))

    ret.append("scoreboard players operation " + config.NAMESPACE + " ram_addr = " + config.NAMESPACE + " " + src_addr.value)
    ret.append("scoreboard players add " + config.NAMESPACE + " ram_addr " + src_addr.offset)
    ret.append("scoreboard players set " + config.NAMESPACE + " tmp " + str(config.RAM_BLOCK_SIZE))
    for i in range(config.RAM_DEPTH):
        ret.append("scoreboard players operation " + config.NAMESPACE + " ram_addr_" + str(i) + " = " + config.NAMESPACE + " ram_addr")
        ret.append("scoreboard players operation " + config.NAMESPACE + " ram_addr_" + str(i) + " %= " + config.NAMESPACE + " tmp")
        ret.append("scoreboard players operation " + config.NAMESPACE + " ram_addr /= " + config.NAMESPACE + " tmp")

    for j in range(config.RAM_BLOCK_SIZE):
            ret.append("execute if score " + config.NAMESPACE + " ram_addr_" + str(config.RAM_DEPTH - 1) + " matches " + str(j) + " run data modify storage " + config.NAMESPACE + " ram_cache1 set from storage " + config.NAMESPACE + " ram[" + str(j) + "]")

    for i in reversed(range(1, config.RAM_DEPTH - 1)):
        for j in range(config.RAM_BLOCK_SIZE):
            ret.append("execute if score " + config.NAMESPACE + " ram_addr_" + str(i) + " matches " + str(j) + " run data modify storage " + config.NAMESPACE + " ram_cache" + str(config.RAM_DEPTH - i) + " set from storage " + config.NAMESPACE + " ram_cache" + str(config.RAM_DEPTH - i - 1) + "[" + str(j) + "]")

    for j in range(config.RAM_BLOCK_SIZE):
        ret.append("execute if score " + config.NAMESPACE + " ram_addr_0 matches " + str(j) + " store result score " + config.NAMESPACE + " " + dst_reg.value + " run data get storage " + config.NAMESPACE + " ram_cache" + str(config.RAM_DEPTH - 1) + "[" + str(j) + "]")

    return ret

def sb(src_reg, dst_addr):
    ret = []
    if config.DEBUG:
        ret.append("#sb: " + str(src_reg) + " " + str(dst_addr))

    ret.append("scoreboard players operation " + config.NAMESPACE + " ram_addr = " + config.NAMESPACE + " " + dst_addr.value)
    ret.append("scoreboard players add " + config.NAMESPACE + " ram_addr " + dst_addr.offset)
    ret.append("scoreboard players set " + config.NAMESPACE + " tmp " + str(config.RAM_BLOCK_SIZE))
    for i in range(config.RAM_DEPTH):
        ret.append("scoreboard players operation " + config.NAMESPACE + " ram_addr_" + str(i) + " = " + config.NAMESPACE + " ram_addr")
        ret.append("scoreboard players operation " + config.NAMESPACE + " ram_addr_" + str(i) + " %= " + config.NAMESPACE + " tmp")
        ret.append("scoreboard players operation " + config.NAMESPACE + " ram_addr /= " + config.NAMESPACE + " tmp")

    for j in range(config.RAM_BLOCK_SIZE):
            ret.append("execute if score " + config.NAMESPACE + " ram_addr_" + str(config.RAM_DEPTH - 1) + " matches " + str(j) + " run data modify storage " + config.NAMESPACE + " ram_cache1 set from storage " + config.NAMESPACE + " ram[" + str(j) + "]")

    for i in reversed(range(1, config.RAM_DEPTH - 1)):
        for j in range(config.RAM_BLOCK_SIZE):
            ret.append("execute if score " + config.NAMESPACE + " ram_addr_" + str(i) + " matches " + str(j) + " run data modify storage " + config.NAMESPACE + " ram_cache" + str(config.RAM_DEPTH - i) + " set from storage " + config.NAMESPACE + " ram_cache" + str(config.RAM_DEPTH - i - 1) + "[" + str(j) + "]")

    for j in range(config.RAM_BLOCK_SIZE):
        ret.append("execute if score " + config.NAMESPACE + " ram_addr_0 matches " + str(j) + " store result storage " + config.NAMESPACE + " ram_cache" + str(config.RAM_DEPTH - 1) + "[" + str(j) + "]" + " int 1 run scoreboard players get " + config.NAMESPACE + " " + src_reg.value)

    for i in range(1, config.RAM_DEPTH - 1):
        for j in range(config.RAM_BLOCK_SIZE):
            ret.append("execute if score " + config.NAMESPACE + " ram_addr_" + str(i) + " matches " + str(j) + " run data modify storage " + config.NAMESPACE + " ram_cache" + str(config.RAM_DEPTH - i - 1) + "[" + str(j) + "] set from storage " + config.NAMESPACE + " ram_cache" + str(config.RAM_DEPTH - i))

    for j in range(config.RAM_BLOCK_SIZE):
        ret.append("execute if score " + config.NAMESPACE + " ram_addr_" + str(config.RAM_DEPTH - 1) + " matches " + str(j) + " run data modify storage " + config.NAMESPACE + " ram[" + str(j) + "] set from storage " + config.NAMESPACE + " ram_cache1")

    return ret


def convertToBin(dst, src_reg):
    ret = []
    if config.DEBUG:
        ret.append("#convertToBin: " + dst + " " + str(src_reg))

    ret.append("scoreboard players operation " + config.NAMESPACE + " bin_tmp = " + config.NAMESPACE + " " + src_reg.value)
    ret.append("scoreboard players set " + config.NAMESPACE + " tmp 2")
    for i in range(32):
        ret.append("scoreboard players operation " + config.NAMESPACE + " bin_tmp2 = " + config.NAMESPACE + " bin_tmp")
        ret.append("scoreboard players operation " + config.NAMESPACE + " bin_tmp2 %= " + config.NAMESPACE + " tmp")
        ret.append("scoreboard players operation " + config.NAMESPACE + " bin" + dst + "_" + str(i) + " = " + config.NAMESPACE + " bin_tmp2")
        ret.append("scoreboard players operation " + config.NAMESPACE + " bin_tmp /= " + config.NAMESPACE + " tmp")

    return ret


def convertToDec(dst_reg, src):
    ret = []
    if config.DEBUG:
        ret.append("#convertToDec: " + str(dst_reg) + " " + src)

    ret.append("scoreboard players set " + config.NAMESPACE + " bin_tmp 0")
    ret.append("scoreboard players set " + config.NAMESPACE + " bin_tmp2 1")
    ret.append("scoreboard players set " + config.NAMESPACE + " tmp 2")
    for i in range(32):
        ret.append("execute if score " + config.NAMESPACE + " bin" + src + "_" + str(i) + " matches 1 run scoreboard players operation " + config.NAMESPACE + " bin_tmp += " + config.NAMESPACE + " bin_tmp2")
        ret.append("scoreboard players operation " + config.NAMESPACE + " bin_tmp2 *= " + config.NAMESPACE + " tmp")

    ret.append("scoreboard players operation " + config.NAMESPACE + " " + dst_reg.value + " = " + config.NAMESPACE + " bin_tmp")

    return ret
    

def setBinary(dst, value):
    ret = []
    if config.DEBUG:
        ret.append("#setBinary: " + dst + " " + str(value))

    bin_value = format(value, "032b")[::-1]
    for i in range(32):
        ret.append("scoreboard players set " + config.NAMESPACE + " bin" + dst + "_" + str(i) + " " + bin_value[i])

    return ret


def sra(dst_reg, src_reg, imm):
    ret = []
    if config.DEBUG:
        ret.append("#sra: " + str(dst_reg) + " " + str(src_reg) + " " + str(imm))

    ret.append("scoreboard players set " + config.NAMESPACE + " bin_tmp " + str(pow(2, int(imm))))
    ret.append("scoreboard players operation " + config.NAMESPACE + " " + dst_reg.value + " = " + config.NAMESPACE + " " + src_reg.value)
    ret.append("scoreboard players operation " + config.NAMESPACE + " " + dst_reg.value + " /= " + config.NAMESPACE + " bin_tmp")
    
    return ret


def sll(dst_reg, src_reg, imm):
    ret = []
    if config.DEBUG:
        ret.append("#sll: " + str(dst_reg) + " " + str(src_reg) + " " + str(imm))

    ret.append("scoreboard players set " + config.NAMESPACE + " bin_tmp " + str(pow(2, int(imm))))
    ret.append("scoreboard players operation " + config.NAMESPACE + " " + dst_reg.value + " = " + config.NAMESPACE + " " + src_reg.value)
    ret.append("scoreboard players operation " + config.NAMESPACE + " " + dst_reg.value + " *= " + config.NAMESPACE + " bin_tmp")
    
    return ret


def syscall():
    ret = []
    if config.DEBUG:
        ret.append("#syscall")

    ret.append("function " + config.NAMESPACE + ":syscalls/syscall")

    return ret


def andOp(dst_reg, src_reg1, src_reg2):
    ret = []
    if config.DEBUG:
        ret.append("#and: " + str(dst_reg) + " " + str(src_reg1) + " " + str(src_reg2))

    ret += convertToBin("1", src_reg1)
    ret += convertToBin("2", src_reg2)
    for i in range(32):
        ret.append("scoreboard players operation " + config.NAMESPACE + " bin1_" + str(i) + " *= " + config.NAMESPACE + " bin2_" + str(i))

    ret += convertToDec(dst_reg, "1")

    return ret


def orOp(dst_reg, src_reg1, src_reg2):
    ret = []
    if config.DEBUG:
        ret.append("#or: " + str(dst_reg) + " " + str(src_reg1) + " " + str(src_reg2))

    ret += convertToBin("1", src_reg1)
    ret += convertToBin("2", src_reg2)
    for i in range(32):
        ret.append("scoreboard players operation " + config.NAMESPACE + " bin1_" + str(i) + " += " + config.NAMESPACE + " bin2_" + str(i))
        ret.append("execute if score " + config.NAMESPACE + " bin1_" + str(i) + " matches 2 run scoreboard players set " + config.NAMESPACE + " bin1_" + str(i) + " 1")

    ret += convertToDec(dst_reg, "1")

    return ret


def xorOp(dst_reg, src_reg1, src_reg2):
    ret = []
    if config.DEBUG:
        ret.append("#or: " + str(dst_reg) + " " + str(src_reg1) + " " + str(src_reg2))

    ret += convertToBin("1", src_reg1)
    ret += convertToBin("2", src_reg2)
    for i in range(32):
        ret.append("scoreboard players set " + config.NAMESPACE + " bin3_" + str(i) + " 1")
        ret.append("execute if score " + config.NAMESPACE + " bin1_" + str(i) + " = " + config.NAMESPACE + " bin2_" + str(i) + " run scoreboard players set " + config.NAMESPACE + " bin3_" + str(i) + " 0")

    ret += convertToDec(dst_reg, "3")

    return ret


ops = {
    "move": Op([ArgType.REGISTER, ArgType.REGISTER], move),

    "add": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.REGISTER], add),
    "addi": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.IMMEDIATE], addi),
    "sub": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.REGISTER], sub),
    "subi": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.IMMEDIATE], subi),

    "li": Op([ArgType.REGISTER, ArgType.IMMEDIATE], li),
    "la": Op([ArgType.REGISTER, ArgType.LABEL], la),

    "blt": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.LABEL], blt, True),
    "ble": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.LABEL], ble, True),
    "bgt": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.LABEL], bgt, True),
    "bge": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.LABEL], bge, True),
    "beq": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.LABEL], bge, True),
    "j": Op([ArgType.LABEL], j, True),
    "syscall": Op([], syscall, True),

    "lb": Op([ArgType.REGISTER, ArgType.ADDRESS], lb),
    "sb": Op([ArgType.REGISTER, ArgType.ADDRESS], sb),

    "and": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.REGISTER], andOp),
    "or": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.REGISTER], orOp),
    "xor": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.REGISTER], xorOp),

    "sll": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.IMMEDIATE], sll), # not tested
    "sra": Op([ArgType.REGISTER, ArgType.REGISTER, ArgType.IMMEDIATE], sra), # not tested
}
   

regs = {
    "$0": "zero",

    "$t0": "t0",
    "$t1": "t1",
    "$t2": "t2",
    "$t3": "t3",

    "$v0": "v0",
    "$2": "v0",

    "$3": "v1",

    "$a0": "a0",
    "$4": "a0",

    "$a1": "a1",
    
    "$sp": "sp",
    "$29": "sp",

    "$fp": "fp",
    "$30": "fp",

    "$ra": "ra",
    "$31": "ra"
}


def generateRegs():
    ret = []

    for v in set(regs.values()):
        ret.append("scoreboard objectives add " + v + " dummy")
        ret.append("scoreboard players set " + config.NAMESPACE + " " + v + " 0")

    return ret

