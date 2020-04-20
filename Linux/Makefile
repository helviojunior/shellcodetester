# Instala shellcode tester no ambiente atual
ifeq ($(PREFIX),)
    PREFIX := /usr/local
endif

install:
	@ echo '[+] Instalando Shellcode Tester...'
	@ echo '    Copiando aplicação para $(PREFIX)/bin/'
	@ cp shellcodetester.sh $(PREFIX)/bin/shellcodetester
	@ chmod 777 $(PREFIX)/bin/shellcodetester
	@ echo '[+] Aplicação instalada'
	@ echo ' '
	@ echo 'Utilização: shellcodetester arquivo.asm'
	@ echo ' '

uninstall:
	@ echo 'Removendo Shellcode Tester...'
	@ rm -rf $(PREFIX)/bin/shellcodetester

.PHONY: install