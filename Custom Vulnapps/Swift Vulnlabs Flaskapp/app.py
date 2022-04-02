from flask import Flask, render_template, request, render_template_string
import os
app=Flask("Development App")

@app.route('/', methods=['GET','POST'])
def index():

    global directoryContents #global variables idk why
    global currentDirectory


    #reading the directory name and files contents to display
    directoryContents=[]
    currentDirectory=os.popen("pwd").read()
    contents = os.popen("ls -p | egrep -v /$").read()
    for item in contents.split():
        directoryContents.append(item)

    if request.method == 'POST': #handling a submission request
        postData = os.popen('cat ./{}'.format(request.form['filename'])).read()
        if postData == '':
            postData = "Something broke lmao"
        return render_template('index.html', files=directoryContents, cwd=currentDirectory, data=postData)
    return render_template('index.html', files=directoryContents, cwd=currentDirectory, data='\n\n\n\n\n\n\n\n\n\n') #Get request + scuffed block

@app.route('/upload', methods=['GET','POST'])
def upload():
    
    global uploadedFiles #global variables and shit i forgot why i need them
    global uploadDirectory

    #reading upload directory and displaying the uploads
    uploadedFiles=[]
    uploadDirectory = os.popen('pwd').read().strip('\n')
    uploadDirectory += '/uploads'
    contents = os.popen("ls ./uploads -p | egrep -v /$").read()
    for item in contents.split():
        uploadedFiles.append(item)

    if request.method == 'POST': #file being uploaded
        if 'file' not in request.files:
            return render_template('upload.html', files=uploadedFiles, uploadDir=uploadDirectory, data='Missing file parameter') #post request has no file
        fileToUpload = request.files['file'] #getting the file from the post parameter
        if fileToUpload.filename == '':
            return render_template('upload.html', files=uploadedFiles, uploadDir=uploadDirectory, data='No file selected') #post request file has no name
        fileToUpload.save(os.path.join(uploadDirectory, fileToUpload.filename))
        #Re checking uploaded files
        uploadedFiles=[]
        uploadDirectory = os.popen('pwd').read().strip('\n')
        uploadDirectory += '/uploads'
        contents = os.popen("ls ./uploads -p | egrep -v /$").read()
        for item in contents.split():
            uploadedFiles.append(item)
        return render_template('upload.html', files=uploadedFiles, uploadDir=uploadDirectory, data='Successful upload') #Upload workey

    return render_template('upload.html', files=uploadedFiles, uploadDir=uploadDirectory, data='\n\n\n\n\n\n\n\n\n\n') #Get Request

@app.route('/render', methods=['GET','POST'])
def render():
    global uploadedFiles #global variables and shit i forgot why i need them
    global uploadDirectory

    #reading upload directory and displaying the uploads
    uploadedFiles=[]
    uploadDirectory = os.popen('pwd').read().strip('\n')
    uploadDirectory += '/uploads'
    contents = os.popen("ls ./uploads -p | egrep -v /$").read()
    for item in contents.split():
        uploadedFiles.append(item)
    if request.method == 'POST': #handling a render request
        try:
            file_to_read = open(uploadDirectory + "/"+request.form['filename'], mode='r') #SSTI
            file_contents = file_to_read.read()
            file_to_read.close()
            return render_template('render.html', files=uploadedFiles, uploadDir=uploadDirectory, data=render_template_string(file_contents))
        except:
            return render_template('render.html', files=uploadedFiles, uploadDir=uploadDirectory, data='Couldn\'t Render it  ¯\_(ツ)_/¯')
    return render_template('render.html', files=uploadedFiles, uploadDir=uploadDirectory, data='\n\n\n\n\n\n\n\n\n\n') #Get Request

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
