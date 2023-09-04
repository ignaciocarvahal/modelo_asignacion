# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 12:22:00 2023

@author: Ignacio Carvajal
"""

import pandas as pd 
import numpy as np
import random
import os
import psycopg2
from datetime import datetime
"""
    # connection details
    host = "127.0.0.1"
    port = "5432"
    user = "postgres"
    password = "gauss7720"
    database = "topusDB"
"""

def connectionDB(query):

        # Datos de conexión
    host = "190.171.188.230"
    port = "5432"  # Puerto predeterminado de PostgreSQL
    database = "topusDB"  # Reemplazar por el nombre real de la base de datos
    user = "user_solo_lectura"
    password = "4l13nW4r3.C0ntr4s3n4.S0l0.L3ctur4"
    #connection 
    try:
        # Establecer la conexión
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        print("Conexión exitosa a la base de datos PostgreSQL")
    except (Exception, psycopg2.Error) as error:
        print("Error al conectarse a la base de datos PostgreSQL:", error)
    # execute the query 
    cursor = connection.cursor()
    cursor.execute(query)

    rows = cursor.fetchall()
    #close the cursor
    cursor.close()
    return rows

