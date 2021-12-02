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

from PIL import Image
from PIL import ImageDraw

import cv2

sys.path.append(os.path.abspath("modulos/zcoral/"))
sys.path.append(os.path.abspath("zcoral/"))

import detect
import tflite_runtime.interpreter as tflite
import platform

EDGETPU_SHARED_LIB = {
  'Linux': 'libedgetpu.so.1',
  'Darwin': 'libedgetpu.1.dylib',
  'Windows': 'edgetpu.dll'
}[platform.system()]



#for create a new init config file
#init_config = {}
#init_config['model'] = {'model':'models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite', 'labels':'models/coco_labels.txt', 'threshold': 0.4, 'cameras':[['realsense_2ir1', 'color']], 'draw_filter': 'Abierta_Abajo'}
#init_config['debug'] = 1
#with open('modulos/zcoral/init_config.json', 'w') as outfile:
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

      out_data[nombre]['frames']={}
    #init_config['model'] = {'model':'ssd-mobilenet-v1', 'labels':'models/coco_labels.txt', 'threshold': 0.4, 'cameras':[['opencv_cam', 'cam1']]}


      local_data['debug']= init_config['debug']
      local_data['l_model'] = init_config['model']['model']
      local_data['draw_filter'] = init_config['model']['draw_filter']
      local_data['l_labels'] = init_config['model']['labels']
      local_data['l_threshold'] = init_config['model']['threshold']
      #local_data['source_modules']=init_config['sorce_modules']
      local_data['cameras'] = init_config['model']['cameras']
      local_data['labels'] = load_labels('modulos/' + local_data['modName'] + '/' + local_data['l_labels'])
      local_data['interpreter'] = make_interpreter('modulos/' + local_data['modName'] + '/' + local_data['l_model'])
      
      
      local_data['interpreter'].allocate_tensors()
      local_data['interpreter'].invoke()


      out_data[nombre]['detected'] = {}




    def work(self,nombre,local_data, out_data):
        time_now=  time.time()
        out_data[nombre]['detected'] = {}
        #scale = detect.set_input(local_data['interpreter'], image.size,
        #                   lambda size: image.resize(size, Image.ANTIALIAS))
        #out_data[nombre]['frames']['ir2']=cv2.cvtColor(out_data['realsense_2ir']['frames']['ir2'], cv2.COLOR_BGR2RGB)
        #images = [out_data[nombre]['ir1'], out_data[nombre]['ir2']]
        #l_frames = ['ir1','ir2']
        
        #for n in out_data[local_data['source_modules']]['frames'].keys():
        for i in range (len(local_data['cameras'])):
            [mod,cam] = local_data['cameras'][i]
            modcam = mod + '_' + cam
            out_data[nombre]['frames'][modcam] = np.copy(out_data[mod]['frames'][cam])
            out_data[nombre]['frames'][modcam]=cv2.cvtColor(out_data[nombre]['frames'][modcam], cv2.COLOR_BGR2RGB)
            #out_data[nombre]['frames'][modcam]=cv2.cvtColor(out_data[local_data['sorce_modules']]['frames'][modcam], cv2.COLOR_BGR2RGB)
            out_data[nombre]['frames'][modcam] = Image.fromarray(out_data[nombre]['frames'][modcam])
                   
            scale = detect.set_input(local_data['interpreter'], out_data[nombre]['frames'][modcam].size,
                            lambda size: out_data[nombre]['frames'][modcam].resize(size, Image.NEAREST)) #OPTIMIZAR
                            #lambda size: out_data[nombre]['frames'][n].resize(size, Image.ANTIALIAS)) #OPTIMIZAR
          #time_now2=  time.time()

          #print ((time.time() - time_now2)*1000)
            local_data['interpreter'].invoke()
            objs = detect.get_output(local_data['interpreter'], local_data['l_threshold'], scale)
            #draw_objects_pil(ImageDraw.Draw(out_data[nombre]['frames'][n]), objs, local_data['labels'])

            out_data[nombre]['frames'][modcam] = np.array(out_data[nombre]['frames'][modcam])
            out_data[nombre]['frames'][modcam] = cv2.cvtColor(out_data[nombre]['frames'][modcam], cv2.COLOR_RGB2BGR)
          

            for obj in objs:
              #out_data[nombre]['detected']['cam'].append({'label':local_data['labels'].get(obj.id, obj.id), 'score': obj.score, 'bbox':obj.bbox})
              objs2= []
              objs2.append({'label':local_data['labels'].get(obj.id, obj.id), 'score': obj.score, 'bbox':obj.bbox})
              out_data[nombre]['detected']['cam']=objs2
              if (local_data['labels'].get(obj.id, obj.id) in local_data['draw_filter']):
                draw_objects(out_data[nombre]['frames'][modcam], obj, local_data['labels'].get(obj.id, obj.id))

              if local_data['debug']:
                if not objs:
                  print('No objects detected')
                for obj in objs:
                  print(local_data['labels'].get(obj.id, obj.id))
                  print('  id:    ', obj.id)
                  print('  score: ', obj.score)
                  print('  bbox:  ', obj.bbox)
  
      
        if local_data['debug']:
          #print (local_data['time'])
          for k in out_data[nombre]['frames'].keys():
            cv2.imshow('Inference ' + k, out_data[nombre]['frames'][k])
          key = cv2.waitKey(1)
          local_data['time']=(time.time()-time_now)*1000
          print (local_data['time'])
        else:
          local_data['time']=(time.time()-time_now)*1000

        




    def onError(self,nombre,local_data, out_data):
        None
    
    def event (self, nombre, local, out, event, event_sync):
        None

    def end (self, nomre, local_data, out_data):
        None

#* * * * * * * * * * * * * * * * * * * * * * * * * * * *#

def load_labels(path, encoding='utf-8'):
  """Loads labels from file (with or without index numbers).

  Args:
    path: path to label file.
    encoding: label file encoding.
  Returns:
    Dictionary mapping indices to labels.
  """
  with open(path, 'r', encoding=encoding) as f:
    lines = f.readlines()
    if not lines:
      return {}

    if lines[0].split(' ', maxsplit=1)[0].isdigit():
      pairs = [line.split(' ', maxsplit=1) for line in lines]
      return {int(index): label.strip() for index, label in pairs}
    else:
      return {index: line.strip() for index, line in enumerate(lines)}

def make_interpreter(model_file):
  model_file, *device = model_file.split('@')
  return tflite.Interpreter(
      model_path=model_file,
      experimental_delegates=[
          tflite.load_delegate(EDGETPU_SHARED_LIB,
                               {'device': device[0]} if device else {})
      ])


def draw_objects_pil(draw, objs, labels):
  """Draws the bounding box and label for each object."""
  for obj in objs:
    bbox = obj.bbox
    draw.rectangle([tuple ([bbox.xmin, bbox.ymin]), tuple ([bbox.xmax, bbox.ymax])],
                   outline='red')
    draw.text(tuple ([bbox.xmin + 10, bbox.ymin + 10]),
              '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score),
              fill='red')

def draw_objects(image, obj, label):
  """Draws the bounding box and label for each object."""
  bbox = obj.bbox
  cv2.rectangle(image, tuple ([bbox.xmin,bbox.ymin]) , tuple([bbox.xmax,bbox.ymax]), (0,0,255), 2)
  cv2.putText(image, label, tuple ([bbox.xmin,bbox.ymin]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1)