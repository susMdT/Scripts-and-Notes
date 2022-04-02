This app has 3 endpoints, /, /render, and /upload

/ is vulnerable to command injection and lfi
/upload allows uploads (although technically you could command inject to get the same result)
/render renders specified files so SSTI is possible
