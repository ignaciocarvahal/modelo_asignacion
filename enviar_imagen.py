import os
from datetime import datetime, timedelta

def obtener_ultima_imagen(fecha):
    # Directorio actual
    directorio_actual = os.getcwd()
    
    # Fecha del día siguiente
    fecha_dia_siguiente = (fecha).strftime('%Y-%m-%d')
    
    # Directorio \static\tmp\{fecha_dia_siguiente}
    directorio_tmp = os.path.join(directorio_actual, 'static', 'tmp', fecha_dia_siguiente)
    
    # Lista para almacenar los archivos de imagen con rutas relativas
    extensiones_imagenes = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    archivos_imagenes = []
    
    # Revisar archivos en el directorio actual
    for archivo in os.listdir(directorio_actual):
        if os.path.isfile(os.path.join(directorio_actual, archivo)) and os.path.splitext(archivo)[1].lower() in extensiones_imagenes:
            archivos_imagenes.append(archivo)
    
    # Revisar archivos en el directorio \static\tmp\{fecha_dia_siguiente}
    if os.path.exists(directorio_tmp):
        for archivo in os.listdir(directorio_tmp):
            if os.path.isfile(os.path.join(directorio_tmp, archivo)) and os.path.splitext(archivo)[1].lower() in extensiones_imagenes:
                archivos_imagenes.append(os.path.join('static', 'tmp', fecha_dia_siguiente, archivo))
    
    # Ordenar los archivos alfabéticamente y obtener el último
    if archivos_imagenes:
        archivos_imagenes.sort()
        ultima_imagen = archivos_imagenes[-1]
    else:
        ultima_imagen = None
    
    return os.getcwd() + "/" + ultima_imagen





import pywhatkit as kit
import os

def enviar_imagen_whatsapp(numero, ruta_imagen):
    # Verificar si la imagen existe
    if not os.path.isfile(ruta_imagen):
        print("La imagen no existe en la ruta proporcionada.")
        return
    
    # Enviar la imagen usando pywhatkit
    try:
        kit.sendwhats_image(numero, ruta_imagen, caption="Aquí tienes la imagen que solicitaste")
        print("Imagen enviada con éxito a", numero)
    except Exception as e:
        print("Ocurrió un error al enviar la imagen:", str(e))


"""
# Llamar a la función y guardar la última imagen en una variable
ultima_imagen = obtener_ultima_imagen()


numero_destino = "+56988876774"  # Reemplaza con el número de teléfono destino


enviar_imagen_whatsapp(numero_destino, ultima_imagen)
"""