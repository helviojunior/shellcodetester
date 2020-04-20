
#include<stdio.h>
#include<string.h>
#include<windows.h>

//Compilando
//gcc.exe -c runner64.c 
//gcc.exe -shared -o runner64.dll runner64.o -m64

__declspec(dllexport) void __cdecl RunShellcode(char** code, int size){
	
	char shellcode[size];

	DWORD l=0;
	
	memcpy(shellcode, code, size);
	
	VirtualProtect(shellcode,size,PAGE_EXECUTE_READWRITE,&l);
	
	(*  (int(*)()) shellcode    ) ();
}

