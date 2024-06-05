# import all the libraries
import pyscipopt as scip
import time
import pandas as pd
import numpy as np
import random
import os
import psycopg2
import datetime
from datetime import datetime
from datetime import datetime, timedelta
from funciones import *
from connection import *
from models import *
from utils2 import preprocess, time_filler, date_filter, group_by_id, merge
from gantt import *
from dfconsumer import df_portuarios
from whatpy import message, resumen
import datetime
import time 
import os
import pandas as pd

def tuplas_a_strings(tupla):
    return str(tupla)

def guardar_df_en_directorio_actual(dataframe, nombre_archivo):
    try:
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_guardado = os.path.join(directorio_actual, nombre_archivo)
        dataframe.to_excel(ruta_guardado, index=False)
        print(f"DataFrame guardado como {nombre_archivo} en el directorio actual: {directorio_actual}.")
    except Exception as e:
        print(f"Error al guardar el DataFrame: {str(e)}")
        

def cargar_excel_como_df(nombre_archivo):
    try:
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_excel = os.path.join(directorio_actual, nombre_archivo)
        
        # Utiliza pandas para leer el archivo Excel y convertirlo en un DataFrame
        df = pd.read_excel(ruta_excel)
        
        print(f"Archivo Excel '{nombre_archivo}' cargado como DataFrame:")
        
        return df
    except Exception as e:
        print(f"Error al cargar el archivo Excel como DataFrame: {str(e)}")
        return None

def determinar_tipo_viaje(grupo):

    if any(grupo['etapa_tipo'] == 2) and (any((grupo['etapa_tipo'] == 3) & (grupo['comuna_nombre']=='Valparaíso')) or any((grupo['etapa_tipo'] == 1) & (grupo['comuna_nombre']=='Valparaíso'))):
        return 'Puerto cruzado'
    
    elif  any(grupo['cont_tamano']== str(20)) and any(grupo['etapa_tipo'] == 2):
        return 'viaje_20'
    
    elif any(grupo['etapa_tipo'] == 2):
        return 'presentacion'
    
    elif any((grupo['etapa_tipo'] == 1) & (grupo['comuna_nombre']!='San Antonio')) :
        return 'retiro_val'

    elif any((grupo['etapa_tipo'] == 1) & (grupo['comuna_nombre']=='San Antonio')) :
        return 'retiro_sai'
    
    else:
        return 'otro_tipo'
    

    
def procesar_datos(df, fecha_filtro, fecha_referencia, fecha_referencia_fin):
    from datetime import datetime, timedelta
    
    # Obtener la fecha de mañana
    #fecha_de_mañana = datetime.now() + timedelta(days=1)
    #fecha_de_hoy_str = fecha_de_mañana.strftime("%d-%m-%Y")
    
    
    #fecha_inicio = fecha_inicio.strftime("%d-%m-%Y")
    #fecha_final = fecha_final.strftime("%d-%m-%Y")
    
    #df[df[["etapa_1_fecha"]]]
    
    
    
    #print(fecha_de_mañana_str, fecha_filtro)
    fecha_de_mañana_str = fecha_filtro
    #print(fecha_de_mañana_str)
    
    # Filtrar el DataFrame por el día de mañana
    df_mañana = df#[(df["etapa_1_fecha"] == fecha_de_mañana_str)]
    #df = preprocess(df)
    #df = date_filter(df, fecha_referencia, fecha_referencia_fin)
    return df_mañana.groupby('id').apply(determinar_tipo_viaje).to_dict()


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
        self.start_date = start_date 
        self.fecha_formateada = ''
        
    def Querys(self):
        
        espacio = """
        """
        
        print("inicializando fecha")
        # Obtener la fecha que vamos a correr
        fecha = self.start_date 
        # Formatear la fecha como una cadena (por ejemplo, "2023-09-22")
        fecha_formateada = fecha.strftime("%Y-%m-%d")
        self.fecha_formateada = fecha.strftime("%d-%m-%Y")
        print("La fecha ha sido formateada a %d-%m-%Y")
        
        
        
        print("definiendo fechas de hoy y mañana")
        fecha_ahora = datetime.datetime.now()
        
        fecha_de_hoy = fecha_ahora + timedelta(days=0)
        fecha_de_hoy_str = fecha_de_hoy.strftime("%d-%m-%Y")
        # Obtener la fecha de mañana
        fecha_de_mañana = fecha_ahora + timedelta(days=1)
        fecha_de_mañana_str = fecha_de_mañana.strftime("%d-%m-%Y")
        
        # Formatear la fecha y hora como una cadena
        fecha_hora_formateada = fecha_ahora.strftime("%Y-%m-%d %H:%M:%S")
        # Reemplazar ":" por "_" en la hora
        fecha_hora_formateada = fecha_hora_formateada.replace(":", "-")        
        
        print("han sido creadas fechas de hoy y mañana")    
        print(espacio)
        
        
        print("Creando directorio para guardar resultados")
        directory = os.getcwd()
        # Directorio donde crear la carpeta
        directorio_base = directory + "\\static\\tmp\\"  # Ruta base donde deseas crear la carpeta
        # Comprobar si la carpeta ya existe antes de crearla
        if not os.path.exists(os.path.join(directorio_base, fecha_formateada)):
            os.mkdir(os.path.join(directorio_base, fecha_formateada))
        print("directorio creado")
        print(espacio)
        
        
        print("leer query principal desde directorio y traerlas desde la base")

        with open(directory + "\\queries\\new_travels.txt", "r") as archivo:
            contenido = archivo.read()
        query = contenido
        

        nombre_archivo = "df.xlsx"
        #df = cargar_excel_como_df(nombre_archivo)
        
        print('query_de_viajes')
        df = connectionDB_todf(query)
        print('df de query de viajes (principal) cargada')
        print(espacio)
        

        print("Guadando df con las fechas en que se corrio")
        #print(df[['fk_servicio','etapa_1_conductor_nombre']])
        df.to_excel(directory + "\\static\\tmp\\" + str(fecha_formateada) + "\\query_travels" + str(fecha_hora_formateada) + ".xlsx", index=False)
        print('Excel guardado')
        print(espacio)
        
        
        print("Desde connection, se iguala la hora y fecha de la presentacion con la de devolución")
        df = transform_dataframe(df)
        print("horas listas para ser estimadas")
        print(espacio)
        
        
        pd.set_option('display.float_format', '{:.0f}'.format)
        print('Desde connection, estimamos las estadias en cliente ')
        df = merged()
        print("Estimación de estadias lista")
        print(espacio)
        
        
        print("ELegimos y renombramos las columnas (connection)")
        df = rename_df(df)
        

        
        print("Columnas elegidas y formateadas")
        print("Inicializamos self.df con este ultimo dataframe")
        self.df = df
        df = pd.DataFrame(self.df)
        print("Inicializando tipos de viaje: ptocruzado, porteo...")
        print("tipo_viaje", df.columns)
        #self.tipo_viaje = procesar_datos(df, self.fecha_formateada, self.start_date, self.end_date) 
        print("Tipos de viajes creados")
        print(espacio)
        
        
        print("Trayendo datos de conductores")
        query_trackers = f'''SELECT DISTINCT ON (usu_rut) nombre, ult_empt_tipo, usu_rut
                                FROM public.timeline_programacion_conductores 
                                WHERE tipo_fecha != 'SINDISPONIBILIDAD'  AND 
                                      TO_DATE(fecha_desde, 'DD-MM-YYYY') >= '{fecha_de_hoy_str}'
                                      AND TO_DATE(fecha_hasta, 'DD-MM-YYYY') <= '{fecha_de_mañana_str}'
                                      AND tipo_fecha = 'ETAPA'
                                      ORDER BY usu_rut, TO_DATE(fecha_desde, 'DD-MM-YYYY');'''
        
        
        query_trackers = f'''SELECT DISTINCT ON (usu_rut) nombre, ult_empt_tipo, usu_rut
                                FROM public.timeline_programacion_conductores 
                                WHERE tipo_fecha != 'SINDISPONIBILIDAD'  AND 
                                      TO_DATE(fecha_desde, 'DD-MM-YYYY') >= '{fecha_de_hoy_str}'
                                      AND TO_DATE(fecha_hasta, 'DD-MM-YYYY') <= '{fecha_de_mañana_str}'
                                      AND tipo_fecha = 'ETAPA'
                                      ORDER BY usu_rut, TO_DATE(fecha_desde, 'DD-MM-YYYY');'''
        rows = connectionDB(query_trackers)
        print("Datos recibidos")
        print(espacio)
        
        
        print("Creando conductores dicponibles")
        trackers = []
        porteadores = ['BETHI PROAÑO R', 'MIGUEL PEÑAHERRERA P', 'OSWALDO ESCALONA A', 'LUIS PAILLALEF P', 'PATRICIO PARDO V', 'CRISTIAN REAL M', 'YOSMAR PEREZ P', 'CRISTIAN REAL M']
       
        maximo = 80
        i=0
        
        for row in rows:
            if i < maximo:
                if str(row[0]) in porteadores:
                    trackers.append((str(row[0]), 'PORTEADOR', 0, 1, str(row[2])))
                    #print(str(row[0]))
                elif str(row[1]) == 'PROPIO' and not(str(row[0]) in porteadores):
                    trackers.append((str(row[0]), str(row[1]), 0, 1, str(row[2])))
                elif str(row[1]) == 'ASOCIADO':
                    trackers.append((str(row[0]), str(row[1]), 1, 1, str(row[2])))
                elif str(row[1]) == 'TERCERO':
                    trackers.append((str(row[0]), str(row[1]), 2, 0, str(row[2])))
            i += 1
            
        print("Conductores disponibles creados: ", len(trackers))
        
        print("Agregamos conductores ficticios")
        for j in range(70):
            if j % 2 or j % 3 or j % 5 == 0:
                trackers.append((str(f'''Porteador {j}'''), str('PORTEADOR_ext'), 0, 0, str('99.999.999-9')))
            else:
                trackers.append((str(f'''Tercero {j}'''), str('TERCERO'), 0, 0, str('99.999.999-9'))) 
                
        # Convertir la lista de tuplas a un DataFrame
        self.trackers = [x for x in trackers]
        self.tipo_tracker = pd.DataFrame(self.trackers, columns=['id', 'tipo_conductor', 'resp1', 'resp2', 'rut'])
        self.tipo_tracker = self.tipo_tracker.set_index('id')['tipo_conductor'].to_dict()
        self.trackers = [str(x) for x in trackers]
        print("Conductores creados")
        print(espacio)


    def preprocessing(self):
        
        espacio = """
        """
        
        print('Traemos datos del puerto con scraper')
        try: 
            df_port = df_portuarios(self.start_date, self.end_date, self.download)
        except:
            print('Error al descargar directos diferidos')
            df_port = pd.DataFrame(columns=['contenedor', 'fecha', 'comuna', 'empresa', 'servicios', 'cont_tamano', 'contenedor_peso', 'fk_etapa'])

        print("Sacamos vacios de coluna fechas")
        self.df = preprocess(self.df)
        print("Rellenamos fechas invalidas ")
        self.df = date_filter(self.df, self.start_date, self.end_date)
        print("Calculamos las horas de salida y llegada ademas agregar los retiros de puerto del scraper")
        print(espacio)
        
        print("Identificando servicios ya asignados")
        self.servicios_asignados = self.df[['id', 'etapa_1_conductor_rut']]#[self.df['etapa_1_conductor_rut']!='']
        # Convertir DataFrame a diccionario
        self.servicios_asignados = dict(zip(self.servicios_asignados['id'], self.servicios_asignados['etapa_1_conductor_rut']))
        #print(self.servicios_asignados.items())
        print("Servicios asignados reconocidos")
        print(espacio)
        
        print("Colocar fechas y horas de las etapas con estimaciones estadisticas")
        self.df, self.df_visualization = time_filler(self.df, df_port)
      
        print("tipo_viaje", self.df_visualization.head(5))
        self.tipo_viaje = procesar_datos(self.df_visualization, self.fecha_formateada, self.start_date, self.end_date) 
        #print(self.tipo_viaje)
        print("Horas por etapa fijadas")
        print(espacio)
        
        
        self.df = self.df[["id", "hora_salida", "hora_llegada"]]
        
        print("Sacar inicio y final de todas las etapas de cada servicio")
        self.df, self.min_hora_inicio, self.max_hora_salida = group_by_id(
            self.df_visualization)
        print("Inicios y finales calculados")
        print(espacio)
        
        
        print("Seleccionar cantidad de camioneros que entran al modelo")
        n_truckers_ini = initializator(self.df, self.fecha_formateada) + 16
        self.trackers = self.trackers[:n_truckers_ini]
        print("Camioneros seleccionados para el modelo: ", str(n_truckers_ini))
        print(espacio)
        
        
        #print(self.trackers)

    def model_dict(self):
        min_hora_inicio, max_hora_salida = self.min_hora_inicio, self.max_hora_salida
        # print(min_hora_inicio)
        #print(self.df['fk_etapa'])
        
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
        #print(self.trackers)
        # Resolver el modelo y medir el tiempo de resolución
        start_time = time.time()
        #print(self.inicios)
        df, n_camiones, total_camiones = secuencial_problem(self.servicios_asignados, self.tipo_viaje, self.tipo_tracker,self.df_visualization, self.inicios, self.Fv, self.Iv, 90, self.trackers, self.olgura, self.start_date, self.end_date, self.mostrar_info)
        end_time = time.time()
        
        # Obtener el tiempo de resolución en segundos
        solve_time = end_time - start_time
        print("Demoro " + str(solve_time/60) + " minutos")
        directory = os.getcwd()
        # Asegúrate de que el nombre del archivo sea correcto
        datos = pd.read_excel(directory + '\\static\\tmp\\planificacion.xlsx')
        
        try:
            print("mensaje")
            #message(self.cellphone)
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





#Input date string
start_string = '2024-06-05 17:00:00' 

end_string = '2024-06-06 23:59:00' 


# Convert to a pandas datetime object
start_date = pd.to_datetime(start_string)
end_date = pd.to_datetime(end_string)

assignament = Assignament(60*0, start_date, end_date, '', False, False)

assignament.reset()

df, n_camiones, total_camioneros = assignament.execute()

"""
debo crear una query que rankee por llegada 

el ultimo que llega es el ultimo que sale 

"""