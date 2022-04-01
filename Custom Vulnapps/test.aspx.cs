using System;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Text;
namespace test
{
        public partial class testing:System.Web.UI.Page
        {
 
                protected void IP_Submit(object sender, EventArgs e)
                {
                        String ipAdd = input.Text;
                        // I heard this will sanitize inputs, but idk! - budget benton
                        //if (ipAdd.Contains("&"))
                        //{
                        //      OutputLabel.Text="Kinda sussy bruh";
                        //}
                        //else
                        //{
                        //      OutputLabel.Text = doTheThing(ipAdd);
                        //}
                        //If we use this code block above, we gotta delete the link below us.  
                        OutputLabel.Text = doTheThing(ipAdd);
                }
 
                protected String doTheThing(String Thing)
                {
                        String ipAdd = Thing;
                        String command = "/c ping " +ipAdd;
                        StringBuilder log = new StringBuilder();
 
                        System.Diagnostics.Process p = new System.Diagnostics.Process();
                        p.StartInfo = new System.Diagnostics.ProcessStartInfo("cmd.exe", command);
                        p.StartInfo.RedirectStandardOutput = true;
                        p.StartInfo.UseShellExecute = false;
                        p.Start();
 
                        while (!p.HasExited)
                        {
                                log.Append(p.StandardOutput.ReadToEnd());
                        }
                        return log.ToString();
 
                }
                protected override object LoadPageStateFromPersistenceMedium()
                {
                        return null;
                }
                protected override object SaveViewState()
                {
                        return null;
                }
        }
}
