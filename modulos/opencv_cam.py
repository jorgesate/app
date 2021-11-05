# Lint as: python3
# Copyright 2021 Jose Carlos Provencio 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import name
import cv2
import numpy as np
import time
from datetime import datetime
import json



#for create a new init config file
#init_config = {}
#init_config['cam']=[]
#init_config['cam'].append ({'name': 'cam0', 'hw_name': '/dev/video0', 'config_name': 'cam0_config.json', 'enable':1, 'preconfig': 0, 'width':800, 'height':600, 'fps':30, 'rotate': 180})
#init_config['cam'].append ({'name': 'cam1', 'hw_name': '/dev/video0', 'config_name': 'cam0_config.json', 'enable':1, 'preconfig': 0, 'width':640, 'height':480, 'fps':30, 'rotate': 180})
#init_config['debug']=1
#with open('modulos/opencv_cam/init_config.json', 'w') as outfile:
#    json.dump(init_config, outfile)


class Modulo:
    def __init__(self):
        None

    def start(self, nombre, local_data, out_data):
        out_data[nombre]['error'] = {}
        nfile='modulos/' + local_data['modName'] +'/'
        if (len(local_data['args'])==0):    
            nfile = nfile+ 'init_config.json'
        else:
            nfile = nfile + local_data['args']
        #load config file
        with open(nfile) as json_file:
            self.init_data = json.load(json_file)
        local_data['cam'] = []
        for ic in self.init_data['cam']:
            local_data['cam'].append(ic)      

        local_data['debug']=self.init_data['debug']        
        local_data['count']=1
        local_data['time']=0
        #local_data['args']=self.init_data['debug']  
        out_data[nombre]['frames'] = {}

        #configure cams    
        self.config_cam(nombre,local_data, out_data)
        if (local_data['debug']):
            self.save_image=0
            for i in range(len(local_data['cam'])):
                cv2.namedWindow(local_data['cam'][i]['name'])
                cv2.setMouseCallback(local_data['cam'][i]['name'], self.save_images_event)



    def work(self, nombre, local_data, out_data):
        time_now=  time.time()
        
        try:
            #clean errors and previous images
            out_data[nombre]['frames']={}
            out_data[nombre]['error'] = {}

            #get images
            for i in range (len(local_data['cam'])):
                nom =local_data['cam'][i]['name']
                ret, out_data[nombre]['frames'][nom] = local_data['cam'][i]['cam_hw'].read()            
                if not ret:
                    out_data[nombre]['error'][1] = 'Error de camara en modulo ' + nombre
                    #print("Can't receive frame (stream end?). Exiting ...")
                    return
                if local_data['cam'][i]['rotate']==90:
                    out_data[nombre]['frames'][nom] = cv2.rotate(out_data[nombre]['frames'][nom], cv2.ROTATE_90_CLOCKWISE)
                if local_data['cam'][i]['rotate']==180:
                    out_data[nombre]['frames'][nom] = cv2.rotate(out_data[nombre]['frames'][nom], cv2.ROTATE_180)
                if local_data['cam'][i]['rotate']==270:
                    out_data[nombre]['frames'][nom] = cv2.rotate(out_data[nombre]['frames'][nom], cv2.ROTATE_90_COUNTERCLOCKWISE)
                
        except:
            out_data[nombre]['error'][1] = 'Fallo de camara'
            return

        local_data['count']= local_data['count'] + 1
        local_data['time']=(time.time()-time_now)*1000
        #if is in debug mode show the image in new windows and time of cams needs
        if local_data['debug']:
            print (local_data['time'])
            for i in range(len(local_data['cam'])):
                cv2.imshow(local_data['cam'][i]['name'], out_data[nombre]['frames'][local_data['cam'][i]['name']])
                if self.save_image:
                    self.save_image=0
                    now_str = datetime.now().strftime("%d%m%Y_%H%M%S")
                    sttt= 'modulos/' + local_data['modName'] + '/images/' + now_str + '_' + local_data['cam'][i]['name'] + '.jpg'
                    cv2.imwrite(sttt,out_data[nombre]['frames'][local_data['cam'][i]['name']])     

            key = cv2.waitKey(1)

    def onError(self,nombre,local_data, out_data):
        self.config_cam(nombre,local_data, out_data)       
        
    def event (self, nombre, local, out, event, event_sync):
        None

    def end (self, nombre, local_data, out_data):
        local_data['piperline'].stop()









    def config_cam(self,nombre,local_data, out_data):
        c={}
        c['CAP_PROP_FRAME_WIDTH']= cv2.CAP_PROP_FRAME_WIDTH
        c['CAP_PROP_FRAME_HEIGHT']= cv2.CAP_PROP_FRAME_HEIGHT
        c['CAP_PROP_AUTO_EXPOSURE']= cv2.CAP_PROP_AUTO_EXPOSURE
        c['CAP_PROP_AUTO_WB']= cv2.CAP_PROP_AUTO_WB
        c['CAP_PROP_AUTOFOCUS']= cv2.CAP_PROP_AUTOFOCUS
        c['CAP_PROP_BUFFERSIZE']= cv2.CAP_PROP_BUFFERSIZE
        c['CAP_PROP_FPS']= cv2.CAP_PROP_FPS
        c['CAP_PROP_BRIGHTNESS']= cv2.CAP_PROP_BRIGHTNESS
        c['CAP_PROP_CONTRAST']= cv2.CAP_PROP_CONTRAST
        c['CAP_PROP_HUE']= cv2.CAP_PROP_HUE
        c['CAP_PROP_GAIN']= cv2.CAP_PROP_GAIN
        c['CAP_PROP_EXPOSURE']= cv2.CAP_PROP_EXPOSURE
        c['CAP_PROP_MONOCHROME']= cv2.CAP_PROP_MONOCHROME
        c['CAP_PROP_SHARPNESS']= cv2.CAP_PROP_SHARPNESS
        c['CAP_PROP_GAMMA']= cv2.CAP_PROP_GAMMA
        c['CAP_PROP_TEMPERATURE']= cv2.CAP_PROP_TEMPERATURE
        c['CAP_PROP_WB_TEMPERATURE']= cv2.CAP_PROP_WB_TEMPERATURE
        c['CAP_PROP_ZOOM']= cv2.CAP_PROP_ZOOM


        for i in range (len(local_data['cam'])):
            local_data['cam'][i]['cam_hw'] =cv2.VideoCapture(local_data['cam'][i]['hw_name'])
            if local_data['cam'][i]['preconfig']:
                #abrimos json
                with open('modulos/' + local_data['modName'] + '/' + local_data['cam'][i]['config_name']) as json_file:
                    loaded_config = json.load(json_file)
                #l_cams=loaded_config['cam']
                #l_files =[]
                #for i in l_cams:
                #    l_files.append (i['config_name'])
                #for n_file in l_files:
                #    with open('modulos/' + nombre + '/' + n_file) as json_file:
                #        cam_config = json.load(json_file)
                for n in c:
                    try:
                        local_data['cam'][i]['cam_hw'].set(c[n], float(loaded_config[n]) )
                        print ('set ' + n + ' ' + str(int(loaded_config[n])))
                    except:
                        None
                print ('\n')
                #for n in c:
                #    local_data['cam'][i]['cam_hw'].set(c[n], loaded_config[n])

            if local_data['debug']:
                if not local_data['cam'][i]['cam_hw'].isOpened():
                    print("Cannot open camera: " + local_data['cam'][i]['name'])
            print (local_data['cam'][i]['name'] + ':')
            
            
            #put if (1): for save defalut values ->> put preconfig to 0 in config file
            if (0):
                d1={}
                for n in c:
                    value = local_data['cam'][i]['cam_hw'].get(c[n])
                    d1[n]=value
                    print (n + ' ' + str(int(value)))
                print ('\n')
                nom = 'modulos/opencv_cam/config_cam_' + local_data['cam'][i]['name'] + '.json'
                with open(nom, 'w') as outfile:
                    json.dump(d1, outfile)
            #open configcamfile

            
        None
        
    def save_images_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.save_image=1
