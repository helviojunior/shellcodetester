; Arquivo pertencente ao treinamento de Shellcoding
; Autor: Hélvio Junior (M4v3r1ck)
;
; Proibida a reprodução ou publicação deste material sem prévia autorização expressa
;
;Filename: execve3.asm
;
;Procedimento de montagem
; shellcodetester --writable-text -asm execve3.asm


[BITS 32]

global _start

section .text

_start:
    jmp step1

step2:
                                ; Realiza o syscall para a função execve
                                ; para isso adiciona o número do syscall correspondente em EAX
                                ; Para busca da tabela de números de syscall correspondente está disponível em:
                                ;     32-bit: /usr/include/x86_64-linux-gnu/asm/unistd_32.h
                                ;     64-bit: /usr/include/x86_64-linux-gnu/asm/unistd_64.h
                                ;
                                ; A Listagem de funções syscall pode ser visualizada com o comando: "man 2 syscalls"
                                ; e posteriormente o detalhe de cada função com o comando: "man 2 execve"
                                ;
                                ; Definição da função:
                                ; int execve(const char *pathname, char *const argv[], char *const envp[]);
                                ;
                                ; Onde ficará execve(&'/bin/sh', &'{ &"/bin/sh", &NULL }', &NULL):
                                ;     EAX <= 11 (__NR_execve)
                                ;     EBX <= &string (Ponteiro/endereço de memória do comando /bin/sh)
                                ;     ECX <= &array (Ponteiro/endereço de memória do array)
                                ;     EDX <= &array (Ponteiro/endereço de memória do array)
                                ;

                                ; Retira da pilha o endereço de memória (ponteiro) do texto
                                ; o qual será manipulado para edição dos NULL bytes e endereços
    pop ebx                     ; Copia para EBX o endereço do texto

                                ; Primeiro parâmetro (EBX):
                                ;     Como o texto ja está no registrador EBX, basta alterar o oitavo caractere 
                                ;     que atualmente está como 0x01 para 0x00
    xor eax,eax                 ;     Zera EAX 
    mov [ebx + 7], al


                                ; Segundo parâmetro (ECX)
                                ;     O array é composto de 2 endereços
                                ;       1 - Endereço do /bin/sh
                                ;       2 - Endereço do NULL
    push eax                    ;     Insere null byte na pilha
    push ebx                    ;     Insere o endereço do /bin/sh
    mov ecx,esp                 ;     Copia o endereço do topo da pilha (onde o array) para ecx


                                ; Terceiro parametro (EDX)
                                ;     Insere o NULL na pilha e copia o endereço do mesmo para edx
    push eax                    ;     Insere null byte na pilha
    mov edx, esp                ;     Copia o endereço do topo da pilha (onde o NULL byte está) para edx


                                ; Código do Syscall para execv
                                ; Zera EAX e posteriormente move o valor 4 para o registrador
    xor eax,eax                 ; Zera EAX
    mov al, 11                  ; Move o 0x0b para o byte menos significativo em EAX o que corresponde a execve (syscall 11)

    int 0x80                    ; Executa o syscall do "execve"

                                ; Sai da aplicação sem aprentar erro
    xor eax, eax                ; Zera EAX 
    mov al, 1                   ; syscall "exit" é 1
    xor ebx, ebx                ; Zera EBX (exit code = 0)
    mov bl, 1                   ; status como 1
    int 0x80                    ; Executa o syscall do "exit" 

step1:
    call step2
    db "/bin/ls", 0x01
