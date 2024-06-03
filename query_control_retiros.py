# -*- coding: utf-8 -*-
"""
Created on Wed May 29 13:13:53 2024

@author: Ignacio Carvajal
"""

from connection import *
import pandas as pd 

def query_control_porteos():
    query = '''
    SELECT
      "public"."etapa"."codigo" AS "codigo",
      "Conductor"."rut" AS "Conductor__nombre",
      COUNT(*) AS "count"
    FROM
      "public"."etapa"
     
    LEFT JOIN "public"."conductor" AS "Conductor" ON "public"."etapa"."id_etapa" = "Conductor"."id_conductor"
      LEFT JOIN "public"."caracteristicas" AS "Caracteristicas" ON "public"."etapa"."id_etapa" = "Caracteristicas"."id_caracteristicas"
      LEFT JOIN "public"."time" AS "Time" ON "public"."etapa"."id_etapa" = "Time"."id_time"
    WHERE
      (
        ("Conductor"."tipo_conductor" = 'ASOCIADO')

      )
     
       AND (
        "Time"."etapa_1_fecha" >= CAST((NOW() + INTERVAL '-30 day') AS date)
      )
      AND (
        "Time"."etapa_1_fecha" < CAST((NOW() + INTERVAL '1 day') AS date)
      )
      AND (
        ("public"."etapa"."codigo" = '2')
        OR ("public"."etapa"."codigo" = '1')
      )
      AND (
        "Time"."etapa_1_fecha" >= timestamp with time zone '2024-05-09 00:00:00.000Z'
      )
    GROUP BY
      "public"."etapa"."codigo",
      "Conductor"."rut"
    ORDER BY
      "public"."etapa"."codigo" ASC,
      "Conductor"."rut" ASC
    
    
    '''
    
    df = connectionDW_todf(query)
    return df


# Definición de la función
def obtener_count(df, codigo, nombre):
    # Filtra el DataFrame por el código y nombre
    fila = df[(df['codigo'] == str(codigo)) & (df['Conductor__nombre'] == nombre)]
    
    # Si se encuentra la fila, devuelve el valor de 'count'
    if not fila.empty:
        return fila['count'].values[0]
    else:
        return 0

"""
df = query_control_porteos()

for nombre in df ['Conductor__nombre']:
    print(nombre, obtener_count(df, 2, nombre))
    print(nombre, obtener_count(df, 1, nombre))
    
"""