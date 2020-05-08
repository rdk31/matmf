import os
import string
import re
import shutil

import config
import ops
import core
import syscalls
from data import Data
from mcfunction import McFunction

    

class Compiler:
    mcfunctions = {}
    data = {}

    fileBuffer = []

    funcNum = 0



    def __init__(self):
        pass


    def newFuncNum(self):
        self.funcNum += 1
        return self.funcNum


    def newFuncLabel(self, label):
        m = re.match(r"^([a-zA-Z]\w*)\_{1}(\d+$)", label)
        baseLabel = label
        num = 0
        if m:
            baseLabel = m.group(1)
            num = int(m.group(2))

        return baseLabel + "_" + str(num + 1)


    def parseText(self):
        currFunc = None
        currSeg = ""

        for line in self.fileBuffer:
            if line == ".text":
                currSeg = "text"
            elif line == ".data":
                currSeg = "data"
            else:
                if currSeg == "text":
                    print("parsing:", line)

                    m = re.match(r"^([a-zA-Z]\w*)\:$", line)
                    if m: # label
                        if currFunc is not None:
                            currFunc.addLine("scoreboard players set " + config.NAMESPACE + " next " + str(self.mcfunctions["app/" + m.group(1)].number))

                        currFunc = self.mcfunctions["app/" + m.group(1)]
                    else:
                        cmd = line.split(" ", 1)
                        name = cmd[0]
                        args = []
                        if len(cmd) > 1:
                            args = cmd[1].split(",")

                        parsedArgs = ops.parseArgs(args)
                        parsedArgsTypes = [arg.argType for arg in parsedArgs]
                        parsed = False
                        for k, v in ops.ops.items():
                            if k == name:
                                if v.argTypes == parsedArgsTypes:
                                    for arg in parsedArgs:
                                        if arg.argType == ops.ArgType.REGISTER:
                                            if arg.value in ops.regs:
                                                arg.value = ops.regs[arg.value]
                                            else:
                                                raise Exception("unsupported register:", arg.value)
                                        
                                        elif arg.argType == ops.ArgType.LABEL:
                                            if "app/" + arg.value in self.mcfunctions:
                                                arg.value = str(self.mcfunctions["app/" + arg.value].number)
                                            elif arg.value in self.data:
                                                arg.value = str(self.data[arg.value].addr)
                                            else:
                                                raise Exception("label not found:", arg.value)

                                        elif arg.argType == ops.ArgType.ADDRESS:
                                            if arg.value in ops.regs:
                                                arg.value = ops.regs[arg.value]
                                            else:
                                                raise Exception("unsupported register:", arg.value)
                                    
                                    newFunc = None

                                    if v.branchOut:
                                        newLabel = self.newFuncLabel(currFunc.label)
                                        newFunc = McFunction(self.newFuncNum(), newLabel)
                                        self.mcfunctions["app/" + newLabel] = newFunc
                                        currFunc.addLine("scoreboard players set " + config.NAMESPACE + " next " + str(newFunc.number))

                                    currFunc.addLines(v.generate(parsedArgs))

                                    if v.branchOut:
                                        currFunc = newFunc

                                    parsed = True
                                    break

                                else:
                                    raise Exception("op:", name, "wrong arguments:", parsedArgsTypes, "should be:", v.argTypes)
                        
                        if not parsed:
                            raise Exception("cannot parse op:", name)

                        print()


    def generateDatapack(self):
        shutil.rmtree(config.NAMESPACE, ignore_errors=True)

        os.makedirs(config.NAMESPACE + "\\data\\" + config.NAMESPACE + "\\functions", exist_ok=True)
        os.makedirs(config.NAMESPACE + "\\data\\" + config.NAMESPACE + "\\functions\\app", exist_ok=True)
        os.makedirs(config.NAMESPACE + "\\data\\" + config.NAMESPACE + "\\functions\\syscalls", exist_ok=True)
        os.makedirs(config.NAMESPACE + "\\data\\" + config.NAMESPACE + "\\functions\\input", exist_ok=True)
        os.makedirs(config.NAMESPACE + "\\data\\minecraft\\tags\\functions", exist_ok=True)

        with open(config.NAMESPACE + "\\pack.mcmeta", "w") as f:
            f.write("{\"pack\":{\"pack_format\":1,\"description\":\"" + config.NAMESPACE + "\"}}\n")

        with open(config.NAMESPACE + "\\data\\minecraft\\tags\\functions\\load.json", "w") as f:
            f.write("{\"values\":[\"" + config.NAMESPACE + ":load\"]}\n")

        with open(config.NAMESPACE + "\\data\\minecraft\\tags\\functions\\tick.json", "w") as f:
            f.write("{\"values\":[\"" + config.NAMESPACE + ":tick\"]}\n")

        for k, v in self.mcfunctions.items():
            with open(config.NAMESPACE + "\\data\\" + config.NAMESPACE + "\\functions\\" + k + ".mcfunction", "w") as f:
                body = v.generate()
                for line in body:
                    f.write(line + "\n")

    
    def generateTick(self):
        func = McFunction()

        for k, v in self.mcfunctions.items():
            if v.number != 0:
                func.addLine("execute if score " + config.NAMESPACE + " next matches " + str(v.number) + " run function " + config.NAMESPACE + ":" + k)

        self.mcfunctions["tick"] = func


    def generateRam(self):
        if config.RAM_DEPTH < 2:
            raise Exception("RAM DEPTH >= 2")

        ramSize = pow(config.RAM_BLOCK_SIZE, config.RAM_DEPTH)

        ram = [0 for i in range(ramSize)]

        dataSize = 0
        for k, v in self.data.items():
            dataSize += v.size

        if dataSize > ramSize:
            raise Exception("NOT ENOUGH RAM")

        print("ram size:", ramSize)
        print("data size:", dataSize, "\n")

        dataAddr = 0
        for k, v in self.data.items():
            data = v.generate()
            for j in range(len(data)):
                ram[dataAddr + j] = data[j]
            
            v.addr = dataAddr
            dataAddr += v.size

        def node(depth, desired_depth):
            if depth == desired_depth:
                return "[]"
            else:
                ret = "["

                for i in range(config.RAM_BLOCK_SIZE):
                    ret += node(depth + 1, desired_depth) + ","

                ret = ret[:-1]
                ret += "]"
                return ret

        cmd = "data modify storage " + config.NAMESPACE + " ram set value " + node(0, config.RAM_DEPTH - 1)
        self.mcfunctions["load"].addLine(cmd)

        def numberToBase(n, b):
            if n == 0:
                return [0]
            digits = []
            while n:
                digits.append(int(n % b))
                n //= b
            return digits[::-1]

        for i in range(pow(config.RAM_BLOCK_SIZE, config.RAM_DEPTH - 1)):
            addr = ("{:0" + str(config.RAM_DEPTH - 1) + "x}").format(i)

            for j in range(config.RAM_BLOCK_SIZE):
                ret = "data modify storage " + config.NAMESPACE + " ram"
                for c in addr:
                    ret += "[" + str(int(c, config.RAM_BLOCK_SIZE)) + "]"

                ret += " append value " + str(ram[i * config.RAM_BLOCK_SIZE + j])
                self.mcfunctions["load"].addLine(ret)


    def generateCore(self):
        self.mcfunctions["load"] = core.generateLoad()

        func = McFunction()
        func.addLine("function tickbuster:api/vote/in")
        self.mcfunctions["start"] = func

        self.mcfunctions = { **self.mcfunctions, **syscalls.generateSyscalls(), **core.generateInputs()}


    def printLabels(self):
        print("labels:")
        for k, v in self.mcfunctions.items():
            if v.number != 0:
                print(k)

        print()

        print("data labels:")
        for k, v in self.data.items():
            print(k)

        print()


    def parseLabels(self):
        currSeg = ""
        for line in self.fileBuffer:
            if line == ".text":
                currSeg = "text"
            elif line == ".data":
                currSeg = "data"
            else:
                if currSeg == "text":
                    if line[-1] == ":": # label
                        label = line[:-1]
                        self.mcfunctions["app/" + label] = McFunction(self.newFuncNum(), label)

                elif currSeg == "data":
                    cmd = line.split(" ", 2)

                    if cmd[0][-1] == ":" and len(cmd) == 3: 
                        label = cmd[0][:-1]
                        self.data[label] = Data(cmd[1], cmd[2])

             
    def readFile(self, inputFile):
        with open(inputFile) as f:
            for line in f:
                line = re.sub(r"\s+", " ", line)
                line = line.strip()
                line = line.replace(", ", ",")

                if not line:
                    continue

                self.fileBuffer.append(line)


    def compile(self, inputFile):
        self.mcfunctions = {}
        self.data = {}
        self.fileBuffer = []
        self.funcNum = 0

        self.readFile(inputFile)
        self.parseLabels()
        self.printLabels()
        self.generateCore()
        self.generateRam()
        self.parseText()
        self.generateTick()
        self.generateDatapack()
      
      
