import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import ast

def match_tipo(titulo):
    match titulo:
        case 'retiro_full_val':
            return 'RETIRO CONTENEDOR FULL'
        case 'retiro_full_sai':
            return 'RETIRO CONTENEDOR FULL'
        case 'almacenamiento':
            return 'ALMACENAMIENTO'
        case 'trayecto':
            return 'TRAYECTO'
        case 'presentacion':
            return 'PRESENTACION EN CLIENTE'
        case 'devolucion_vacio_sai':
            return 'DEVOLUCION VACIO'
        case 'devolucion_vacio_val':
            return 'DEVOLUCION VACIO'
        case _:
            return titulo
        
def cargar_modelo(df):
    user = 'postgres'
    password = 'ignacio'
    host = '54.160.143.94'
    port = '5432'
    database = 'topusDBbackup2'
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
    
    # Convertir las cadenas de las tuplas a tuplas reales
    df['Trackers'] = df['Trackers'].apply(ast.literal_eval)
    
    # Separar las tuplas de la columna 'Trackers' en columnas separadas
    df[['Nombre', 'Tipo', 'Valor1', 'Valor2', 'Documento']] = pd.DataFrame(df['Trackers'].tolist(), index=df.index)

    #print(df.columns)
    # Eliminar la columna 'Trackers' original
    df.drop(columns=['Trackers', 'Valor1', 'Valor2'], inplace=True)
    '''
    #df = df.drop(df.columns[0], axis=1)
    df = df.rename(columns= {
        'id': 'fk_servicio',
        'etapa': 'titulo',
        'DT inicio': 'fecha_desde',
        'DT final': 'fecha_hasta'
    })

    df['titulo'] = df['titulo'].apply(match_tipo)
    
    df['cond_rut'] = df['Trackers'].apply(
        lambda x: x.split(',')[4].replace("'", "").replace(")", "").strip()
    )
    df['cond_nombre'] = df['Trackers'].apply(
        lambda x: x.split(',')[0].replace("'", "").replace("(", "").strip()
    )
    df['cond_tipo'] = df['Trackers'].apply(
        lambda x: x.split(',')[1].replace("'", "").replace("(", "").strip()
    )
    
    print(df.columns)
    
    df_final = df[['fk_servicio', 'cond_rut', 'cond_nombre', 'cond_tipo', 'fk_etapa', 'titulo', 'fecha_desde', 'fecha_hasta']]
    '''
    
    df.to_sql('timeline_programacion_conductores_python', engine, index=False, if_exists='replace')
    
    print("subido! jdvkadsjkadv")



def connectionDB(query):

    user = 'postgres'
    password = 'ignacio'
    host = '54.160.143.94'
    port = '5432'
    database = 'topusDBbackup2'
    

    
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

query = 'select * from timeline_programacion_conductores_python'
#print(connectionDB(query))