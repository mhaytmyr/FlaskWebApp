import os

from application import app, APP_ROOT
from flask import render_template, request, url_for

import cv2, numpy as np
import pydicom

FILENAMES = None
MODELNAME = None

def convert_dcm_to_image(dst):
    #read dcm image
    img = pydicom.read_file(dst).pixel_array.astype('float32');
    shape = img.shape;
    #rescale image
    imgScaled = (img-img.min())*255/img.max();
    #convert to uint
    imgScaled = np.uint(imgScaled);
    #write image as png file
    newFileName = dst.replace('dcm','png'); 
    cv2.imwrite(newFileName,imgScaled);
    print("Img saved! ",img.shape)

    return newFileName.split('/')[-1]#I need just file name not the path

def get_file_names(request):
    #destination to save temporary images
    target = os.path.join(APP_ROOT,'static/')
    
    #if destination doesn't exist create new destination
    if not os.path.isdir(target):
        os.mkdir(target)

    filenames = [];
    #loop over the files
    for file in request.files.getlist("input_files"):
        #print(file)
        filename = file.filename
        #filenames.append(filename)

        #destination to upload
        dst = "/".join([target,filename])

        #save that file to specified destination
        file.save(dst)

        #add preprocessing here to DCM images
        filename = convert_dcm_to_image(dst)
        filenames.append(filename)

    return filenames


@app.route('/',methods=['POST','GET'])
def main_test():
    global FILENAMES

    #check landing page
    if request.method == 'POST':
        if request.form['action']=='UPLOAD':
            #get uploaded filenames
            filenames = get_file_names(request)
            FILENAMES = filenames
            return render_template("predict_bootsrap.html",filenames=filenames)
        elif request.form['action']=='SEGMENT':
            tmpPage = '<h1>Segment pressed</h1>'
            for key in request.form:
                tmpPage += '<p>form '+key+':'+request.form[key]+'</p>'
            #print filenames for debugging
            for file in FILENAMES:
                tmpPage += '<p>'+file+'</p>'
            return tmpPage
        else:
            return render_template("predict_bootsrap.html",filenames=None)

    return render_template("predict_bootsrap.html",filenames=None)

@app.route('/tmp',methods=['POST','GET'])
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
        #print(file)
        filename = file.filename
        #filenames.append(filename)

        #destination to upload
        dst = "/".join([target,filename])

        #save that file to specified destination
        file.save(dst)

        #add preprocessing here to DCM images
        filename = convert_dcm_to_image(dst);
        filenames.append(filename);


    #update file names

    return render_template("predict_bootsrap.html",filenames=filenames)

@app.route('/predict',methods=['POST','GET'])
def model_selection():
    print("Calling model_selection")

    for key in request.form:
        print("form key "+key+":"+request.form[key])
    #print("Success called model selection")
    #return redirect(url_for('upload_method'))
    return render_template("predict_bootsrap.html",filenames=FILENAMES)