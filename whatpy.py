# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 11:46:20 2023

@author: Ignacio Carvajal
"""
import pywhatkit as kit
import datetime
import time

def message(numero_destino):
    mensaje = "¡Hola! el modelo está listo! : https://transportesnm-my.sharepoint.com/:f:/g/personal/icarvajal_transportesnm_cl/EgHz3_CiGn9PuEAChLdnbJ0BYj9wAgvJ5Z9WK5RGpvUGLA?e=lVV0ns"
    max_intentos = 4
    
    for intento in range(max_intentos):
        hora_actual = datetime.datetime.now().time()
        hora_envio = hora_actual.replace(minute=hora_actual.minute + 2)
        
        try:
            kit.sendwhatmsg(numero_destino, mensaje, hora_envio.hour, hora_envio.minute)
            print("Mensaje enviado exitosamente")
            break  # Salir del bucle si el envío fue exitoso
        except Exception as e:
            print(f"Error al enviar el mensaje (Intento {intento + 1}):", str(e))
            if intento < max_intentos - 1:
                print("Reintentando en 5 segundos...")
                time.sleep(5)  # Esperar 5 segundos antes de reintentar
            else:
                print("Máximo número de intentos alcanzado. No se pudo enviar el mensaje.")
