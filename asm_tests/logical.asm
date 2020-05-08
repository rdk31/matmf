.text
main:

    li $t0, 123
    li $t1, 45
    and $a0, $t0, $t1

    li $v0, 1
    syscall

    or $a0, $t0, $t1
    syscall

    xor $a0, $t0, $t1
    syscall

