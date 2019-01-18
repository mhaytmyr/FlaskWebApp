import os

from application import app, APP_ROOT
from flask import render_template, request, url_for

import cv2, numpy as np
import pydicom

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

    return render_template("predict_bootsrap.html",filenames=filenames)
