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
import threading


#for create a new init config file
#init_config = {}
#    init_config['inf_mods'] = []
#    init_config['labels'] = []
#    init_config['triggers'] = []
#    init_config['inf_mods'].append ('jetson_inference1')
#    init_config['inf_mods'].append ('zcoral1')
#    init_config['labels'].append ('abierta_abajo')
#    init_config['labels'].append ('abierta_arriba')
#    init_config['screen_size']= [1920,1080]
#    init_config['debug'] = 1   
#    with open('modulos/gui_opencv/init_config.json', 'w') as outfile:
#        json.dump(init_config, outfile)

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
        
        local_data['inf_mods'] = init_config['inf_mods']
        local_data['labels'] = init_config['labels']
        local_data['triggers'] = init_config['triggers']
        local_data['inf_mods'] = init_config['inf_mods']
        local_data['screen_size'] =  init_config['screen_size']
        local_data['debug'] = init_config['debug']
        local_data['trigger'] = 0

        local_data['t_count'] = 0


        [y,x] = local_data['screen_size']
        out_data[nombre]['screen'] = np.zeros([x,y,3],dtype=np.uint8)
        out_data[nombre]['screen'].fill(175)
        out_data[nombre]['counters'] = {}
        local_data['counters'] = {}
      
        



    def work(self,nombre,local_data, out_data):


        #Calculo de estadisticas
        try:
            for mod in local_data['inf_mods']: #Recorremos los modulos configurados en el json
                de_cam = out_data[mod]['detected'] #dic with cams
                for de in de_cam: #recorremos las detecciones
                    lab = de_cam[de]#list with detections
                    for label in lab:
                        if (label['label'] in local_data['labels']):
                            local_data['counters'][label['label']] = 1
                if (not(local_data['t_count']==(out_data['tcp_in_out']['t_count']))): #Si ha tenido disparo el trigger
                    local_data['t_count'] = out_data['tcp_in_out']['t_count']
                    for jj in local_data['counters']:
                        try:
                            out_data[nombre]['counters'][jj] = out_data[nombre]['counters'][jj] + 1
                        except:
                            out_data[nombre]['counters'][jj] = 0
                    out_data[nombre]['counters']['Total'] = local_data['t_count']
                    local_data['counters'] = {}
            t_sta =''
            for jj in out_data[nombre]['counters']:
                t_sta = t_sta + jj + '   : ' + str(out_data[nombre]['counters'][jj]) + '\n'
            
         
        except:
            #ERROR
            print ('Fallo al calcular estadisticas, comprobar que se esta ejecutando el modulo tcp_in_out')

        #Pantalla de alarmas
        alarms = np.zeros([480,640,3],dtype=np.uint8)
        alarms.fill(255)
        font = cv2.FONT_HERSHEY_SIMPLEX
        to='ALARMAS:\n'
        for modulo in out_data:
            for alarma in out_data[modulo]['error']:
                to = to + str (alarma) + ' : ' + str (out_data[modulo]['error'][alarma]) + '\n'
        y0, dy = 50, 25
        for i, line in enumerate(to.split('\n')):
            yb = y0 + i*dy
            cv2.putText(alarms, line, (50, yb ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

        #Pantalla de estadisticas
        stadistics = np.zeros([480,640,3],dtype=np.uint8)
        stadistics.fill(255)
        font = cv2.FONT_HERSHEY_SIMPLEX
        to='ESTADISTICAS:\n' + t_sta
        #for modulo in out_data:
        #    for alarma in out_data[modulo]['error']:
        #        to = to + str (alarma) + ' : ' + str (out_data[modulo]['error'][alarma]) + '\n'
        y0, dy = 50, 25
        for i, line in enumerate(to.split('\n')):
            yb = y0 + i*dy
            cv2.putText(stadistics, line, (50, yb ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)



        x=0
        y=0
        ymax=0
        bi=out_data[nombre]['screen']
        [bi_y,bi_x,bi_z]=bi.shape
        try:
            for mod in local_data['inf_mods']:
                for frame in out_data[mod]['frames'].keys():
                    si=out_data[mod]['frames'][frame]
                    [si_y,si_x,si_z]=si.shape

                    if ((si_x+x<=bi_x) and (si_y+y<=bi_y)):
                        bi[y:si_y+y,x:si_x+x,:] = si#[0:si_y,0:si_x,:]
                        x = x + si_x
                        if (si_y>ymax):
                            ymax=si_y
                    else:
                        y = ymax
                        x=0
                        if ((si_x+x<=bi_x) and (si_y+y<=bi_y)):
                            bi[y:si_y+y,x:si_x+x,:] = si#[0:si_y,0:si_x,:]
                            x = x + si_x
                            if (si_y>ymax):
                                ymax=si_y
            #y = y + ymax
            #x=0 #Tocado
        except:
            x, y = 0, 0

        #cv2.putText(alarms,to,(100,100), font, 1,(0,0,0),2)
        si=alarms
        [si_y,si_x,si_z]=si.shape
        if ((si_x+x<=bi_x) and (si_y+y<=bi_y)):
            bi[y:si_y+y,x:si_x+x,:] = si#[0:si_y,0:si_x,:]
            x = x + si_x
            if (si_y>ymax):
                ymax=si_y
        #x=si_x

        si=stadistics
        [si_y,si_x,si_z]=si.shape
        [si_y,si_x,si_z]=si.shape
        if ((si_x+x<=bi_x) and (si_y+y<=bi_y)):
            bi[y:si_y+y,x:si_x+x,:] = si#[0:si_y,0:si_x,:]
            x = x + si_x
            if (si_y>ymax):
                ymax=si_y
        
        cv2.imshow('PYVISIONAPP', out_data[nombre]['screen'])
        cv2.waitKey(1)


    def onError(self,nombre,local_data, out_data):
        None
    
    def event (self, nombre, local, out, event, event_sync):
        None

    def end (self, nomre, local_data, out_data):
        None

#* * * * * * * * * * * * * * * * * * * * * * * * * * * *#

