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
using System.Text.RegularExpressions;

namespace ShellCodeTester
{
    public partial class Form1 : Form
    {
        private UInt32 pageSize = 0;
        OpenFileDialog openFileDialog1 = new OpenFileDialog();

        public Form1()
        {
            InitializeComponent();

            //
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.ControlBox = true;
            this.MinimizeBox = true;
            this.MaximizeBox = false;

            System.Reflection.Assembly assembly = System.Reflection.Assembly.GetExecutingAssembly();
            FileVersionInfo fvi = FileVersionInfo.GetVersionInfo(assembly.Location);
            string version = fvi.FileMajorPart + "." + fvi.FileMinorPart;

            this.Text = "M4v3r1ck ShellCode Tester v" + version;

            pageSize = GetPageSize(); //Minimum allocation size
        }

        public List<Byte> StringToByteArray(string hex)
        {
            return Enumerable.Range(0, hex.Length)
                             .Where(x => x % 2 == 0)
                             .Select(x => Convert.ToByte(hex.Substring(x, 2), 16)).ToList<Byte>();
        }

        private void btnExecute_Click(object sender, EventArgs e)
        {
            
            this.Enabled = false;
            this.BtnDisassemble_Click(sender, e);
            try
            {
                if (String.IsNullOrEmpty(txtShellcode.Text.Trim()))
                {
                    MessageBox.Show("Favor informar o Shellcode", "Alerta!", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }

                List<Byte> shellcode = new List<byte>();

                if (cbAlighStack.Checked){
                    UInt32 len = (UInt32)txtShellcode.Text.Length;
                    len += 9;

                    if (rb64Bits.Checked)
                    {
                        //Calcula alinhamento em 16 bits para que o shellcode funcione corretamente em 64 bits
                        //seguindo a calling convention
                        len += 32;
                        byte[] getRIP = { 0xeb, 0x05, 0x48, 0x8b, 0x04, 0x24, 0xc3, 0xe8, 0xf6, 0xff, 0xff, 0xff };
                        byte[] movRSPEAX = { 0x48, 0x89, 0xC4 };
                        byte[] align = { 0x48, 0x83, 0xE0, 0xF0 };
                        shellcode.AddRange(getRIP);
                        shellcode.Add(0x05); //ADD EAX
                        shellcode.AddRange(BitConverter.GetBytes(len)); //Size to be added
                        shellcode.AddRange(align); //and rax, 0xFFFFFFFFFFFFFFF0 ; Ensure RSP is 16 byte aligned
                        shellcode.AddRange(movRSPEAX);
                    }
                    else
                    {
                        byte[] getEIP = { 0xeb, 0x04, 0x8b, 0x04, 0x24, 0xc3, 0xe8, 0xf7, 0xff, 0xff, 0xff };
                        byte[] movESPEAX = { 0x89, 0xc4 };
                        shellcode.AddRange(getEIP);
                        shellcode.Add(0x05); //ADD EAX
                        shellcode.AddRange(BitConverter.GetBytes(len)); //Size to be added
                        shellcode.AddRange(movESPEAX);
                    }

                }


                if (cbBreakpoint.Checked)
                    shellcode.Add(0xCC);

                try
                {
                    txtShellcode.Text = ExtractHexDigits(txtShellcode.Text);
                    shellcode.AddRange(StringToByteArray(txtShellcode.Text));
                }
                catch
                {
                    shellcode.Clear();
                }

                if (shellcode.Count == 0)
                {
                    MessageBox.Show("Erro ao realizar o parse do Shellcode", "Erro!", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    return;
                }

                if (shellcode.Count  > pageSize)
                {
                    MessageBox.Show("Tamanho máximo do Shellcode permitido é " + pageSize + " bytes", "Erro!", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    return;
                }

                sbStatus.Text = "Executando shellcode, aguarde...";

                Execute(shellcode.ToArray(), cbBreakpoint.Checked);
            }
            finally
            {
                sbStatus.Text = "";
                this.Enabled = true;
            }
        }

        private void Execute(Byte[] payload, Boolean debug = false)
        {
            System.Reflection.Assembly asm = System.Reflection.Assembly.GetExecutingAssembly();
            String path = Path.GetDirectoryName(asm.Location);

            Process p = new Process();
            p.StartInfo.UseShellExecute = true;
            //p.StartInfo.RedirectStandardOutput = true;
            //p.StartInfo.RedirectStandardError = true;
            if (rb64Bits.Checked)
            {
                p.StartInfo.FileName = Path.Combine(path, "Runner64.exe");
            }
            else
            {
                p.StartInfo.FileName = Path.Combine(path, "Runner.exe");
            }
            p.StartInfo.Arguments = BitConverter.ToString(payload).Replace("-","");

            if (debug)
                p.StartInfo.Arguments += " --debug";
            p.Start();

            p.WaitForExit();

        }
        
        UInt32 GetPageSize()
        {
            SYSTEM_INFO info;
            GetSystemInfo(out info);

            return info.AllocationGranularity;
        }

        public static string ExtractHexDigits(string input)
        {
            // remove any characters that are not digits (like #)
            Regex isHexDigit
               = new Regex("[abcdefABCDEF\\d]+", RegexOptions.Compiled);
            string newnum = "";
            foreach (char c in input)
            {
                if (isHexDigit.IsMatch(c.ToString()))
                    newnum += c.ToString();
            }
            return newnum;
        }


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

        private void AboutToolStripMenuItem_Click(object sender, EventArgs e)
        {

        }

        private void OpenToolStripMenuItem_Click(object sender, EventArgs e)
        {
           
            this.openFileDialog1 = new System.Windows.Forms.OpenFileDialog();
            this.openFileDialog1.FileName = "";
            DialogResult res = this.openFileDialog1.ShowDialog();
            if (res == DialogResult.OK)
            {
                try
                {
                    byte[] fileBytes = File.ReadAllBytes(this.openFileDialog1.FileName);
                    String sData = BitConverter.ToString(fileBytes).Replace("-","");
                    txtShellcode.Text = sData;
                }
                catch(Exception ex)
                {
                    MessageBox.Show("Erro carregando o arquivo: " + ex.Message, "Erro!", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    return;
                }
            }
        }

        private void TxtShellcode_TextChanged(object sender, EventArgs e)
        {
            
        }

        private void BtnDisassemble_Click(object sender, EventArgs e)
        {
            System.Reflection.Assembly asm = System.Reflection.Assembly.GetExecutingAssembly();
            String path = Path.GetDirectoryName(asm.Location);

            FileInfo tmpFile = new FileInfo(Path.Combine(Path.GetTempPath(), "ShellcodeTester.o"));

            List<Byte> shellcode = new List<byte>();
            try
            {
                shellcode.AddRange(StringToByteArray(txtShellcode.Text));
            }
            catch
            {
                shellcode.Clear();
            }

            if (shellcode.Count > 0)
            {
                File.WriteAllBytes(tmpFile.FullName, shellcode.ToArray());

                Process p = new Process();
                p.StartInfo.UseShellExecute = false;
                p.StartInfo.RedirectStandardOutput = true;
                p.StartInfo.RedirectStandardError = true;
                p.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;

                p.StartInfo.FileName = Path.Combine(path, "objdump.exe");
                if (rb64Bits.Checked)
                {
                    p.StartInfo.Arguments = "objdump -D -Mintel,x86-64 -b binary -m i386 \"" + tmpFile.FullName + "\"";
                }
                else
                {
                    p.StartInfo.Arguments = "objdump -D -Mintel,i386 -b binary -m i386 \"" + tmpFile.FullName + "\"";
                }

                p.Start();
                string output = p.StandardOutput.ReadToEnd();

                Int32 offset = output.IndexOf("<.data>:");
                if (offset > 0)
                {
                    output = output.Substring(offset + 8).TrimStart("\r\n".ToCharArray());
                }

                p.WaitForExit();
               
                txtdisassemble.Text = output;
            }
            else
            {
                txtdisassemble.Text = "Shellcode vazio";
            }

        }

        private void ToolStripMenuItem1_Click(object sender, EventArgs e)
        {

            System.Reflection.Assembly assembly = System.Reflection.Assembly.GetExecutingAssembly();
            FileVersionInfo fvi = FileVersionInfo.GetVersionInfo(assembly.Location);
            string version = fvi.FileMajorPart + "." + fvi.FileMinorPart + "." + fvi.FilePrivatePart; ;

            StringBuilder str = new StringBuilder();
            str.AppendLine("Shellcode Tester criado por M4v3r1ck");
            str.AppendLine("Versão: " + version);
            str.AppendLine("helvio_junior [at] hotmail [dot] com");

            str.AppendLine("");
            str.AppendLine("Disasseble utilizando ObjDump do GNU");
            str.AppendLine("http://www.gnu.org/software/binutils/");


            Form2 frm = new Form2();
            frm.Text = this.Text;
            frm.SetText(str.ToString());
            frm.ShowDialog();
        }
    }
}
