.data
info: .asciiz "fib sequence"
.text
main:

	li $v0, 4
	la $a0, info
	syscall

	li $t0, 1
	li $t1, 0
	li $t3, 100

	loop:
		li $t2, 0
	
		add $t2, $t0, $t1
		move $t0, $t1
		move $t1, $t2
	
		li $v0, 1
		move $a0, $t2
		syscall
	
		blt $t2, $t3, loop
	
	li $v0, 10
	syscall
