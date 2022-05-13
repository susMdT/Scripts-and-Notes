Process Injection/Hollowing via donut shellcode hosted on a web server.

Installation Directions:
<br>
1. Download the executable, dockerfile, server script, and setup script
2. Place the dockerfile and setup script in the same directory. Place the server script in ./serv/ and whatever exes you want in ./exe
3. build the image `docker build -t donutimg` and run it while port forwarding 8081 `docker run -p 8081:8081 donutimg`
4. Run the exe
<br>
Credit to 3xpl01tc0d3r, https://github.com/3xpl01tc0d3r for Process Hollowing
<br>
Todo:
<br>
[-] Make deployment easier
<br>
[-] Test other .NET executables
<br>
[-] Figure a fix to python/go or any way to not have to utilize wine 
<br>
[-] Implement SSL to make payload download more sneaky?
