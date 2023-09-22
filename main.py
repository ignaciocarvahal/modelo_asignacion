# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 15:04:15 2023

@author: Ignacio Carvajal
"""

# import all the libraries
import pyscipopt as scip
import time
import pandas as pd
import numpy as np
import random
import os
import psycopg2
from datetime import datetime
from connection import *
from models import *
from utils2 import preprocess, time_filler, date_filter, group_by_id, merge
from gantt import *
from dfconsumer import df_portuarios
from whatpy import message
import datetime

class Assignament:
    def __init__(self, olgura, start_date, end_date, cellphone, mostrar_info, download=True, T_estimado_retiros=40,  T_estimado_presentacion=180, T_estimado_descargas=10, T_viaje_retiros_SAI=30, T_viaje_retiros_STGO=160, T_viaje_retiros_VAL=120):

        self.df = {}
        self.df_visualization = {}
        self.olgura = olgura
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.min_hora_inicio = np.zeros(len(self.df))
        self.max_hora_salida = np.zeros(len(self.df))
        self.cellphone = cellphone
        self.trackers = []
        self.Iv = []
        self.inicios = {}
        self.Fv = {}
        self.duration = {}
        self.mostrar_info = mostrar_info
        self.download = download

    def Querys(self):

        # Obtener la fecha que vamos a correr
        fecha = start_date 

        # Formatear la fecha como una cadena (por ejemplo, "2023-09-22")
        fecha_formateada = fecha.strftime("%Y-%m-%d")
        directory = os.getcwd()
        
        # Directorio donde crear la carpeta
        directorio_base = directory + "\\static\\tmp\\"  # Ruta base donde deseas crear la carpeta
        
        # Comprobar si la carpeta ya existe antes de crearla
        if not os.path.exists(os.path.join(directorio_base, fecha_formateada)):
            os.mkdir(os.path.join(directorio_base, fecha_formateada))
        
        
        with open(directory + "\\queries\\new_travels.txt", "r") as archivo:
            contenido = archivo.read()
        query = contenido
        
        fecha_ahora = datetime.datetime.now()

        # Formatear la fecha y hora como una cadena
        fecha_hora_formateada = fecha_ahora.strftime("%Y-%m-%d %H:%M:%S")
        # Reemplazar ":" por "_" en la hora
        fecha_hora_formateada = fecha_hora_formateada.replace(":", "-")        
        
        
        
        df = connectionDB_todf(query)
        df.to_excel( directory + "\\static\\tmp\\" + str(fecha_formateada) + "\\query_travels" + str(fecha_hora_formateada) + ".xlsx", index=False)
        df = transform_dataframe(df)
        
        pd.set_option('display.float_format', '{:.0f}'.format)
        
        df = merged()
        df = rename_df(df)
        
        self.df = df

        df = pd.DataFrame(self.df)


        query_trackers = "SELECT DISTINCT ON (usu_rut) nombre, ult_empt_tipo FROM public.timeline_programacion_conductores WHERE tipo_fecha != 'SINDISPONIBILIDAD'  and fecha_desde > '04-08-2023' and fecha_hasta < '06-08-2023' ORDER BY usu_rut, fecha_desde;"
        rows = connectionDB(query_trackers)
        trackers = []
        for row in rows:
            if str(row[1]) == 'PROPIO':
                trackers.append((str(row[0]), str(row[1]), 0))
            elif str(row[1]) == 'ASOCIADO':
                trackers.append((str(row[0]), str(row[1]), 1))
            elif str(row[1]) == 'TERCERO':
                trackers.append((str(row[0]), str(row[1]), 2))

        trackers = sorted(trackers, key=lambda x: x[2])
        self.trackers = []
        for trucker in trackers:
            self.trackers.append(str((trucker[0], trucker[1])))
        print(len(self.trackers))



    def preprocessing(self):
        try: 
            df_port = df_portuarios(self.start_date, self.end_date, self.download)
        except:
            print('Error al descargar directos diferidos')
            df_port = pd.DataFrame(columns=['contenedor', 'fecha', 'comuna', 'empresa', 'servicios', 'cont_tamano', 'contenedor_peso'])

        self.df = preprocess(self.df)
        # print("hola", self.df)
        self.df = date_filter(self.df, self.start_date, self.end_date)
        # print("hola2", self.df)
        self.df, self.df_visualization = time_filler(self.df, df_port)
        self.df = self.df[["id", "hora_salida", "hora_llegada"]]
        print(self.df_visualization.columns)
        
        self.df, self.min_hora_inicio, self.max_hora_salida = group_by_id(
            self.df_visualization)
        
        n_truckers_ini = int(len(set(self.df_visualization["id"])) * 1) + 1
        n_truckers_ini = 90
        self.trackers = []
        for i in range(n_truckers_ini):
            self.trackers.append(str((i, i)))
        

    def model_dict(self):
        min_hora_inicio, max_hora_salida = self.min_hora_inicio, self.max_hora_salida
        # print(min_hora_inicio)
        for i, id in enumerate(set(self.df['id'])):
            if type(min_hora_inicio.iloc[i]) == float:
                min_hora_inicio.iloc[i] = datetime.fromtimestamp(
                    min_hora_inicio.iloc[i])
            if type(max_hora_salida.iloc[i]) == float:
                max_hora_salida.iloc[i] = datetime.fromtimestamp(
                    max_hora_salida.iloc[i])

            self.Iv.append(id)
            self.inicios = min_hora_inicio.to_dict()

            for id, fecha in self.inicios.items():
                self.inicios[id] = fecha.timestamp()
            self.Fv = max_hora_salida.to_dict()
            for id, fecha in self.Fv.items():
                self.Fv[id] = fecha.timestamp()
                
            self.duration[id] = max_hora_salida.iloc[i].timestamp() - \
                min_hora_inicio.iloc[i].timestamp()

    def execute(self):

        # Resolver el modelo y medir el tiempo de resolución
        start_time = time.time()
        df, n_camiones, total_camiones = secuencial_problem(
            self.df_visualization, self.inicios, self.Fv, self.Iv, 50, self.trackers, self.olgura, self.start_date, self.end_date, self.mostrar_info)
        end_time = time.time()

        # Obtener el tiempo de resolución en segundos
        solve_time = end_time - start_time
        print("Demoro " + str(solve_time/60) + " minutos")
        directory = os.getcwd()
        # Asegúrate de que el nombre del archivo sea correcto
        datos = pd.read_excel(directory + '\\static\\tmp\\planificacion.xlsx')
        
        try:
            message(self.cellphone)
        except:
            print("mensaje fallido")

        return df, n_camiones+1, total_camiones

    def reset(self):
        print("doing querys")
        self.Querys()
        print("preprocessing")
        self.preprocessing()
        print("dict")
        self.model_dict()




"""
# Input date string
start_string = '2023-09-25 00:00:00'
end_string = '2023-09-25 23:59:00'

# Convert to a pandas datetime object
start_date = pd.to_datetime(start_string)
end_date = pd.to_datetime(end_string)

assignament = Assignament(-60*0, start_date, end_date, '+56998900893', False, False)

assignament.reset()

df, n_camiones, total_camioneros = assignament.execute()
# print("numero de camioneros", n_camiones)


WHERE
  /* 1 en transito 2 cerrado */
  ser.estado = 1
"""
