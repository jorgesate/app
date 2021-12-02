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

import numpy as np
import sys
import os
import argparse
import time
import json
import cv2
import jetson.inference
import traceback

sys.path.append(os.path.abspath("modulos/jetson_inference/"))
sys.path.append(os.path.abspath("jetson_inference/"))


#for create a new init config file
#init_config = {}
#init_config['models'] = []
#init_config['models'].append({'model':'modlos/jetson_inference/models/ssd-mobilenet.onnx', 'labels':'models/coco_labels.txt', 'threshold': 0.4, 'cameras':[['ralsense_2ir1', 'color'],['opencv_cam1', 'cam0']], 'draw_filter': 'Abierta_Abajo'})
#init_config['models'].append({'model':'modlos/jetson_inference/models/ssd-mobilenet.onnx', 'labels':'models/coco_labels.txt', 'threshold': 0.4, 'cameras':[['ralsense_2ir1', 'ir1'],['opencv_cam1', 'cam1']], 'draw_filter': 'Abierta_Abajo'})
#init_config['debug'] = 1
#with open('modulos/jetson_inference/init_config.json', 'w') as outfile:
#    json.dump(init_config, outfile)

class Modulo:
    def __init__(self):
      None

    def start(self,nombre,local_data, out_data):
      out_data[nombre]['error'] = {}
      #Read module config
      nfile='modulos/' + local_data['modName'] +'/'
      if (len(local_data['args'])==0):    
          nfile = nfile+ 'init_config.json'
      else:
          nfile = nfile + local_data['args']
      with open(nfile) as json_file:
          init_config = json.load(json_file)
        
      local_data['debug']=init_config['debug']
      local_data['models'] = init_config['models']
      local_data['nets']=[]

      for model in local_data['models']:
        local_data['nets'].append(jetson.inference.detectNet(argv=['--model=' + model['model'], '--labels=' + model['labels'], '--input-blob=input_0','--output_cvg=scores', '--output-bbox=boxes']))
      out_data[nombre]['detected'] = {}
      out_data[nombre]['frames'] ={}

    def work(self,nombre,local_data, out_data):
        objs=[]
        time_now=  time.time()
        out_data[nombre]['detected'] = {}
        out_data[nombre]['frames'] ={}
        for n in range (len(local_data['nets'])):
          net = local_data['nets'][n]
          for i in range (len(local_data['models'][n]['cameras'])):
            [mod,cam] = local_data['models'][n]['cameras'][i]
            modcam = mod + '_' + cam

            out_data[nombre]['frames'][modcam] = np.copy(out_data[mod]['frames'][cam])
            cuda_image = out_data[nombre]['frames'][modcam]
            cuda_image = cv2.cvtColor(cuda_image, cv2.COLOR_BGR2RGBA)
            cuda_image = jetson.utils.cudaFromNumpy(out_data[nombre]['frames'][modcam])
            try:
              detected = net.Detect(cuda_image, overlay='none')

              for h in range(len(detected)):
                x1 = int (detected[h].Left)
                x2 = int (detected[h].Right)
                y1 = int (detected[h].Top)
                y2 = int (detected[h].Bottom)
                objs.append({'label': net.GetClassDesc(detected[h].ClassID), 'score': detected[h].Confidence,'bbox': [[x1,y1],[x2,y2]]})
                out_data[nombre]['detected'][modcam]= objs
              for obj in objs:
                if (obj['label'] in local_data['models'][n]['draw_filter']):
                  draw_objects(out_data[nombre]['frames'][modcam], obj)

            except Exception:
              traceback.print_exc()

          if local_data['debug']:
              if not objs:
                  print('No objects detected')
              for obj in objs:
                  print('  label:    ', obj['label'])
                  print('  score: ', obj['score'])
                  print('  bbox:  ', obj['bbox'])
   
          count=1
        
        local_data['time']=(time.time()-time_now)*1000
        if local_data['debug']:
          for k in out_data[nombre]['frames'].keys():
            cv2.imshow('Inference ' + k, out_data[nombre]['frames'][k])
          key = cv2.waitKey(1)
          print (local_data['time'])

    def onError(self,nombre,local_data, out_data):
        None
    
    def event (self, nombre, local, out, event, event_sync):
        None

    def end (self, nomre, local_data, out_data):
        None

#* * * * * * * * * * * * * * * * * * * * * * * * * * * *#

def draw_objects(image, obj):
  """Draws the bounding box and label for each object."""
  bbox = obj['bbox']
  cv2.rectangle(image, tuple(bbox[0]) ,tuple (bbox[1]), (0,0,255), 2)
  cv2.putText(image, obj['label'], tuple(bbox[0]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1)

