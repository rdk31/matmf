.data
stack: .space 20
.text
main:
    li $t0, 0
    li $t1, 97
    sb $t1, ($t0)
    li $t1, 98
    sb $t1, 1($t0)
    li $t1, 99
    sb $t1, 2($t0)
    li $t1, 100
    sb $t1, 3($t0)
    li $t1, 0
    sb $t1, 4($t0)

    move $a0, $t0
    li $v0, 4
    syscall