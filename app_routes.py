import os

from application import app, APP_ROOT
from flask import render_template, request, url_for

import cv2, numpy as np
import pydicom

FILENAMES = None
MODELNAME = None

def convert_dcm_to_image(dst,img):
    
    #get image shape
    shape = img.shape   
    #rescale image
    imgScaled = (img-img.min())*255/img.max()
    #convert to uint
    imgScaled = np.uint(imgScaled)
    #write image as png file
    newFileName = dst.replace('dcm','png') 
    cv2.imwrite(newFileName,imgScaled)
    print(dst+" saved!")

    return newFileName.split('/')[-1]#return file name not the path

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

        #destination to upload
        dst = "/".join([target,filename])

        #save that file to specified destination
        file.save(dst)

        #read dcm image
        imgArr = pydicom.read_file(dst).pixel_array.astype('float32')

        #add preprocessing here to DCM images
        filename = convert_dcm_to_image(dst,imgArr)
        filenames.append(filename)

    return filenames

def predict(files,model=None,blur=5):
    newFiles = []
    for file in files:
        imgArr = pydicom.read_file(file).pixel_array.astype('float32')
        #apply operation
        imgPred = cv2.blur(imgArr,(blur,blur))
        #create new destination
        dst = file.replace('.dcm','_pred.dcm')
        #save new image
        predFile = convert_dcm_to_image(dst,imgPred)
        newFiles.append(predFile)
    return newFiles



def predict_slices(filenames,request):
    #this method will perform prediction and return segmented slices
    #for testing, apply some image processing
    
    #destination to save temporary images
    path = os.path.join(APP_ROOT,'static')
    
    #first get dcm filenames
    files = ["/".join([path,item.replace('png','dcm')]) for item in filenames]

    #get model name
    selected_model = request.form['model_name']
    if selected_model=='head':
        #choose head model
        return predict(files,blur=10)
    elif selected_model=='thorax':
        #choose thorax model
        return predict(files,blur=20)
    elif selected_model=='abdomen':
        #choose abdomen
        return predict(files,blur=30)
    elif selected_model=='prostate':
        return predict(files,blur=50)
    else:
        return []

@app.route('/',methods=['POST','GET'])
def main_page():
    global FILENAMES

    #check landing page
    if request.method == 'POST':
        if request.form['action']=='UPLOAD':
            #get uploaded filenames
            filenames = get_file_names(request)
            FILENAMES = filenames
            return render_template("predict_bootsrap.html",filenames=filenames,predicts=None)
        elif request.form['action']=='SEGMENT':
            #validate uploaded files first
            if FILENAMES is None:
                render_template("predict_bootsrap.html",filenames=None,predicts=None)     
            else:
                #appy prediction and show on the right image
                prediction = predict_slices(FILENAMES,request)
                return render_template("predict_bootsrap.html",filenames=FILENAMES,predicts=prediction)
        else:
            return '<h1> BAD REQUEST SEND </h1>'

    return render_template("predict_bootsrap.html",filenames=None,predicts=None)

@app.route('/tmp',methods=['POST','GET'])
def index():
    return render_template("predict_bootsrap.html",filenames=None)

@app.route('/predict',methods=['POST','GET'])
def model_selection():
    print("Calling model_selection")

    for key in request.form:
        print("form key "+key+":"+request.form[key])
    #print("Success called model selection")
    #return redirect(url_for('upload_method'))
    return render_template("predict_bootsrap.html",filenames=FILENAMES)