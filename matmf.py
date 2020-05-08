import compiler
import sys



if __name__ == "__main__":
    c = compiler.Compiler()

    if len(sys.argv) != 2:
        print("python matmf.py <file.asm>")
        sys.exit(1)

    c.compile(sys.argv[1])
