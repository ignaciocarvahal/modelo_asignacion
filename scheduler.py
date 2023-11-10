# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 10:35:02 2023

@author: Ignacio Carvajal
"""

import pandas as pd
import schedule
import time
import datetime
from main import Assignament
from programacion_ws import excel_to_df, insertar_dataframe_en_data_demurrage

def model_execution():
    # Obtener la fecha actual
    current_date = datetime.datetime.now().date()

    # Calcular la fecha del día siguiente
    next_day = current_date + datetime.timedelta(days=1)

    # Crear objetos de fecha y hora para el inicio y fin del día siguiente
    start_date = datetime.datetime.combine(next_day, datetime.time(0, 0))
    end_date = datetime.datetime.combine(next_day, datetime.time(23, 59))

    assignament = Assignament(60*0, start_date, end_date, "+56998900893", False, True)
    assignament.reset()

    df, n_camiones, total_camioneros = assignament.execute()
    df = excel_to_df()
    #print(df.columns)
    insertar_dataframe_en_data_demurrage(df)
    # print("numero de camioneros", n_camiones)

def model_execution_today():
    # Obtener la fecha actual
    current_date = datetime.datetime.now().date()

    # Crear objetos de fecha y hora para el inicio y fin del día siguiente
    start_date = datetime.datetime.combine(current_date, datetime.time(0, 0))
    end_date = datetime.datetime.combine(current_date, datetime.time(23, 59))

    assignament = Assignament(60*0, start_date, end_date, "+56998900893", True, False)
    assignament.reset()

    df, n_camiones, total_camioneros = assignament.execute()
    # print("numero de camioneros", n_camiones)
    df = excel_to_df()
    #print(df.columns)
    insertar_dataframe_en_data_demurrage(df)

def job():
    
    print("Ejecutando el script...")
    model_execution()
    print("Script ejecutado.")

def job_today():
    print("Ejecutando el script...")
    model_execution_today()
    print("Script ejecutado.")
    
# Programar la ejecución del script todos los días a las 13:00 y 16:30
schedule.every().day.at("10:00").do(job_today)
schedule.every().day.at("13:35").do(job)
schedule.every().day.at("15:35").do(job)
schedule.every().day.at("17:48").do(job)
schedule.every().day.at("20:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
