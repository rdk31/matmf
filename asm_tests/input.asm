.data
str1: .asciiz "enter char"
str2: .asciiz "entered char"
str3: .asciiz "enter string"
str4: .asciiz "entered string"
text: .space 10
.text
main:

    li $v0, 4
    la $a0, str1
    syscall

    li $v0, 12
    syscall

    move $t0, $v0

    li $v0, 4
    la $a0, str2
    syscall

    move $a0, $t0
    li $v0, 11
    syscall

    li $v0, 4
    la $a0, str3
    syscall

    li $v0, 8
    la $a0, text
    li $a1, 9
    syscall

    li $v0, 4
    la $a0, str4
    syscall

    li $v0, 4
    la $a0, text
    syscall


