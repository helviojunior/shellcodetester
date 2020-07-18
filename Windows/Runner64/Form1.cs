using System;
using System.Collections.Generic;
using System.Windows.Forms;
using System.Diagnostics;
using RunnerLib;

namespace Runner
{
    public partial class Form1 : Form
    {
        private String[] args;

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

            Process currentProcess = Process.GetCurrentProcess();
            Int32 pid = currentProcess.Id;

            this.Enabled = false;
            try
            {
                Boolean debug = false;

                if (args == null || args.Length == 0 || String.IsNullOrEmpty(args[0].Trim()))
                {
                    MessageBox.Show("Favor informar o Shellcode", "Alerta!", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }

                if (args.Length > 1)
                {
                    foreach (String a in args)
                    {
                        if (a.ToLower() == "--debug")
                            debug = true;
                    }
                }

                List<Byte> shellcode = new List<byte>();

                try
                {
                    shellcode.AddRange(Run.StringToByteArray(args[0].Trim().Replace("\r", "").Replace("\n", "").Replace(" ", "").Replace("0x", "").Replace(",", "")));
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

                /*
                if (shellcode.Count > pageSize)
                {
                    MessageBox.Show("Tamanho máximo do Shellcode permitido é " + pageSize + " bytes", "Erro!", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    return;
                }*/

                if (shellcode[0] == 0xcc)
                    debug = true;

                if (debug)
                    MessageBox.Show("Breakpoint ativado. Anexe o debugger 64 bits ao PID " + pid + " e pressione OK para continuar.", "Aguardando...", MessageBoxButtons.OK, MessageBoxIcon.Information);

                Run.Execute(shellcode.ToArray());
            }
            finally
            {
                this.Enabled = true;
            }

        }


    }
}
