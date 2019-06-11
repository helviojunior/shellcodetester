using System;
using System.Collections.Generic;
using System.Windows.Forms;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security;

namespace Runner
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main(string[] args)
        {
            System.Windows.Forms.Application.SetUnhandledExceptionMode(UnhandledExceptionMode.CatchException);
            System.Windows.Forms.Application.ThreadException += new System.Threading.ThreadExceptionEventHandler(OnGuiUnhandedException);
            AppDomain.CurrentDomain.UnhandledException += new UnhandledExceptionEventHandler(CurrentDomain_UnhandledException);
            SetUnhandledExceptionFilter(Win32Handler);

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Form1(args));
        }

        [SecurityCritical]
        static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            Process.GetCurrentProcess().Kill();
        }


        private static void OnUnhandledException(Object sender, UnhandledExceptionEventArgs e)
        {
            Process.GetCurrentProcess().Kill();
        }

        private static void OnGuiUnhandedException(object sender, System.Threading.ThreadExceptionEventArgs e)
        {
            Process.GetCurrentProcess().Kill();
        }

        static int Win32Handler(IntPtr nope)
        {
            //MessageBox.Show("Native uncaught SEH exception"); // show + report or whatever
            Environment.Exit(-1); // exit and avoid WER etc
            return 1; // thats EXCEPTION_EXECUTE_HANDLER, although this wont be called due to the previous line
        }

        [DllImport("kernel32.dll")]
        static extern FilterDelegate SetUnhandledExceptionFilter(FilterDelegate lpTopLevelExceptionFilter);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        delegate int FilterDelegate(IntPtr exception_pointers);

    }
}
