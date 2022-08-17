format ELF64 executable
entry start
segment readable executable
start:
lea rax, [rsp+8]
push rax
call main
mov rax, 60
mov rdi, 0
syscall
main:
push rbp
mov rbp, rsp
sub rsp, 40
push 1
mov rax, [rsp+0]
mov [rbp-8], rax
add rsp, 8
mov rcx, [rbp+8]
mov rdx, [rbp]
mov rsp, rbp
add rsp, 16
push rdx
pop rbp
push rcx
ret
segment readable
segment readable writable
_tokens: rb 65536
_tokens_index: rb 8
