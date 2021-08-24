#!/usr/bin/env bash
#
LANG=C
LC_ALL=C

#filename="${1%%.*}"
# Error messages array
error_msg[1]='Utilização: shellcodetester.sh [-f <arquivo.asm>] [-b <badchars>] [--break-point]'
error_msg[2]='Erro montando arquivo .asm'
error_msg[3]='Erro na compilação!'
error_msg[4]='Opcao Invalida! Usage: shellcodetester.sh [-f <arquivo.asm>] [-b <badchars>] [--break-point]'
error_msg[5]='Opcao requer um argumento'

#Error message function
error (){

  [[ $1 -eq 5 ]] && echo -e "\n\e[31;1m[!]\e[m Opcao -$2 requer argumento"
  [[ $1 -ne 5 ]] && echo -e "\n\e[31;1m[!]\e[m ${error_msg[$1]}\n"
  exit $1

}

while getopts ":f:b:h-:" opts; do

	case ${opts} in

		:) error 5 ${OPTARG}
		;;

		\?) error 4
		;;

		-)
			[[ ${OPTARG} == 'break-point' ]] && echo -e "\n\e[1mAdicionando breakpoint antes do shellcode\e[m" && bp='0xCC' || error 4
		;;

    h) error 1
    ;;

		f)
			filename="${OPTARG%%.*}"
			fullname="${OPTARG}"
			gcc_flags=""
			c_file="$filename-shellcodetester.c"
			o_file="$filename-shellcodetester.o"
			bin_file="$filename-shellcodetester.x"
			bp=""


bits64=$(grep -i '\[BITS 64\]' "$fullname")

if [[ $bits64 ]]; then
    echo "Arquitetura: 64 bits"
else
    echo "Arquitetura: 32 bits"
    gcc_flags=" -m32 "
fi

echo -e "Montando arquivo \e[32;1m$fullname\e[m em $o_file"
rm -rf /tmp/sct.o >/dev/null 2>&1
nasm $fullname -o $o_file

[[ $? -ne 0 ]] && error 2

echo -e "Gerando arquivo \e[4m$c_file\e[m"

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

echo -e "Compilando arquivo \e[4m$c_file\e[m para \e[32;1m$bin_file\e[m"
gcc $c_file -o $bin_file $gcc_flags -fno-stack-protector -z execstack

[[ $? -eq 0 ]] || erro 3

echo -e \
"Montagem e compilação realizada com sucesso.\n
Tamanho do Payload: $l bytes
Tamanho do Payload: Tamanho final em hexa: $l2 bytes\n"
		;;

		b)
			badchars=${OPTARG}
			echo $'\e[1mBadchars:\e[m '"${badchars}"''
			cat $o_file | xxd -p | tr -d '\n' | grep -E --color "${badchars//\\x/|}"
		;;

		esac
done
