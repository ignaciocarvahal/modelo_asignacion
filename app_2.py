# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 09:57:05 2023

@author: Ignacio Carvajal
"""

# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import requests

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
import psycopg2




# Resto del código del archivo Python...
# Función para insertar los datos en la tabla 'parametros'
def insert_into_parametros(status, olgura, fecha, inicio, final):
    connection = None
    try:
        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(
            host="127.0.0.1",
            port="5432",
            user="postgres",
            password="gauss7720",
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


app = Flask(__name__)

# Configura la clave secreta para la sesión
app.config['SECRET_KEY'] = 'mi_clave_secreta'

# Configura la extensión Flask-Session para que use el sistema de archivos para almacenar las sesiones
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
def index():
    current_directory = os.getcwd()
    return render_template('index.html', current_directory=current_directory)

@app.route('/process_data', methods=['POST'])
def process_data():
    olgura = int(request.form['olugra'])
    start_date = str(request.form['start_date'])
    start_time = request.form['start_time']
    end_time = request.form['end_time']

    start_string = str(start_date) + ' ' + str(start_time) + ':00'
    end_string = str(start_date) + ' ' + str(end_time) + ':00'

    # Convert to a pandas datetime object
    start_date = pd.to_datetime(start_string)
    end_date = pd.to_datetime(end_string)

    # Guardar los valores en la sesión del usuario
    session['olgura'] = olgura * 60
    session['start_date'] = start_date
    session['end_date'] = end_date

    # Llamar a la función para insertar en la tabla 'parametros' con status = 1
    insert_into_parametros(status=1, olgura=olgura, fecha=str(start_date.date()), inicio=str(start_date.time()), final=str(end_date.time()))

    # Redireccionar a la página de animación
    return redirect(url_for('show_loading_animation'))

@app.route('/show_loading_animation')
def show_loading_animation():

    
    # Verificar el estado del último registro en la base de datos cada 5 segundos
    while True:
        status = get_last_record_status()
        if status == 1:
            # Mostrar la animación de carga
            pass
            #return render_template('loading_animation.html')
        elif status == 0:
            # Redireccionar a la página de resultados
            return redirect(url_for('show_results'))
        time.sleep(5)

# Función para obtener el estado del último registro en la tabla 'parametros'
def g2et_last_record_status():
    try:
        response = requests.get('http://127.0.0.1:5000/') # Cambiar la URL por la dirección de tu servidor Flask
        return response
    except requests.exceptions.RequestException as e:
        print("Error al obtener el estado del último registro:", e)
        return None
    
    
    
# Función para ejecutar el modelo con los parámetros del último registro con status = 1
def get_last_record_status():
    connection = None
    try:
        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(
            host="127.0.0.1",
            port="5432",
            user="postgres",
            password="gauss7720",
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
            return status


    except (Exception, psycopg2.Error) as error:
        print("Error al obtener status desde la tabla parametros:", error)

    finally:
        # Cerrar la conexión
        if connection:
            cursor.close()
            connection.close()

@app.route('/show_results')
def show_results():
    # ... Resto del código de lectura del archivo y preparación de datos como se muestra en la respuesta anterior ...

    # Obtener los valores de olgura, start_date y end_date desde la sesión del usuario
    olgura = session.get('olgura')
    start_date = session.get('start_date')
    end_date = session.get('end_date')
    n_camiones = session.get('n_camiones')

    # Pasar el valor total_camioneros a la plantilla show_results.html
    return render_template('show_results.html', total_camioneros=n_camiones)

if __name__ == '__main__':
    app.run(debug=True)