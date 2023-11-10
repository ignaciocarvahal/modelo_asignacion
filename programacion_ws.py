# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 11:28:02 2023

@author: Ignacio Carvajal
"""
import os
import time
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import stat
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
from datetime import datetime, timedelta
import pandas as pd
from connection import connectionDB
import psycopg2
from scrapper import encontrar_fila_con_similitud



def calcular_verificador_contenedor(numero_contenedor):
    letras = {
        'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17,
        'H': 18, 'I': 19, 'J': 20, 'K': 21, 'L': 23, 'M': 24, 'N': 25,
        'O': 26, 'P': 27, 'Q': 28, 'R': 29, 'S': 30, 'T': 31, 'U': 32,
        'V': 34, 'W': 35, 'X': 36, 'Y': 37, 'Z': 38, '?': 39, '0':0, 
        '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9
    }

    digitos_base = numero_contenedor[:10]
    suma = 0

    for i, caracter in enumerate(digitos_base):
        if caracter in letras:
            valor = letras[caracter]
            
            suma += valor * (2 ** i)

    verificador = suma % 11
    return str(verificador) if verificador < 10 else "0"




def concat_dataframes(dataframes_list):
    """
    Concatenates a list of DataFrames vertically (one after another),
    or returns the single DataFrame if there's only one in the list.
    
    Args:
        dataframes_list (list of pandas.DataFrame): List of DataFrames to be concatenated.
        
    Returns:
        pandas.DataFrame: Concatenated DataFrame if there are multiple DataFrames,
                          or the single DataFrame if there's only one.
    """
    if len(dataframes_list) < 1:
        # Crear un DataFrame vacío con las columnas requeridas
        column_names = ['Sigla', 'Numero', 'Dv', 'C.Alm', 'Desc. Alm', 'Descargado', 'Carga limpia',
            'Desp.Programado', 'Rango fecha', 'Fecha descarga', 'NAVE', 'ETA']
        
        df = pd.DataFrame(columns=column_names)
        return df
    
    elif len(dataframes_list) == 1:
        return dataframes_list[0]
    
    elif len(dataframes_list) >1:
        print(dataframes_list)
        concatenated_df = pd.concat(dataframes_list, ignore_index=True)
        return concatenated_df
    else:
        return pd.DataFrame()









def excel_to_df():
    directorio_actual = os.getcwd()
    sti_dir = directorio_actual + "\secuencias\sti"
    dfs = {}
    dfs["sti"] = []
    
    #sti
    for archivo in os.listdir(sti_dir):
        if archivo.endswith(".xls") or archivo.endswith(".xlsx"):
            archivo_ruta = os.path.join(sti_dir, archivo)
            df1 = pd.read_excel(archivo_ruta, header=0)  # Leer el archivo Excel y convertirlo en DataFrame
            # Patrón a buscar en el encabezado
            patron = 'Sigla Numero Dv C.Alm Desc. Alm Descargado Carga limpia Desp.Programado Rango fecha Fecha descarga NAVE ETA'
            # Encuentra el número de fila con la mejor similitud
            numero_de_fila = encontrar_fila_con_similitud(df1, patron)
            print("hoalsd", numero_de_fila)
            df = pd.read_excel(archivo_ruta, header=0)
            dfs["sti"].append(df)

    dfs["sti"] = concat_dataframes(dfs["sti"])
    
    return dfs["sti"]
    




        
        
        
        





def insertar_dataframe_en_data_demurrage(df):
    try:
        # Conectarse a la base de datos PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="data_demurrage",
            user="postgres",
            password="ignacio"
        )
        
        # Crear un cursor
        cursor = conn.cursor()

        # Iterar sobre filas del DataFrame
        for index, row in df.iterrows():
            # Verificar si Rango fecha no es nulo o vacío
            if pd.notna(row['Rango fecha']) and row['Rango fecha'] != '':
                
                # Construir el número de contenedor
                numero_verificador = calcular_verificador_contenedor(row['Sigla'] + str(row['Numero']))
                numero_contenedor = f"{row['Sigla']}{row['Numero']}{numero_verificador}"
                

                # Crear tupla de datos
                datos = (
                    numero_contenedor,
                    str(row['Rango fecha']),
                    str(row['Fecha descarga']),
                    str(row['ETA']),
                    str(row['NAVE']),
                    str(row['C.Alm']),
                    str(row['Desc. Alm']),
                    str(row['Descargado']),
                    str(row['Carga limpia']),
                    str(row['Desp.Programado'])
                )

                # Inserción de datos en la tabla data_demurrage con manejo de conflicto
                query = """
                    INSERT INTO public.data_demurrage (
                        numero_cont, 
                        rango_fecha, 
                        fecha_descarga, 
                        eta, 
                        nave,
                        "C.Alm",
                        "Desc. Alm",
                        "Descargado",
                        "Carga limpia",
                        "Desp.Programado"
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (numero_cont, fecha_descarga) DO NOTHING;
                """
                cursor.execute(query, datos)

        # Confirmar la transacción
        conn.commit()

        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()

        print("Inserción exitosa en la tabla data_demurrage")

    except (Exception, psycopg2.Error) as error:
        print(f"Error al insertar datos en la tabla data_demurrage: {error}")









#df = excel_to_df()
#print(df.columns)
#insertar_dataframe_en_data_demurrage(df)
#print(t_df)