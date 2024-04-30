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

def obtener_datos_mensaje(fecha):
    
    # Convertir la cadena a un objeto datetime
    fecha_objeto = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
    #print(fecha_objeto)
    # Formatear la fecha en el nuevo formato
    fecha = str(fecha_objeto.strftime("%d-%m-%Y"))
    #from datetime import datetime, timedelta
    
    # Define las fechas de inicio y fin para tu consulta
    #fecha_inicio = datetime.now() + timedelta(days=1)
    #fecha_fin = datetime.now() + timedelta(days=2)
    
    # Convierte las fechas al formato de cadena adecuado
    #fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    #fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
    
    
    
    query_enrolados = '''
        SELECT
        SUM( CASE WHEN usu.ult_empt_tipo='PROPIO' then 1 else 0 end) as tot_tnm
        , SUM( CASE WHEN usu.ult_empt_tipo='ASOCIADO' then 1 else 0 end) as tot_tercero
        from public.usuarios as usu
        where
        usu_tipo=2
        and usu_estado=0
        ;

    '''
    
    df_enrolados = connectionDB_todf(query_enrolados)#.to_string(query_enrolados)
    
  
    n_total_propios = str(df_enrolados['tot_tnm'][0])
    n_total_asociados = str(df_enrolados['tot_tercero'][0])
    
    query = f'''SELECT
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

                  AND ser.fk_tipo_carga != 'lcl'
                  AND eta_1.fecha = '{fecha}'
                  AND eta_1.tipo = 2
                GROUP BY
                  comer.usu_rut
                ;'''
    
    query_cond_propios = f'''
                SELECT
                          CAST("personas"."tabla_hechos"."dia" AS date) AS "dia",
                          "Dimension Usuario"."empleado_tipo" AS "Dimension Usuario__empleado_tipo",
                          {n_total_propios} - count(distinct "Dimension Usuario"."rut_conductor") AS "count"
                        FROM
                          "personas"."tabla_hechos"
                         
                        LEFT JOIN "personas"."dimension_usuario" AS "Dimension Usuario" ON "personas"."tabla_hechos"."dia_libre_id" = "Dimension Usuario"."dia_libre_id"
                          LEFT JOIN "personas"."dimension_tipo_permiso" AS "Dimension Tipo Permiso" ON "personas"."tabla_hechos"."dia_libre_id" = "Dimension Tipo Permiso"."dia_libre_id"
                        WHERE
                          (
                            "personas"."tabla_hechos"."dia" >= CAST((NOW() + INTERVAL '1 day') AS date)
                          )
                         
                           AND (
                            "personas"."tabla_hechos"."dia" < CAST((NOW() + INTERVAL '2 day') AS date)
                          )
                          AND ("Dimension Usuario"."estado_empleado2" = 0)
                          AND ("Dimension Usuario"."tipo_empleado" = 2)
                          AND ("Dimension Usuario"."empleado_tipo" = 'PROPIO')
                        GROUP BY
                          CAST("personas"."tabla_hechos"."dia" AS date),
                          "Dimension Usuario"."empleado_tipo"
                        ORDER BY
                          CAST("personas"."tabla_hechos"."dia" AS date) ASC,
                          "Dimension Usuario"."empleado_tipo" ASC
    '''
    #print(query_cond_propios)
    query_cond_asociados = f'''
        SELECT
          CAST("personas"."tabla_hechos"."dia" AS date) AS "dia",
          "Dimension Usuario"."empleado_tipo" AS "Dimension Usuario__empleado_tipo",
          {n_total_asociados} - count(distinct "Dimension Usuario"."rut_conductor") AS "count"
        FROM
          "personas"."tabla_hechos"
         
        LEFT JOIN "personas"."dimension_usuario" AS "Dimension Usuario" ON "personas"."tabla_hechos"."dia_libre_id" = "Dimension Usuario"."dia_libre_id"
          LEFT JOIN "personas"."dimension_tipo_permiso" AS "Dimension Tipo Permiso" ON "personas"."tabla_hechos"."dia_libre_id" = "Dimension Tipo Permiso"."dia_libre_id"
        WHERE
          (
            "personas"."tabla_hechos"."dia" >= CAST((NOW() + INTERVAL '1 day') AS date)
          )
         
           AND (
            "personas"."tabla_hechos"."dia" < CAST((NOW() + INTERVAL '2 day') AS date)
          )
          AND ("Dimension Usuario"."estado_empleado2" = 0)
          AND ("Dimension Usuario"."tipo_empleado" = 2)
          AND ("Dimension Usuario"."empleado_tipo" = 'ASOCIADO')
          AND (
          ("Dimension Usuario"."estado_empleado" <> 1)
         
          OR ("Dimension Usuario"."estado_empleado" IS NULL)
        )
          
        GROUP BY
          CAST("personas"."tabla_hechos"."dia" AS date),
          "Dimension Usuario"."empleado_tipo"
        ORDER BY
          CAST("personas"."tabla_hechos"."dia" AS date) ASC,
          "Dimension Usuario"."empleado_tipo" ASC
    '''
    
    fecha = f'''{fecha}'''

    propios_disponibles = connectionDW_todf(query_cond_propios)['count'].iloc[0]
    asociados_disponibles = connectionDW_todf(query_cond_asociados)['count'].iloc[0]
    return connectionDB_todf(query).to_string(index=False), propios_disponibles, asociados_disponibles

    
    
    
    

def resumen(numero_destino, numero_camiones, total_presentaciones, total_retiros, hora_peak, cantidad_chasis, cantidad_chasis_20, fecha, n_terceros, n_porteadores):

    

    presentaciones_por_comercial, propios_disponibles, asociados_disponibles = obtener_datos_mensaje(fecha)
    total_cond_disp = int(propios_disponibles) + int(asociados_disponibles)
    
    resta_camiones =  int(numero_camiones) - int(total_cond_disp)
    camiones_faltantes = max(0, resta_camiones)
    mensaje = f"""
    
    *PLANIFICACIÓN*
    {fecha}
    
    *CAMIONES FALTANTES: {camiones_faltantes}* ({n_terceros} terceros y {n_porteadores} porteadores)
    
    *Requerimiento estimado*
                    *Minimo {numero_camiones} transportistas.*
                    Minimo {cantidad_chasis} chasis de veinte + multi.
                    Minimo  {cantidad_chasis_20} chasis de veinte
    
    *Camiones Disponibles*
                    Propios: {propios_disponibles}
                    Asociado: {asociados_disponibles}
                    TOTAL: {total_cond_disp}
    
    *Servicios Solicitados:*                
                    Presentaciones: {total_presentaciones}
                    Retiros: {total_retiros}
    
    *Servicios Solicitados por ejecutivo:*
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
#
#resumen('+56988876774', 70, 50, 120, '00:00', 13, 40,  '2024-03-09 00:00:00', 2, 3)