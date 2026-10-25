using System;
using System.IO;
using System.Diagnostics;
using System.Drawing;
using System.Net;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace ResearchForgeLauncher
{
    public class MainForm : Form
    {
        private Label lblTitle;
        private Label lblSubtitle;
        private Label lblApiStatus;
        private Label lblWebStatus;
        private Button btnLaunchBrowser;
        private Button btnApiDocs;
        private Button btnOpenLogs;
        private Button btnRestart;
        private TextBox txtRealtimeLogs;
        private System.Windows.Forms.Timer statusTimer;
        private System.Windows.Forms.Timer logTimer;
        
        private string projectRoot;
        private long lastLogPosition = 0;
        private Process apiProcess = null;
        private Process webProcess = null;

        public MainForm()
        {
            InitializeComponent();
            DetermineProjectRoot();
            StartServicesIfNeeded();
            
            statusTimer = new System.Windows.Forms.Timer();
            statusTimer.Interval = 3000;
            statusTimer.Tick += (s, e) => CheckServicesStatus();
            statusTimer.Start();

            logTimer = new System.Windows.Forms.Timer();
            logTimer.Interval = 1000;
            logTimer.Tick += (s, e) => TailRealtimeLogs();
            logTimer.Start();

            CheckServicesStatus();
            TailRealtimeLogs();
        }

        private void InitializeComponent()
        {
            this.Text = "ResearchForge — Scholarly Literature & Synthesis Studio";
            this.Size = new Size(820, 600);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(249, 248, 246); // Warm Editorial cream background
            this.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);

            // Header Banner
            Panel topPanel = new Panel();
            topPanel.Dock = DockStyle.Top;
            topPanel.Height = 85;
            topPanel.BackColor = Color.FromArgb(38, 35, 32); // Deep espresso/charcoal
            this.Controls.Add(topPanel);

            lblTitle = new Label();
            lblTitle.Text = "RESEARCHFORGE STUDIO";
            lblTitle.Font = new Font("Georgia", 16f, FontStyle.Bold);
            lblTitle.ForeColor = Color.FromArgb(250, 246, 240);
            lblTitle.Location = new Point(24, 16);
            lblTitle.AutoSize = true;
            topPanel.Controls.Add(lblTitle);

            lblSubtitle = new Label();
            lblSubtitle.Text = "Grounded Evidence Synthesis · Inter-Rater Reliability · PRISMA 2020 · Lineage DAG";
            lblSubtitle.Font = new Font("Segoe UI", 9f, FontStyle.Regular);
            lblSubtitle.ForeColor = Color.FromArgb(190, 180, 170);
            lblSubtitle.Location = new Point(25, 48);
            lblSubtitle.AutoSize = true;
            topPanel.Controls.Add(lblSubtitle);

            // Status Section
            Panel statusPanel = new Panel();
            statusPanel.Location = new Point(24, 105);
            statusPanel.Size = new Size(755, 60);
            statusPanel.BackColor = Color.White;
            statusPanel.BorderStyle = BorderStyle.FixedSingle;
            this.Controls.Add(statusPanel);

            lblApiStatus = new Label();
            lblApiStatus.Text = "API Backend (Port 8000): Checking...";
            lblApiStatus.Location = new Point(20, 20);
            lblApiStatus.AutoSize = true;
            lblApiStatus.Font = new Font("Segoe UI", 10f, FontStyle.Bold);
            statusPanel.Controls.Add(lblApiStatus);

            lblWebStatus = new Label();
            lblWebStatus.Text = "Web Frontend (Port 5173): Checking...";
            lblWebStatus.Location = new Point(400, 20);
            lblWebStatus.AutoSize = true;
            lblWebStatus.Font = new Font("Segoe UI", 10f, FontStyle.Bold);
            statusPanel.Controls.Add(lblWebStatus);

            // Main Launch Button
            btnLaunchBrowser = new Button();
            btnLaunchBrowser.Text = "🚀  OPEN RESEARCHFORGE IN BROWSER (http://localhost:5173)";
            btnLaunchBrowser.Location = new Point(24, 180);
            btnLaunchBrowser.Size = new Size(755, 52);
            btnLaunchBrowser.BackColor = Color.FromArgb(142, 68, 173); // Regal Editorial Purple / Maroon
            btnLaunchBrowser.ForeColor = Color.White;
            btnLaunchBrowser.Font = new Font("Segoe UI", 11f, FontStyle.Bold);
            btnLaunchBrowser.FlatStyle = FlatStyle.Flat;
            btnLaunchBrowser.Cursor = Cursors.Hand;
            btnLaunchBrowser.Click += (s, e) => OpenUrl("http://localhost:5173");
            this.Controls.Add(btnLaunchBrowser);

            // Action Buttons Bar
            btnApiDocs = new Button();
            btnApiDocs.Text = "📖  API Docs (Swagger /docs)";
            btnApiDocs.Location = new Point(24, 245);
            btnApiDocs.Size = new Size(235, 38);
            btnApiDocs.BackColor = Color.White;
            btnApiDocs.ForeColor = Color.FromArgb(40, 40, 40);
            btnApiDocs.FlatStyle = FlatStyle.Flat;
            btnApiDocs.Cursor = Cursors.Hand;
            btnApiDocs.Click += (s, e) => OpenUrl("http://localhost:8000/docs");
            this.Controls.Add(btnApiDocs);

            btnOpenLogs = new Button();
            btnOpenLogs.Text = "📄  Open Live Log File";
            btnOpenLogs.Location = new Point(284, 245);
            btnOpenLogs.Size = new Size(235, 38);
            btnOpenLogs.BackColor = Color.White;
            btnOpenLogs.ForeColor = Color.FromArgb(40, 40, 40);
            btnOpenLogs.FlatStyle = FlatStyle.Flat;
            btnOpenLogs.Cursor = Cursors.Hand;
            btnOpenLogs.Click += (s, e) => OpenLogFile();
            this.Controls.Add(btnOpenLogs);

            btnRestart = new Button();
            btnRestart.Text = "🔄  Restart Local Servers";
            btnRestart.Location = new Point(544, 245);
            btnRestart.Size = new Size(235, 38);
            btnRestart.BackColor = Color.White;
            btnRestart.ForeColor = Color.FromArgb(40, 40, 40);
            btnRestart.FlatStyle = FlatStyle.Flat;
            btnRestart.Cursor = Cursors.Hand;
            btnRestart.Click += (s, e) => RestartServices();
            this.Controls.Add(btnRestart);

            // Real-Time Interaction Logs Viewer
            Label lblLogHeader = new Label();
            lblLogHeader.Text = "REAL-TIME USER INTERACTION & AUDIT STREAM:";
            lblLogHeader.Location = new Point(24, 298);
            lblLogHeader.AutoSize = true;
            lblLogHeader.Font = new Font("Segoe UI", 9f, FontStyle.Bold);
            lblLogHeader.ForeColor = Color.FromArgb(70, 65, 60);
            this.Controls.Add(lblLogHeader);

            txtRealtimeLogs = new TextBox();
            txtRealtimeLogs.Multiline = true;
            txtRealtimeLogs.ReadOnly = true;
            txtRealtimeLogs.ScrollBars = ScrollBars.Vertical;
            txtRealtimeLogs.Location = new Point(24, 322);
            txtRealtimeLogs.Size = new Size(755, 215);
            txtRealtimeLogs.BackColor = Color.FromArgb(28, 28, 28);
            txtRealtimeLogs.ForeColor = Color.FromArgb(220, 240, 220); // Terminal green/white
            txtRealtimeLogs.Font = new Font("Consolas", 8.8f, FontStyle.Regular);
            this.Controls.Add(txtRealtimeLogs);
        }

        private void DetermineProjectRoot()
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            if (Directory.Exists(Path.Combine(baseDir, "apps")) && Directory.Exists(Path.Combine(baseDir, "logs")))
            {
                projectRoot = baseDir;
            }
            else
            {
                // Fallback to current working directory
                projectRoot = @"D:\D ata Didit\doctoral\DOKTORAL PROJECTS\researchforge-handoff-v0.3\researchforge";
            }
        }

        private bool IsHttpEndpointUp(string url)
        {
            try
            {
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
                req.Timeout = 1200;
                req.Method = "GET";
                using (HttpWebResponse res = (HttpWebResponse)req.GetResponse())
                {
                    return res.StatusCode == HttpStatusCode.OK;
                }
            }
            catch
            {
                return false;
            }
        }

        private void CheckServicesStatus()
        {
            bool apiUp = IsHttpEndpointUp("http://localhost:8000/healthz");
            bool webUp = IsHttpEndpointUp("http://localhost:5173/");

            if (apiUp)
            {
                lblApiStatus.Text = "● API Backend: Running (Port 8000)";
                lblApiStatus.ForeColor = Color.FromArgb(39, 174, 96);
            }
            else
            {
                lblApiStatus.Text = "○ API Backend: Offline (Starting...)";
                lblApiStatus.ForeColor = Color.FromArgb(192, 57, 43);
            }

            if (webUp)
            {
                lblWebStatus.Text = "● Web Frontend: Running (Port 5173)";
                lblWebStatus.ForeColor = Color.FromArgb(39, 174, 96);
            }
            else
            {
                lblWebStatus.Text = "○ Web Frontend: Offline (Starting...)";
                lblWebStatus.ForeColor = Color.FromArgb(192, 57, 43);
            }
        }

        private void StartServicesIfNeeded()
        {
            bool apiUp = IsHttpEndpointUp("http://localhost:8000/healthz");
            bool webUp = IsHttpEndpointUp("http://localhost:5173/");

            if (!apiUp)
            {
                string apiDir = Path.Combine(projectRoot, "apps", "api");
                string venvPython = Path.Combine(apiDir, ".venv", "Scripts", "python.exe");
                
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = "cmd.exe";
                psi.Arguments = "/c cd /d \"" + apiDir + "\" && set PYTHONPATH=. && .\\.venv\\Scripts\\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000";
                psi.CreateNoWindow = true;
                psi.UseShellExecute = false;
                try
                {
                    apiProcess = Process.Start(psi);
                }
                catch {}
            }

            if (!webUp)
            {
                string webDir = Path.Combine(projectRoot, "apps", "web");
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = "cmd.exe";
                psi.Arguments = "/c cd /d \"" + webDir + "\" && npx vite preview --port 5173 --host 0.0.0.0";
                psi.CreateNoWindow = true;
                psi.UseShellExecute = false;
                try
                {
                    webProcess = Process.Start(psi);
                }
                catch {}
            }
        }

        private void RestartServices()
        {
            txtRealtimeLogs.AppendText("\r\n[SYSTEM] Triggering services restart...\r\n");
            try
            {
                Process.Start(new ProcessStartInfo("cmd.exe", "/c taskkill /f /im uvicorn.exe /im vite.exe") { CreateNoWindow = true, UseShellExecute = false });
            }
            catch {}
            Thread.Sleep(1000);
            StartServicesIfNeeded();
            CheckServicesStatus();
        }

        private void OpenUrl(string url)
        {
            try
            {
                Process.Start(new ProcessStartInfo(url) { UseShellExecute = true });
            }
            catch (Exception ex)
            {
                MessageBox.Show("Could not open browser: " + ex.Message);
            }
        }

        private void OpenLogFile()
        {
            string logPath = Path.Combine(projectRoot, "logs", "realtime_interactions.log");
            if (File.Exists(logPath))
            {
                Process.Start(new ProcessStartInfo("notepad.exe", "\"" + logPath + "\"") { UseShellExecute = true });
            }
        }

        private void TailRealtimeLogs()
        {
            try
            {
                string logPath = Path.Combine(projectRoot, "logs", "realtime_interactions.log");
                if (!File.Exists(logPath)) return;

                using (FileStream fs = new FileStream(logPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                {
                    if (fs.Length > lastLogPosition)
                    {
                        fs.Seek(lastLogPosition, SeekOrigin.Begin);
                        using (StreamReader reader = new StreamReader(fs, Encoding.UTF8))
                        {
                            string newContent = reader.ReadToEnd();
                            if (!string.IsNullOrEmpty(newContent))
                            {
                                txtRealtimeLogs.AppendText(newContent.Replace("\n", "\r\n"));
                                txtRealtimeLogs.SelectionStart = txtRealtimeLogs.Text.Length;
                                txtRealtimeLogs.ScrollToCaret();
                            }
                        }
                        lastLogPosition = fs.Position;
                    }
                }
            }
            catch {}
        }

        [STAThread]
        public static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            // If launched with --open, open browser immediately upon starting
            if (args.Length > 0 && args[0] == "--open")
            {
                try { Process.Start(new ProcessStartInfo("http://localhost:5173") { UseShellExecute = true }); } catch {}
            }

            Application.Run(new MainForm());
        }
    }
}
