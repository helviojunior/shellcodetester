using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace ShellCodeTester
{
    public partial class Form2 : Form
    {
        public Form2()
        {
            InitializeComponent();
        }

        private void Form2_Load(object sender, EventArgs e)
        {
            this.Focus();
        }

        public void SetText(String text)
        {
            this.txtCredits.Text = text;
            this.txtCredits.Select(0, 0);
        }
    }
}
