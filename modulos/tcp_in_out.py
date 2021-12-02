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
import socket
import sys
import time
import json

#for create a new init config file
if (0):
    init_config = {}
    init_config['ip']= '127.0.0.1'
    init_config['port']= 2000
    init_config['labels']=['person', 'dog']
    init_config['debug']=1
    init_config['trigger_in']='1\n'
    init_config['trigger_out']='1'
    init_config['trigger_out_reset']='0'
    init_config['inference_modules']=['zcoral']
    with open('tcp_in_out/init_config.json', 'w') as outfile:
        json.dump(init_config, outfile)


class Modulo:
    def __init__(self):
        None


    def start(self,nombre,local_data, out_data):
        out_data[nombre]['error'] = {}
        nfile='modulos/' + local_data['modName'] +'/'
        if (len(local_data['args'])==0):    
            nfile = nfile+ 'init_config.json'
        else:
            nfile = nfile + local_data['args']
        with open(nfile) as json_file:
            self.init_data = json.load(json_file)

        out_data[nombre]['t_count'] = 0

        local_data['ip'] = self.init_data['ip']
        local_data['port'] = self.init_data['port']
        
        self.init_net(nombre, local_data, out_data)


        local_data['t_last_send'] = time.time()
        local_data['t_last_send_max'] = 100
        local_data['debug'] = self.init_data['debug']
        local_data['labels'] = self.init_data['labels']
        local_data['trigger_in']=self.init_data['trigger_in']
        local_data['trigger_out']=self.init_data['trigger_out']
        local_data['trigger_out_reset']=self.init_data['trigger_out_reset']
        local_data['inference_modules']=self.init_data['inference_modules']
        local_data['time'] = time.time()


    def work(self,nombre,local_data, out_data):
        try:
            data_in = local_data['sock'].recv(1024)
            data_in=data_in.decode()
            print(data_in)
            #Si ha recibido el flanco manda un 0
            if data_in == local_data['trigger_in']:
                self.send_data(nombre, local_data, out_data, local_data['trigger_out_reset'])
                out_data[nombre]['t_count'] = out_data[nombre]['t_count'] + 1

        except:
            None
        try:
            detected = 0
            for i in local_data['inference_modules']:#recorremos todos los modulos de deteccion                   
                for n in out_data[i]['detected']:#recorremos las camaras 
                    for d in out_data[i]['detected'][n]:#Recorremos las detecciones
                        #for label in d[label]:
                        for label_local in local_data['labels']:
                            if d['label'] == label_local:
                                detected = 1
            if detected:
                self.send_data(nombre, local_data, out_data, local_data['trigger_out'])
        except:
            None
        if (time.time()>(1+local_data['time'])):
            self.send_data(nombre, local_data, out_data, 'alive')
            local_data['time'] = time.time()


    def onError(self,nombre,local_data, out_data):
        self.init_net(nombre, local_data, out_data)
    
    def event (self, nombre, local, out, event, event_sync):
        None

    def end (self, nombre, local_data, out_data):
        None




    def init_net(self, nombre, local_data, out_data):
        if len (out_data[nombre]['error'].keys()):
            local_data['sock'].close()
            time.sleep(5)
        try:
            
            local_data['sock'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            local_data['sock'].connect((local_data['ip'],local_data['port']))
            local_data['sock'].settimeout(0.0001)
            out_data[nombre]['error'].pop(1)
        except:
            None
    
    def send_data (self, nombre, local_data, out_data, data):
        try:
            local_data['sock'].send(data.encode())
        except:
            out_data[nombre]['error'][1]='Error de red'    
