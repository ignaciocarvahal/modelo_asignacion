# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 11:46:20 2023

@author: Ignacio Carvajal
"""
import pywhatkit as kit
import datetime
import time
from connection import * 

def message(numero_destino):
    mensaje = "¡Hola! el modelo está listo! : https://transportesnm-my.sharepoint.com/:f:/g/personal/icarvajal_transportesnm_cl/EnsvZlQ1NtRBrfsuZCoFUcoBvtYB8GGYXYh65y6PpPXwtg?e=vhm4Hr"
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



def resumen(numero_destino, numero_camiones, total_presentaciones, total_retiros, hora_peak, cantidad_chasis, cantidad_chasis_20, fecha):
    # Convertir la cadena a un objeto datetime
    fecha_objeto = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
    print(fecha_objeto)
    # Formatear la fecha en el nuevo formato
    fecha = str(fecha_objeto.strftime("%d-%m-%Y"))
    
    query = f'''SELECT
  
  ---DISTINCT ser.id,
  comer.usu_nombre as Comercial,
  COUNT(comer.usu_rut) as Cantidad_de_servicios
FROM
  public.servicios as ser
INNER JOIN
  public.usuarios as comer ON ser.fk_comercial = comer.usu_rut
LEFT JOIN
  public.servicios_etapas as eta_1 ON ser.id = eta_1.fk_servicio
WHERE
  ser.estado = 1
  AND (
    eta_1.fecha > TO_CHAR(CURRENT_DATE - INTERVAL '4 days', 'DD-MM-YYYY')
    OR ser.id IN (
      SELECT DISTINCT s.id
      FROM public.servicios as s
      INNER JOIN public.servicios_etapas as eta_1_sub ON s.id = eta_1_sub.fk_servicio
      WHERE eta_1_sub.fecha > TO_CHAR(CURRENT_DATE - INTERVAL '4 days', 'DD-MM-YYYY')
    )
  )
  AND ser.fk_tipo_carga != 'lcl'
  AND eta_1.fecha = '{fecha}'
  AND eta_1.tipo = 2
GROUP BY
  comer.usu_rut
;'''
    
        

    fecha = f'''{fecha}'''
    print(f'''{fecha}''')
    presentaciones_por_comercial = connectionDB_todf(query).to_string(index=False) 
    print(presentaciones_por_comercial)
    mensaje = f"""
                Resumen para el día {fecha}

                Minimo {numero_camiones} transportistas.
                Minimo {cantidad_chasis} chasis de veinte + multi.
                Minimo  {cantidad_chasis_20} chasis de veinte
                Presentaciones: {total_presentaciones}
                Retiros: {total_retiros}
{presentaciones_por_comercial}
                
                

               """
    max_intentos = 4
    
    for intento in range(max_intentos):
        hora_actual = datetime.now().time()
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
  
  
#pruebas

#resumen('+56988876774', 70, 50, 120, '00:00', 13, 40,  '2024-03-09 00:00:00')