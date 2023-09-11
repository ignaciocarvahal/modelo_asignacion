# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 16:37:13 2023

@author: Ignacio Carvajal
"""
# import all the libraries
#import pyscipopt as scip
import time
import pandas as pd
import numpy as np
import random
import os
#import psycopg2
from datetime import datetime
#from connection import *
#from travel_dataframe import *
import time
from flask import Flask, render_template, request, redirect, url_for
from main import Assignament
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import schedule
import time
import psycopg2

# Resto del código del archivo Python...
# Función para insertar los datos en la tabla 'parametros'
def insert_into_parametros(status, olgura, fecha, inicio, final):
    connection = None
    try:
        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(
            host="3.91.152.225",
            port="5432",
            user="postgres",
            password="ignacio",
            database="modelo_opti"
        )

        cursor = connection.cursor()

        # Insertar los datos en la tabla parametros
        insert_query = "INSERT INTO parametros (status, olgura, fecha, inicio, final) VALUES (%s, %s, %s, %s, %s);"
        cursor.execute(insert_query, (status, olgura, fecha, inicio, final))

        # Confirmar la transacción
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error al insertar en la tabla parametros:", error)

    finally:
        # Cerrar la conexión
        if connection:
            cursor.close()
            connection.close()

# Función para actualizar el status del último registro en la tabla 'parametros'
def update_status(status):
    connection = None
    try:
        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(
            host="3.91.152.225",
            port="5432",
            user="postgres",
            password="ignacio",
            database="modelo_opti"
        )

        cursor = connection.cursor()

        # Obtener el ID del último registro con status = 1
        select_query = "SELECT id FROM parametros WHERE status = 1 ORDER BY id DESC LIMIT 1;"
        cursor.execute(select_query)
        result = cursor.fetchone()

        if result:
            registro_id = result[0]
            # Actualizar el status del registro encontrado a 0
            update_query = "UPDATE parametros SET status = 0 WHERE id = %s;"
            cursor.execute(update_query, (registro_id,))
            connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error al actualizar el status en la tabla parametros:", error)

    finally:
        # Cerrar la conexión
        if connection:
            cursor.close()
            connection.close()

# Función para ejecutar el modelo con los parámetros del último registro con status = 1
def run_model_from_db():
    connection = None
    start_date = None 
    end_date = None
    download = False
    try:
        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(
            host="3.91.152.225",
            port="5432",
            user="postgres",
            password="ignacio",
            database="modelo_opti"
        )

        cursor = connection.cursor()

        # Obtener el último registro con status = 1
        select_query = "SELECT * FROM parametros ORDER BY id DESC LIMIT 1;"
        cursor.execute(select_query)
        result = cursor.fetchone()
        print(result)
        if result:
            # Obtener los valores del registro
            status = result[1]
            olgura = result[2]
            fecha = result[3]
            inicio = result[4]
            final = result[5]
            phone_number = result[6]
            download_base = result[8]
            start_string = str(fecha) + ' ' + str(inicio) 
            
            
            
            end_string = str(fecha) + ' ' + str(final) 
            
            if str(download_base) == 'True':
                download = True
            else:
                download = False
            
            print(download)
            if status==1:
                # Convert to a pandas datetime object
                start_date = pd.to_datetime(start_string)
                end_date = pd.to_datetime(end_string)
            
                # Ejecutar el modelo con los parámetros del registro
                assignament = Assignament(olgura*60, start_date, end_date, phone_number, True, download)
           
                assignament.reset()
              
                df, n_camiones, total_camioneros = assignament.execute()
               
            else:
                pass
            # Actualizar el status del registro a 0 después de ejecutar el modelo
            update_status(0)

    except (Exception, psycopg2.Error) as error:
        print("Error al obtener y ejecutar el modelo desde la tabla parametros:", error)

    finally:
        # Cerrar la conexión
        if connection:
            cursor.close()
            connection.close()


# Tarea programada para verificar y ejecutar el modelo cada 5 segundos
def scheduled_task():
    run_model_from_db()

# Configurar la tarea programada cada 5 segundos
schedule.every(5).seconds.do(scheduled_task)

app = Flask(__name__)

# Configura la clave secreta para la sesión
app.config['SECRET_KEY'] = 'mi_clave_secreta'

# Configura la extensión Flask-Session para que use el sistema de archivos para almacenar las sesiones
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configurar la tarea programada cada 5 segundos
schedule.every(5).seconds.do(scheduled_task)

if __name__ == '__main__':
    # Ejecutar la tarea programada en segundo plano
    while True:
        schedule.run_pending()
        time.sleep(1)