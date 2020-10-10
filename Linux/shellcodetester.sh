#!/bin/bash
#

echo "Shellcode Tester v1.2"

if [ $# -eq 0 ]
  then
    echo 
    echo "Utilização: shellcodetester [arquivo.asm] --break-point"
    echo 
    exit 1
fi

gcc_flags=""
filename=$(basename -- "$1")
extension="${filename##*.}"
filename2="${filename%%.*}"
c_file="$filename2-shellcodetester.c"
o_file="$filename2-shellcodetester.o"
bin_file="$filename2-shellcodetester"
bp=""

for arg in "$@"; do
    if [ "$arg" == "--break-point" ]; then
        echo "Adicionando breakpoint antes do shellcode"
        bp="0xCC,"
    fi
done


bits64=$(grep -i '\[BITS 64\]' "$1")
if [ $? -eq 0 ]; then
    bits64=1
else 
    bits64=0
fi

if [ $bits64 -eq 1 ]; then
    echo "Arquiterura: 64 bits"
else
    echo "Arquiterura: 32 bits"
    gcc_flags=" -m32 "
fi

echo "Montando arquivo '$filename' em $o_file"
rm -rf /tmp/sct.o >/dev/null 2>&1
nasm $1 -o $o_file

if [ $? -ne 0 ]; then
    echo
    echo "Erro montando arquivo .asm"
    exit 1
fi

echo "Gerando arquivo $c_file"


cat << EOF > $c_file
#include<stdio.h>
#include<string.h>
#include <sys/mman.h>

unsigned char code[] = {
EOF

echo -n "$bp" >> $c_file

cat $o_file | xxd --include >> $c_file

cat << EOF >> $c_file 
};

void main()
{

    char *shell;
    int size = sizeof(code);
    printf("Shellcode Length:  %d\n", size);

    shell = (char*)mmap(NULL, size, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_ANON|MAP_SHARED, -1, 0);

    memcpy(shell,code,size);

    int (*ret)() = (int(*)())shell;

    ret();

}
EOF

l=$(cat $o_file | wc -c)
t_payload=$(cat $o_file | xxd -p | tr -d '\n')
l2=${#t_payload}

payload=""
i=0
while [ $i -le $l2 ]
do
    hex=${t_payload:i:2}
    if [ "$hex" == "00" ]; then
        payload="$payload\033[0;31m00\033[0m"
    else
        payload="$payload$hex"
    fi
    i=$(( $i + 2 ))
done

echo "Compilando arquivo $c_file para $bin_file"
gcc $c_file -o $bin_file $gcc_flags -fno-stack-protector -z execstack
if [ $? -eq 0 ]; then
    echo "Montagem e compilação realizada com sucesso."
    echo
    echo "Tamanho do Payload: $l bytes"
    echo "Tamanho do Payload: Tamanho final em hexa: $l2 bytes"
    echo -e "$payload"
    echo
    echo "Execute o comando ./$bin_file"
    echo 
else
    echo
    echo "Erro na compilação!" 
fi
