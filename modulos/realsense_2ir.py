# Lint as: python3
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
#export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.6/pyrealsense2
import pyrealsense2 as rs
import numpy as np
import time
from datetime import datetime
import json

#for create a new init config file
#init_config = {}
#init_config['ir1']={'enable':1, 'width':640, 'height':480, 'fps':90}
#init_config['ir2']={'enable':1, 'width':640, 'height':480, 'fps':90}
#init_config['color']={'enable':1, 'width':640, 'height':480, 'fps':30}
#init_config['debug']=1
#init_config['preconfig']=1
#with open('realsense_2ir/init_config.json', 'w') as outfile:
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
        with open(nfile) as json_file:
            self.init_data = json.load(json_file)
        
        
        local_data['debug']=self.init_data['debug']
        local_data['preconfig']=self.init_data['preconfig']
        

        
        local_data['count']=1
        local_data['time']=0
        out_data[nombre]['frames'] = {}
        out_data[nombre]['error'] = {}

        self.config_cam(nombre,local_data, out_data)

        
        
        if local_data['debug']:
            if (self.init_data['ir1']['enable']):
                cv2.namedWindow("IR1")
                cv2.setMouseCallback("IR1", self.save_images_event)
            if (self.init_data['ir2']['enable']):
                cv2.namedWindow("IR2")
                cv2.setMouseCallback("IR2", self.save_images_event)
            if (self.init_data['color']['enable']):
                cv2.namedWindow("COLOR")
                cv2.setMouseCallback("COLOR", self.save_images_event)
        self.save_image=0

    def work(self, nombre, local_data, out_data):
        time_now=  time.time()


        try:
            out_data[nombre]['error'] = {}
            frames = local_data['pipeline'].wait_for_frames()
            #depth_frame = frames.get_depth_frame()
            if (self.init_data['ir1']['enable']):
                ir1 = frames.get_infrared_frame(1)
            if (self.init_data['ir2']['enable']):
                ir2 = frames.get_infrared_frame(2)
            if (self.init_data['color']['enable']):            
                color = frames.get_color_frame()
        except:
            out_data[nombre]['error'][1] = 'Fallo de camara'
            return
            #if (not(1 in out_data['error'])):
            #    out_data['error']={1:'Fallo de camara'}
                #out_data['error'].append(1)
                #out_data['error_text'].append ('Fallo de camara')


        
            

        #color_frame = frames.get_color_frame()
        #if not depth_frame or not color_frame:
        #    continue
        #rgb_image = np.asanyarray(color_frame.get_data())
        
        #rgb_image1 = np.asanyarray(ir1.get_data())
        #rgb_image2 = np.asanyarray(ir2.get_data())
        #out_data['frames'] = []
        #out_data['frames'].append(np.asanyarray(ir1.get_data()))
        #out_data['frames'].append(np.asanyarray(ir1.get_data()))
        out_data[nombre]['frames']={}
        if (self.init_data['ir1']['enable']):
            out_data[nombre]['frames']['ir1'] = np.asanyarray(ir1.get_data())
        if (self.init_data['ir2']['enable']):
            out_data[nombre]['frames']['ir2'] = np.asanyarray(ir2.get_data())
        if (self.init_data['color']['enable']):
            out_data[nombre]['frames']['color'] = np.asanyarray(color.get_data())

        #out_data['frames'].append(np.asanyarray(ir1.get_data()))
        local_data['count']= local_data['count'] + 1
        local_data['time']=(time.time()-time_now)*1000

            #cv2.rectangle(rgb_image, (det.left(), det.top()), (det.right(), det.bottom()), color_green, line_width)
        
        if local_data['debug']:
            print (local_data['time'])
            if (self.init_data['ir1']['enable']):
                cv2.imshow('IR1', out_data[nombre]['frames']['ir1'])
            if (self.init_data['ir2']['enable']):
                cv2.imshow('IR2', out_data[nombre]['frames']['ir2'])
            if (self.init_data['color']['enable']):
                cv2.imshow('COLOR', out_data[nombre]['frames']['ir2'])
            key = cv2.waitKey(1)
            if self.save_image:
                self.save_image=0
                now_str = datetime.now().strftime("%d%m%Y_%H%M%S")
                sttt= 'modulos/' + nombre + '/images/' + now_str + '_ir1.jpg'
                if self.init_data['ir1']['enable']==1:
                    cv2.imwrite('modulos/' + nombre + '/images/'  + '_ir1.jpg',out_data[nombre]['frames']['ir1']) 
                if self.init_data['ir2']['enable']==1:
                    cv2.imwrite( sttt + '_ir2.jpg',out_data[nombre]['frames']['ir2']) 
                if self.init_data['color']['enable']==1:
                    cv2.imwrite('modulos/' + nombre + '/images/' + now_str + '_color.jpg', out_data[nombre]['frames']['color']) 

    def onError(self,nombre,local_data, out_data):
        self.config_cam(nombre,local_data, out_data)        #local_data['piperline'].stop()
        
    def event (self, nombre, local, out, event, event_sync):
        None

    def end (self, nombre, local_data, out_data):
        local_data['piperline'].stop()









    def config_cam(self,nombre,local_data, out_data):
        # Configure depth and color streams
        local_data['pipeline'] = rs.pipeline()
        local_data['config'] = rs.config()
        local_data['config'].enable_device('849412062160')
        #config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        if self.init_data['color']['enable']==1:
            local_data['config'].enable_stream(rs.stream.color, self.init_data['color']['width'],
            self.init_data['color']['height'],
            rs.format.bgr8,
            self.init_data['color']['fps'])
        if self.init_data['ir1']['enable']==1:
            local_data['config'].enable_stream(rs.stream.infrared, 1, self.init_data['ir1']['width'],
            self.init_data['ir1']['height'],
            rs.format.y8,
            self.init_data['ir1']['fps'])
        if self.init_data['ir2']['enable']==1:
            local_data['config'].enable_stream(rs.stream.infrared, 2, self.init_data['ir2']['width'],
            self.init_data['ir2']['height'],
            rs.format.y8,
            self.init_data['ir2']['fps'])

        #config.enable_stream(rs.stream.infrared, 2, 1280,720, rs.format.y8, 6)
        # Start streaming
        local_data['cfg'] = local_data['pipeline'].start(local_data['config'])
        if (local_data['preconfig']==1):
            jsonObj = json.load(open('modulos/' + nombre + '/config_cam.json'))        
            json_string= str(jsonObj).replace("'", '\"')
            local_data['dev'] = local_data['cfg'].get_device()
            local_data['advnc_mode'] = rs.rs400_advanced_mode(local_data['dev'])
            local_data['advnc_mode'].load_json(json_string)


    def save_images_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.save_image=1
            
