format ELF64 executable
entry start
segment readable executable
start:
call main
mov rax, 60
mov rdi, 1
syscall
@print:
push rbp
mov rbp, rsp
mov rax, 1
mov rdi, 1
mov rsi, [rbp+16]
mov rdx, [rbp+24]
syscall
mov rsp, rbp
pop rbp
ret
main:
push rbp
mov rbp, rsp
call test1
add rsp, 0
push r8
push _0
call @print
add rsp, 16
mov rsp, rbp
pop rbp
ret
test1:
push rbp
mov rbp, rsp
push 10
pop r8
mov rsp, rbp
pop rbp
ret
mov rsp, rbp
pop rbp
ret
segment readable
_0: db "Hello, Nothing!", 10
