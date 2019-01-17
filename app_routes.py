import os

from application import app, APP_ROOT
from flask import render_template, request, url_for

@app.route('/',methods=['POST','GET'])
def index():
    return render_template("predict_bootsrap.html",filenames=None)

@app.route('/upload',methods=['POST','GET'])
def upload_method():
    
    #destination to save temporary images
    target = os.path.join(APP_ROOT,'static/')
    
    #if destination doesn't exist create new destination
    if not os.path.isdir(target):
        os.mkdir(target)

    filenames = [];
    #loop over the files
    for file in request.files.getlist("input-file"):
        print(file)
        filename = file.filename
        filenames.append(filename)

        #destination to upload
        dst = "/".join([target,filename])

        #save that file to specified destination
        #TODO: add preprocessing here to DCM images
        file.save(dst)

    return render_template("predict_bootsrap.html",filenames=filenames)
