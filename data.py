import config



class DataType:
    ASCIIZ = "asciiz"
    SPACE = "space"

class Data:
    addr = 0
    dataType = None
    param = None
    size = 0

    def __init__(self, dataType, param):
        self.addr = 0
        if dataType == ".asciiz":
            self.dataType = DataType.ASCIIZ
            self.param = param[1:-1]
            self.size = len(self.param) + 1
        elif dataType == ".space":
            self.dataType = DataType.SPACE
            self.param = param
            self.size = int(self.param)

    def generate(self):
        ret = []

        if self.dataType == DataType.ASCIIZ:
            for c in self.param:
                if c in config.SUPPORTED_CHARACTERS:
                    ret.append(ord(c))
                else:
                    raise Exception("unsupported character:", c)

            ret.append(0)

        elif self.dataType == DataType.SPACE:
            ret = [0 for j in range(int(self.param))]

        return ret

    def __str__(self):
        return self.dataType + " " + self.param