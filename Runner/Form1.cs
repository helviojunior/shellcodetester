using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Reflection;
using System.IO;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;

namespace Runner
{
    public partial class Form1 : Form
    {
        private String[] args;
        private UInt32 pageSize = 0;

        public Form1(string[] args)
        {
            this.args = args;
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.ControlBox = true;
            this.MinimizeBox = true;
            this.MaximizeBox = false;

            pageSize = GetPageSize(); //Minimum allocation size
            Process currentProcess = Process.GetCurrentProcess();
            Int32 pid = currentProcess.Id;

            this.Enabled = false;
            try
            {
                if (args == null || args.Length == 0 || String.IsNullOrEmpty(args[0].Trim()))
                {
                    MessageBox.Show("Favor informar o Shellcode", "Alerta!", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }

                List<Byte> shellcode = new List<byte>();

                try
                {
                    shellcode.AddRange(StringToByteArray(args[0].Trim().Replace("\r", "").Replace("\n", "").Replace(" ", "").Replace("0x", "").Replace(",", "")));
                }
                catch (Exception ex)
                {
                    shellcode.Clear();
                }

                if (shellcode.Count == 0)
                {
                    MessageBox.Show("Erro ao realizar o parse do Shellcode", "Erro!", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    return;
                }

                if (shellcode.Count > pageSize)
                {
                    MessageBox.Show("Tamanho máximo do Shellcode permitido é " + pageSize + " bytes", "Erro!", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    return;
                }

                if (shellcode[0] == 0xcc)
                    MessageBox.Show("Breakpoint ativado. Anexe o debugger ao PID " + pid + " e pressione OK para continuar.", "Aguardando...", MessageBoxButtons.OK, MessageBoxIcon.Information);

                Execute(shellcode.ToArray());
            }
            finally
            {
                this.Enabled = true;
            }

        }


        public List<Byte> StringToByteArray(string hex)
        {
            return Enumerable.Range(0, hex.Length)
                             .Where(x => x % 2 == 0)
                             .Select(x => Convert.ToByte(hex.Substring(x, 2), 16)).ToList<Byte>();
        }


        private void Execute(Byte[] payload)
        {

            UInt32 size = GetPageSize(); //Minimum allocation size

            if (payload.Length > size)
            {
                size = (UInt32)payload.Length;
            }

            byte[] shellcode = new byte[size];

            for (Int32 i = 0; i < shellcode.Length; i++)
            {
                shellcode[i] = 0x90;
            }

            Array.Copy(payload, 0, shellcode, 0, payload.Length);
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

        UInt32 GetPageSize()
        {
            SYSTEM_INFO info;
            GetSystemInfo(out info);

            return info.AllocationGranularity;
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
