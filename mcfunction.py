import config



class McFunction:

    def __init__(self, num = 0, label = ""):
        self.number = num
        self.label = label
        self.body = []
        if num != 0:
            self.addLine("scoreboard players set " + config.NAMESPACE + " next 0\n")

    def addLine(self, line):
        self.body.append(line)

    def addLines(self, lines):
        self.body += lines

    def generate(self):
        return self.body
