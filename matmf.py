import compiler
import sys



if __name__ == "__main__":
    c = compiler.Compiler()
    c.compile(sys.argv[1])
