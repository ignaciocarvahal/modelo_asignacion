# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#import all the libraries
import pyscipopt as scip
import time
import pandas as pd 
import os
from datetime import datetime
import matplotlib.pyplot as plt
from utils2 import merge, delete, process_result
from gantt import *
import ast
from cargar_modelo import cargar_modelo



##############################################################################

#print("Tenemos " + str(len(Iv)) + " servicios")
#This parameter models the tolerance of our model towards the lateness of each travel.
#As there is more slack, our model becomes more conservative.


######D####################################################################

def obtener_elementos_mayores(diccionario, valor_limite):
    elementos_mayores = {clave: valor for clave, valor in diccionario.items() if valor > valor_limite}
    return elementos_mayores

    
def validator(v, j, tipo_viaje, tipo_tracker):
    #si es propio puede hacer cualquier viaje 
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO':
        return True
    
    #si es asociado no puede ir a retirar a valparaiso ni tampoco hacer viajes de 20
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO':
        return True
    
    #si es porteador o porteador externo solo puede ir a retiros de sai 
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR'  and tipo_viaje[v]=='retiro_sai':
        return True
    
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR_ext' and tipo_viaje[v]=='retiro_sai':
        return True
    
    #si es tercero no hace de viajes de 20 ni portea en valpo, ni hace puerto cruzado 
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'TERCERO' and  tipo_viaje[v] != 'retiro_val' and tipo_viaje[v] != 'Puerto cruzado':
        return True
    
    else:
        return False

def combinations(i, camioneros, tipo_viaje, tipo_tracker):
    # Aquí definimos todas las combinaciones de los viajes programados y los trackers que pueden hacerlo
    trios = []
    print("Se inician combinaciones")

    for v, t in i.items():
        for j in camioneros:
            if validator(v, j, tipo_viaje, tipo_tracker):
                #if tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR':
                    #print(tipo_tracker[ast.literal_eval(j)[0]] , tipo_viaje[v])

                trios.append((v, j, t))
            '''
            else:
                if tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR':
                    print(tipo_tracker[ast.literal_eval(j)[0]] , tipo_viaje[v])
            '''
    #trios.append((v, j, t))
    trios = set(trios)
    return trios

def camioneros_comp(v,camiones, tipo_viaje, tipo_tracker):
    comp = []
    viajes = []
    for c in camiones:
        if validator(v, c, tipo_viaje, tipo_tracker):
            comp.append(c)
            viajes.append(v)
    return comp, viajes

#we check the feasability of making two travels with the same tracker. If the end time of one travel is later
#than the start time of another travel that begins after the first one, these two travels are not compatible.
def no_compatible(Iv, i, Fv, olgura):

    eta = {}
    no_comp = []
    for inicio in Iv:
        for final in Iv:
            if i[inicio]   < Fv[final] + olgura and  i[inicio] >  i[final]: 
                eta[(inicio, final)] = 0
                no_comp.append(((inicio,final) ,(i[inicio], i[final]) ))

            elif i[inicio]   < Fv[final] + olgura and  i[inicio] ==  i[final] and inicio != final:
                eta[(inicio, final)] = 0
                no_comp.append(((inicio,final) ,(i[inicio], i[final]) ))

            else:
                eta[(inicio, final)] = 1

    return no_comp



def slicer(valor_limite, i):

    # Obtener elementos mayores a 3.2
    i = obtener_elementos_mayores(i, valor_limite)
    Iv = [clave for clave, valor in i.items()]
    return i, Iv

def setMaxTime(model, max_time):
    model.setRealParam('limits/time', max_time)

def objective_function(v, j, tipo_viaje, tipo_tracker):
    
    
    resultado = 0 
    
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR' and tipo_viaje[v]=='retiro_sai':
        return 1000
    
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR_ext' and tipo_viaje[v]=='retiro_sai':
        return -100

    elif tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO' and tipo_viaje[v] == 'retiro_sai':
        return 20
    
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO' and tipo_viaje[v] != 'retiro_sai':
        return 1000
    # 
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO' and tipo_viaje[v] == 'viaje_20':
        return 2500
    
    #elif tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO':
    #    return 130
    
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO' and tipo_viaje[v] == 'viaje_20':
        return -100
    
    #elif tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO'and tipo_viaje[v] != 'viaje_20':
    #    return 0
    
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO' and tipo_viaje[v] != 'retiro_sai':
        return 20
    
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO' and tipo_viaje[v] == 'retiro_sai':
        return 20
    
    elif (tipo_tracker[ast.literal_eval(j)[0]] == 'TERCERO'):
        return -2000
    
    else:
        return 0
    

def problem3( tipo_viaje, tipo_tracker,trios, no_comp, i, Iv, camioneros, timestop=False):
    
    # Create an empty model
    m1 = scip.Model("assignment2")
    if timestop == False:
        setMaxTime(m1, 1000)  # Establece el tiempo máximo a 60 segundos
    else: 
        pass
    
    # Add a variable for each possible assignment
    x = {}
    for trio in trios:
        x[trio] = m1.addVar(vtype="B", name="locate[" + str(trio) + "]")

    # Add the constraint
    for v, t in i.items():
        m1.addCons(scip.quicksum(x[(v, c, t)] for c in camioneros_comp(v, camioneros, tipo_viaje, tipo_tracker)[0]) == 1)
    
    # Add the constraints
    for v, t in no_comp:
        for c in camioneros:
            if validator(v[0], c, tipo_viaje, tipo_tracker) and validator(v[1], c, tipo_viaje, tipo_tracker):
                m1.addCons(x[v[0], c, t[0]] + x[v[1], c, t[1]] <= 1)
 
    # Set the objective function
    m1.setRealParam('limits/gap', 10)
    
    #m1.setObjective(1 , sense="maximize")
    
    
    m1.setObjective(
        scip.quicksum(
            objective_function(v, c, tipo_viaje, tipo_tracker) * x[v, c, t]
            for v, t in i.items()
            for c in camioneros
            if (v, c, t) in x  # Verifica que la clave exista en el diccionario x
        ),
        sense="maximize"
    )
    
    
    return m1, x

    # Call the printSolution() function with the model as an argument
    #printSolution(m)
    # Call the plotSolution() function with the model as an argument
    



def execute(m):

    # Resolver el modelo y medir el tiempo de resolución
    start_time = time.time()
    m.optimize()
    end_time = time.time()

    # Obtener el tiempo de resolución en segundos
    solve_time = end_time - start_time
    print("Demoro " + str(solve_time/60) + " minutos")



def printSolution(model, x, trios):

    if model.getStatus() == "optimal":
        print("\nCost: %g" % model.getObjVal())
        print("\nBuy:")
        for (v, c, t) in trios:
            if model.getVal(x[v, c, t]) > 0.0001:
                print("%s %g" % ((v, c, t), model.getVal(x[v, c, t])))
    else:
        print("No solution")
        

def timestamp_to_date(timestamp):
    try:
        date_obj = datetime.fromtimestamp(timestamp)
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print("Error converting timestamp to date:", e)
        return None


def plotSolution(model, x, y, trios,Fv, export=False):
    
    if True:#model.getStatus() == "optimal":
        
        #print("\nCost: %g" % model.getObjVal())
        #print("\nBuy:")
        travels = []
        trackers = []
        start_times = []
        end_times = []
        start_to_end_times = []
        
        for (v, c, t) in trios:
 
            if model.getVal(x[v, c, t]) > 0.0001:
                #print((v, c, t),model.getVal(x[v, c, t]))
                travels.append(v)
                trackers.append(c)
                start_times.append(datetime.fromtimestamp(t))
                end_times.append(timestamp_to_date(Fv[v]))
                start_to_end_times.append(datetime.fromtimestamp(Fv[v])-datetime.fromtimestamp(t))
                #print("%s %g" % ((v, c, t), model.getVal(x[v, c, t])))
     
    else:
        travels = []
        trackers = []
        start_times = []
        end_times = []
        start_to_end_times = []
        print("No solution")
    ruta_imagen = os.getcwd()

    fechas = []
    
    # Convertimos cada timestamp a fecha y lo agregamos a la lista de fechas
    for timestamp in start_times:
        fecha = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        fechas.append(fecha)
    
    dictionary = {}
    dictionary["id"] = travels
    dictionary["Trackers"] = trackers
    dictionary["start_time"] = start_times
    dictionary["fechas"] = fechas

    dictionary["end_time"] = end_times
    dictionary["start_to_end_time"] = start_to_end_times
    
    df = pd.DataFrame(dictionary)
    #print(df)
    fig, ax = plt.subplots(1, figsize=(16, 6))
    #print(df["Trackers"])
    ax.barh(df["Trackers"], df["start_to_end_time"], left=df['start_time'])
    plt.savefig(ruta_imagen + "\\static\\tmp\\planificacion.png")
    plt.show()
    
    df = pd.DataFrame(df)
    df.to_excel(ruta_imagen + "\\static\\tmp\\planificacion.xlsx", index=False)
    
    return df






def remove_last_element(lst):
    if lst:
        return lst.pop()
    else:
        print("The list is already empty.")
        return None

def secuencial_problem(tipo_viaje, tipo_tracker, df2, i, Fv, Iv, max_trackers, trackers1, olgura, start, end, mostrar_info):
    trackers = trackers1
    total_camioneros = trackers
    print("no compatibles")
    no_comp = no_compatible(Iv, i, Fv, olgura)
    for n_trackers in range(max_trackers, 0, -1):
        print("todos los posibles")
        trios = combinations(i, trackers, tipo_viaje, tipo_tracker)
        print("definicion del problema")
  
        m, x = problem3( tipo_viaje, tipo_tracker, trios, no_comp, i, Iv, trackers, False)
        y ={}
        print("ejecucion")
        execute(m)
        element = remove_last_element(trackers)
        
        if m.getStatus() == "optimal":
            try:
                df = plotSolution(m, x, y, trios, Fv, True)
            except:
                print("error al plotear la solución")
            print("Con " + str(len(trackers)) + " camioneros")
            directory = os.getcwd()
            delete(directory)
            print(df.columns, df2.columns)
            datos = merge(df2, df)
           
            datos = process_result(datos)
            datos.to_excel(directory + '\\static\\tmp\\planificacion2.xlsx')
            cargar_modelo(datos)
            
            m1, x1, y1 = m, x, y
            m.freeProb()
            break

        else:
            
            trackers.append(element)
     
            #trios = combinations(i, trackers)
            print("problema final")
  
            print("problema final ejecucion")
            
            break
    df = plotSolution(m, x, y, trios, Fv, True)
    directory = os.getcwd()
    delete(directory)
    datos = merge(df2, df)
    datos = process_result(datos)
    datos.to_excel(directory + '\\static\\tmp\\planificacion2.xlsx')
    print(datos.columns)
    cargar_modelo(datos)
    carta_gantt_trackers(datos, start, end, mostrar_info)
    print("final")
    
    try:  
        df = plotSolution(m1, x1, y1, trios, Fv, True)
    except:
        print("error al plotear la solución")
        
    m.freeProb()
    return df, len(trackers) , len(total_camioneros)
            





