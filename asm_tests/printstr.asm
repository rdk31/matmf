.data
str: .asciiz "test 123 ABCD"
.text
main:
    la $a0, str

    li $v0, 4
    syscall
