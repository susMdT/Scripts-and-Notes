<%@ Page Language="C#" AutoEventWireup="false" CodeFile="test.aspx.cs" Inherits="test.testing"%>
<!DOCTYPE html>
<html>
<head>
</head>
<body>
<div>
 
        <span>Connectivity Tester</span>
 
        <div class="flexbox-container" style="position:absolute;top:15rem;">
 
                <div style="margin-top: 2rem;">
                </div>
                <div class="card">
                        <p>Enter IP Address to test connectivity</p>
                </div>
                <form method="post" class="myForm" id="theForm" runat="server" EnableViewState="false" EnableEventValidation="false" >
                        <asp:Label runat="server">IP address:</asp:Label>
                        <asp:TextBox ID="input" name="input" value="" runat="server"/>
                        <br>
                        <asp:Button class="custom-button" type="submit" onclick="IP_Submit" Text="Test Connectivity!" runat="server"/>
                        <br>
                </form>
                <div class="flexbox-container">
                        <asp:Label ID="OutputLabel" runat="server"></asp:Label>
                </div>
        </div>
</div>
</body>
</html>
