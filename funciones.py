# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 09:25:30 2023

@author: Ignacio Carvajal
"""
from datetime import datetime
from datetime import datetime, timedelta
import pandas as pd


def generate_hours_for_date(date):
    # Convert the date into a datetime object
    date_obj = datetime.strptime(date, '%d-%m-%Y')
    
    # List of hours in 5-minute intervals
    hours = []
    for hour in range(0, 24):
        for minute in range(0, 60, 5):
            hour_formatted = f'{hour:02d}:{minute:02d}:{00:02d}'
            hours.append(hour_formatted)
    
    # Generate the list of dates with hours
    dates_with_hours = [date_obj + timedelta(hours=int(h.split(':')[0]), minutes=int(h.split(':')[1])) for h in hours]
    
    # Format the dates in the desired format 'dd-mm-yyyy HH:MM'
    formatted_dates = [f'{date_obj.strftime("%d-%m-%Y")} {hour.strftime("%H:%M:%S")}' for hour in dates_with_hours]
    
    return formatted_dates


def generate_availability_matrix(dataframe, dates_with_hours):
    # Inicializar la matriz con ceros
    availability_matrix = pd.DataFrame(0, columns=dates_with_hours, index=dataframe.index)
    
    # Iterar sobre las filas del DataFrame
    for index, row in dataframe.iterrows():
        #start_time = datetime.strptime(row['DT inicio'], '%Y-%m-%d %H:%M:%S')  # Convertir la hora de inicio a datetime
        #end_time = datetime.strptime(row['DT final'], '%Y-%m-%d %H:%M:%S')  # Convertir la hora de finalización a datetime
        
        start_time = row['DT inicio']  # Convertir la hora de inicio a datetime
        end_time = row['DT final']  # Convertir la hora de finalización a datetime
        
        # Marcar las horas en la matriz como 1 si están en el rango de tiempo
        for hour in dates_with_hours:
            hour_dt = datetime.strptime(hour, '%d-%m-%Y %H:%M:%S')
            if start_time <= hour_dt <= end_time:
                availability_matrix.loc[index, hour] = 1
    
    return availability_matrix




def sum_columns_in_matrix(matrix):
    # Suma las columnas de la matriz
    column_sums = matrix.sum()
    
    # Convierte las sumas en un diccionario
    hour_sum_dict = column_sums.to_dict()
    
    return hour_sum_dict



def find_max_hour(hour_sum_dict):
    max_hour = max(hour_sum_dict, key=hour_sum_dict.get)
    max_value = hour_sum_dict[max_hour]
    return max_hour, max_value


def check_threshold(hour_sum_dict, threshold):
    for hour, value in hour_sum_dict.items():
        if value > threshold:
            return False
    return True


def initializator(df,date):

    dates_with_hours = generate_hours_for_date(date)
    
    # Llama a la función para obtener la matriz de disponibilidad
    availability_matrix = generate_availability_matrix(df, dates_with_hours)
    
    # Llama a la función para obtener el diccionario
    hour_sum_dict = sum_columns_in_matrix(availability_matrix)
    
    # Ejemplo de uso con el diccionario hour_sum_dict
    max_hour, max_value = find_max_hour(hour_sum_dict)

    return max_value
"""
# Example of usage
date = '13-10-2023'


# Especifica la ruta del archivo Excel
archivo_excel = 'C:\\Users\\Usuario\\Desktop\\planificación\\static\\tmp\\planificacion3.xlsx'

# Utiliza pd.read_excel para leer el archivo Excel y crear un DataFrame
df = pd.read_excel(archivo_excel)

dates_with_hours = generate_hours_for_date(date)
print(dates_with_hours)

# Llama a la función para obtener la matriz de disponibilidad
availability_matrix = generate_availability_matrix(df, dates_with_hours)
print(availability_matrix)

# Llama a la función para obtener el diccionario
hour_sum_dict = sum_columns_in_matrix(availability_matrix)

print(hour_sum_dict)
# Ejemplo de uso con el diccionario hour_sum_dict
max_hour, max_value = find_max_hour(hour_sum_dict)

print(f"La hora con el valor máximo es {max_hour} y el valor máximo es {max_value}.")

"""