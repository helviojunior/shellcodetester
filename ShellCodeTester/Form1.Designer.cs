namespace ShellCodeTester
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            this.label1 = new System.Windows.Forms.Label();
            this.txtShellcode = new System.Windows.Forms.TextBox();
            this.btnExecute = new System.Windows.Forms.Button();
            this.cbBreakpoint = new System.Windows.Forms.CheckBox();
            this.sbStatus = new System.Windows.Forms.StatusStrip();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(7, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(54, 13);
            this.label1.TabIndex = 0;
            this.label1.Text = "Shellcode";
            // 
            // txtShellcode
            // 
            this.txtShellcode.Location = new System.Drawing.Point(12, 25);
            this.txtShellcode.Multiline = true;
            this.txtShellcode.Name = "txtShellcode";
            this.txtShellcode.Size = new System.Drawing.Size(655, 195);
            this.txtShellcode.TabIndex = 1;
            // 
            // btnExecute
            // 
            this.btnExecute.Location = new System.Drawing.Point(592, 226);
            this.btnExecute.Name = "btnExecute";
            this.btnExecute.Size = new System.Drawing.Size(75, 23);
            this.btnExecute.TabIndex = 2;
            this.btnExecute.Text = "Executar";
            this.btnExecute.UseVisualStyleBackColor = true;
            this.btnExecute.Click += new System.EventHandler(this.btnExecute_Click);
            // 
            // cbBreakpoint
            // 
            this.cbBreakpoint.AutoSize = true;
            this.cbBreakpoint.Location = new System.Drawing.Point(351, 230);
            this.cbBreakpoint.Name = "cbBreakpoint";
            this.cbBreakpoint.Size = new System.Drawing.Size(235, 17);
            this.cbBreakpoint.TabIndex = 3;
            this.cbBreakpoint.Text = "Adicionar um Breakpoint antes do Shellcode";
            this.cbBreakpoint.UseVisualStyleBackColor = true;
            // 
            // sbStatus
            // 
            this.sbStatus.Location = new System.Drawing.Point(0, 262);
            this.sbStatus.Name = "sbStatus";
            this.sbStatus.Size = new System.Drawing.Size(679, 22);
            this.sbStatus.TabIndex = 4;
            this.sbStatus.Text = "statusStrip1";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(679, 284);
            this.Controls.Add(this.sbStatus);
            this.Controls.Add(this.cbBreakpoint);
            this.Controls.Add(this.btnExecute);
            this.Controls.Add(this.txtShellcode);
            this.Controls.Add(this.label1);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "Form1";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Form1";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox txtShellcode;
        private System.Windows.Forms.Button btnExecute;
        private System.Windows.Forms.CheckBox cbBreakpoint;
        private System.Windows.Forms.StatusStrip sbStatus;
    }
}

