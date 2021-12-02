# Lint as: python3
# Last modifications 2021 Jorge Saez Tejedor
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

import os
import sys
import time
import threading
import queue
import json


from numpy.core.fromnumeric import sort

path = "modulos/"
modulos = {}
modulos_var = {}
mod_var = {}
mod_var['local'] = {}
mod_var['out'] = {}

debug = 1
Exit = 0

#for create a new init config file
#modulos = [{'name':'opencv_cam1', 'modName':'opencv_cam', 'onThread':0, 'args': 'init_config_1cam.json'}, {'name':'realsense_2ir1', 'modName':'realsense_2ir', 'onThread':0, 'args': 'init_config_color.json'}, {'name':'jetson_inference1', 'modName':'jetson_inference', 'onThread':0, 'args': 'init_config_1cam1model.json'},
#             {'name':'zcoral1', 'modName':'zcoral' , 'onThread':0, 'args': ''}, {'name':'tcp_in_out', 'modName':'tcp_in_out' , 'onThread':0, 'args': ''}, {'name':'gui_opencv', 'modName':'gui_opencv', 'onThread':0, 'args': ''}]
#with open('init_config.json', 'w') as outfile:
#    json.dump(modulos, outfile)



#Cargamos modulos
sys.path.insert(0, path)
#Cargamos configuracion
with open('init_config.json') as json_file:
    modulos = json.load(json_file)


#for fname in modulos.keys():
#    listaHilos.append(0)

#INICIALIZAMOS VARIABLES A COMPARTIR
for index, mod1 in enumerate (modulos):
    fname = modulos[index]['name']
    mod = __import__(modulos[index]['modName'])
    modulos[index]['mod'] = mod.Modulo()
    mod_var['local'][fname] = {}
    mod_var['local'][fname]['Exit'] = 0
    mod_var['local'][fname]['fs'] = 1
    mod_var['local'][fname]['args'] = mod1['args']
    mod_var['local'][fname]['local_queue'] = queue.Queue()
    mod_var['local'][fname]['out_queue'] = queue.Queue()   
    mod_var['local'][fname]['thread'] = mod1['onThread']  
    mod_var['local'][fname]['modName'] =  modulos[index]['modName']  
 


    mod_var['out'][fname] = {}
    print (fname)

#Inicializamos

    nombre = mod1['name']
    modulo = modulos[index]['mod']

    try:
        mod_var_temp = {}
        mod_var_temp['out'] = mod_var['out'].copy()
        modulo.start(nombre, mod_var['local'][nombre],mod_var_temp['out'])
        #We only save the output data of the current module
        mod_var['out'][nombre] = mod_var_temp['out'][nombre]
        Exit = Exit + mod_var['local'][nombre]['Exit']
        if debug:
            print ('Iniciado el modulo ' + nombre)
    except:
        if debug:
            print ('Fallo al iniciar el modulo ' + nombre)

#Work loop
#cuenta = -1
while (Exit==0):
    for index, mod1 in enumerate (modulos):
        nombre = mod1['name']
        modulo = modulos[index]['mod']
        #if (1):
        try:
            time_now=  time.time()
            mod_var_temp = {}
            mod_var_temp['out'] = mod_var['out'].copy()
            #if ((mod_var['local'][nombre]['fs'] == 0) and (mod1['onThread']==1)):
            if (mod1['onThread']==1):
                mod_var['local'][nombre]['thread'] = threading.Thread(target=mod1['mod'].work, args=(nombre, mod_var['local'][nombre],mod_var_temp['out'],))
                mod_var['local'][nombre]['thread'].start()

                mod_var['local'][nombre]['fs']=0
            else:
                mod1['mod'].work(nombre, mod_var['local'][nombre],mod_var_temp['out'])
            
            #We only save the output data of the current module
            mod_var['out'][nombre] = mod_var_temp['out'][nombre]
            Exit = Exit + mod_var['local'][nombre]['Exit']
            try:
                mod_var['out'][nombre]['error'].pop(0)
            except:
                None

            if debug:
                
                time_cal= (time.time() - time_now)*1000
                print ('Ciclo del modulo ' + nombre + ' en: ' + str(time_cal) + ' ms')

                

        except:
        #else:
            #We only save the output data of the current module
            mod_var['out'][nombre] = mod_var_temp['out'][nombre]
            Exit = Exit + mod_var['local'][nombre]['Exit']
            mod_var['out'][nombre]['error'][0]= 'Fallo en el ciclo del modulo ' + nombre
            if debug:
                print ('Fallo en el ciclo del modulo ' + nombre)
    cuenta=0

#Error loop
    #for (nombre, modulo) in modulos.items():
    #for mod1 in modulos:
    for index, mod1 in enumerate (modulos):
        nombre = mod1['name']
        modulo = modulos[index]['mod']

        if (len(mod_var['out'][nombre]['error'])>0):
            try:
                mod_var_temp = {}
                mod_var_temp['out'] = mod_var['out'].copy()
                modulo.onError(nombre,mod_var['local'][nombre],mod_var_temp['out'])
                #We only save the output data of the current module
                mod_var['out'][nombre] = mod_var_temp['out'][nombre]
                Exit = Exit + mod_var['local'][nombre]['Exit']
                
                if (len(mod_var['out'][nombre]['error'])>0):
                    None


                if debug:
                    print ('Ciclo de error del modulo ' + nombre)
            except:
                if debug:
                    print ('Error en el Ciclo de error del modulo ' + nombre)
            
#End loop

#for (nombre, modulo) in modulos.items():
for mod1 in modulos:
    nombre = mod1['name']
    modulo = modulos[index]['mod']
    try:
        mod_var_temp = {}
        mod_var_temp['out'] = mod_var['out'].copy()
        modulo.end(mod_var['local'][nombre],mod_var_temp['out'])
        #We only save the output data of the current module
        mod_var['out'][nombre] = mod_var_temp['out'][nombre]
        if debug:
            print ('Finalizado el modulo ' + nombre)
    except:
        if debug:
            print ('Fallo al finalizar el modulo ')