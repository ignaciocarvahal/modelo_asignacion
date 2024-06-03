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
from query_control_retiros import *


##############################################################################

#print("Tenemos " + str(len(Iv)) + " servicios")
#This parameter models the tolerance of our model towards the lateness of each travel.
#As there is more slack, our model becomes more conservative.


######D####################################################################

def obtener_elementos_mayores(diccionario, valor_limite):
    elementos_mayores = {clave: valor for clave, valor in diccionario.items() if valor > valor_limite}
    return elementos_mayores

def validador_asignados(asignados, servicio, rut):
    if servicio in asignados.keys():
        if str(asignados[servicio]) == str(rut):
            return True
        else:
            return False
    
def validator(v, j, tipo_viaje, tipo_tracker):

    if tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO' and (tipo_viaje[v]=='viaje_20' or tipo_viaje[v] == 'Puerto cruzado' or tipo_viaje[v] == 'retiro_val'):
        return False
    
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'TERCERO' and (tipo_viaje[v]=='viaje_20' or tipo_viaje[v] == 'Puerto cruzado'):
        return False
    
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR'  and tipo_viaje[v]!='retiro_sai':
        return False
    
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR_ext' and tipo_viaje[v]!='retiro_sai':
        return False
     
        
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'TERCERO' and  (tipo_viaje[v] == 'retiro_val' or tipo_viaje[v] == 'Puerto cruzado'):
        return False
    
    else: 
        return True
    
    
    
def separar_viajes(tipo_viajes):
    presentacion_ids = []
    retiro_ids = []
    
    for id_viaje, tipo in tipo_viajes.items():
        if tipo == "retiro_val" or tipo == "retiro_sai":
            retiro_ids.append(id_viaje)
        else:
            presentacion_ids.append(id_viaje)
        
    return presentacion_ids, retiro_ids
    '''
    #si es propio puede hacer cualquier viaje 
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO':
        return True
 
    elif tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO' and tipo_viaje[v]=='viaje_20':
        return False

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
    '''
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

def mandatory_combinations(i, camioneros):
    # Aquí definimos todas las combinaciones de los viajes programados y los trackers que pueden hacerlo
    trios = []
    print("Se inician combinaciones")

    for v, t in i.items():
        for j in camioneros:

            trios.append((v, j, t))

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

def objective_function(v, j, tipo_viaje, tipo_tracker,  df_control_retiros):
    
  
    

    
    
    
    resultado = 0 
    r_propio = 0
    r_asociado = 0
    r_porteador = 0
    r_porteador_ext = 0
    r_externo = 0
    
    """
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO':
        
        r_propio = r_propio + 10000
        
    if tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO':
        r_asociado = r_asociado 
      
    if tipo_tracker[ast.literal_eval(j)[0]] == 'TERCERO':
        r_externo = r_externo - 5000
    
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR':
        r_porteador = r_porteador + 5000
        
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR_ext':
        r_porteador_ext = r_porteador_ext - 3000
    """
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR_ext':
        r_porteador_ext = r_porteador_ext - 3000
        
        
        
        
        
    
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR' and tipo_viaje[v]=='retiro_sai':
        r_porteador = r_porteador + 1000
    
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PORTEADOR_ext' and tipo_viaje[v]=='retiro_sai':
        r_porteador = r_porteador + 1000
        
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO' and tipo_viaje[v] == 'retiro_sai':
        r_propio = r_propio - 0
        
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO' and tipo_viaje[v] != 'retiro_sai':
        r_propio = r_propio + 10000
        
    if tipo_tracker[ast.literal_eval(j)[0]] == 'PROPIO' and tipo_viaje[v] == 'viaje_20':
        r_propio = r_propio + 2500
        
    if tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO' and tipo_viaje[v] == 'viaje_20':
        r_asociado = r_asociado - 2000
        
    
    #elif tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO'and tipo_viaje[v] != 'viaje_20':
    #    return 0
    
    if tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO' and tipo_viaje[v] != 'retiro_sai':
        r_asociado = r_asociado + 1000
        
        
    import numpy as np
    if tipo_tracker[ast.literal_eval(j)[0]] == 'ASOCIADO' and tipo_viaje[v] == 'retiro_sai':
        
        c_retiros = obtener_count(df_control_retiros, 1, eval(j)[0])
        c_presentaciones = obtener_count(df_control_retiros, 2, eval(j)[0])
        
        if c_presentaciones == 0:
            r = c_retiros / (c_presentaciones + 1)
        else:
            r = c_retiros / (c_presentaciones)        
            
        if r < 0.7:
            ganas_de_portear = (1.5-r)*10000 
        else:
            ganas_de_portear = 0
            
        r_asociado = r_asociado + ganas_de_portear
    
    if (tipo_tracker[ast.literal_eval(j)[0]] == 'TERCERO'):
        r_externo = r_externo - 7000
    

    
    
    return r_propio + r_asociado + r_porteador + r_externo + r_porteador_ext
    

def problem3(asignados, tipo_viaje, tipo_tracker,trios, no_comp, i, Iv, camioneros, timestop=False):
    
    presentaciones, retiros = separar_viajes(tipo_viaje)
    
    # Create an empty model
    m1 = scip.Model("assignment2")
    if timestop == False:
        setMaxTime(m1, 3000)  # Establece el tiempo máximo a 60 segundos
    else: 
        pass
    
    # Add a variable for each possible assignment
    x = {}
    for trio in trios:
        #if validador_asignados(asignados, trio[0], eval(trio[1])[-1]):
        #print(trio)
        x[trio] = m1.addVar(vtype="B", name="locate[" + str(trio) + "]")
    


    
    for trio in trios:
        #print((trio[0], eval(trio[1])[-1]), asignados)
        if validador_asignados(asignados, trio[0], eval(trio[1])[-1]):
        #if (trio[0], eval(trio[1])[-1]) in asignados.items():
        
            print(trio)
            #m1.addCons(x[trio]  == 1)
            
    #print(asignados.items())
        
    df_control_retiros = query_control_porteos()

    T = 0.8
    T2 = 0.5
    
    # Add the constraint

    for c in camioneros:
        

        if eval(c)[1] == 'PROPIO':
            print( eval(c)[1] )
            #todos los propios deben viajar 
            m1.addCons( scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in presentaciones and validator(v, c, tipo_viaje, tipo_tracker))  >= 1 )

                
        #control retiros vs presentaciones
        if eval(c)[1] == 'ASOCIADO':
            #
            c_retiros = obtener_count(df_control_retiros, 1, eval(c)[4])
            c_presentaciones = obtener_count(df_control_retiros, 2, eval(c)[4])
            #m1.addCons( c_retiros + scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in retiros and validator(v, c, tipo_viaje, tipo_tracker)) - T*c_presentaciones -  T*scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in presentaciones and validator(v, c, tipo_viaje, tipo_tracker))  <= 0 )
            #m1.addCons( c_retiros + scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in retiros and validator(v, c, tipo_viaje, tipo_tracker)) - T2*c_presentaciones -  T2*scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in presentaciones and validator(v, c, tipo_viaje, tipo_tracker))  >= 1 )
            
            #se prioriza la segunda vuelta del propio
            m1.addCons( scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in presentaciones and validator(v, c, tipo_viaje, tipo_tracker))  == 1 )

            if c_presentaciones != 0:
                r = c_retiros/c_presentaciones
            else:
                r = c_retiros/1
                
            #pregunta: 
            if r > T:
                
                print(eval(c)[0], r, 0.8)
                #si cumple no debe hacer más que un retiro al día 
                
                m1.addCons( scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in retiros and validator(v, c, tipo_viaje, tipo_tracker))  <=1 )
                
                
                
            elif r>T2 and r<= T:
               
                print(eval(c)[0], r, 0.5)
                #si no cumple, debe mantenerse o mejorar
                m1.addCons( scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in retiros and validator(v, c, tipo_viaje, tipo_tracker))  >= 1 )
                m1.addCons( scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in retiros and validator(v, c, tipo_viaje, tipo_tracker))  <= 2 )

                
            else:
                print(eval(c)[0], r, 0)
                #si esta en un nivel inaceptable debe retirar dos veces
                m1.addCons( scip.quicksum(x[(v, c, t)] for v, t in i.items() if v in retiros and validator(v, c, tipo_viaje, tipo_tracker))  == 2 )
                
                
          
    
    # Add the constraint
    for v, t in i.items():
        #todo viaje debe ser realizado por un conductor que pueda hacerlo
        m1.addCons(scip.quicksum(x[(v, c, t)] for c in camioneros_comp(v, camioneros, tipo_viaje, tipo_tracker)[0]) == 1)
    
    # Add the constraints
    for v, t in no_comp:
        for c in camioneros:
            #si ambos viajes pueden ser realizados por el mismo conductor, deben realizarse sin solape
            if validator(v[0], c, tipo_viaje, tipo_tracker) and validator(v[1], c, tipo_viaje, tipo_tracker):
                m1.addCons(x[v[0], c, t[0]] + x[v[1], c, t[1]] <= 1)
                

        
        
    # Set the objective function
    m1.setRealParam('limits/gap', 0.01)
    m1.setParam('limits/solutions', 3)
    #m1.setObjective(1 , sense="maximize")
    
    
    m1.setObjective(
        scip.quicksum(
            objective_function(v, c, tipo_viaje, tipo_tracker, df_control_retiros) * x[v, c, t]
            for v, t in i.items()
            for c in camioneros
            if (v, c, t) in x  # Verifica que la clave exista en el diccionario x
        ),
        sense="maximize"
    )
    
    # Resolver el modelo y medir el tiempo de resolución
    start_time = time.time()
    m1.optimize()
    end_time = time.time()

    # Obtener el tiempo de resolución en segundos
    solve_time = end_time - start_time
    print("Demoro " + str(solve_time/60) + " minutos")
       
    # Obtener la mejor solución encontrada
    sol = m1.getBestSol()
    
    # Obtener los valores de las variables x en la solución
    x_values = {}
    if sol is not None:
        for var in x:
            x_values[var] = m1.getSolVal(sol, x[var])
    else:
        print("No feasible solution found within the time limit.")
    
    return m1, x, x_values


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


def plotSolution(model, x, y, trios, Fv, df2, start, end, mostrar_info, export=False):

    if True:#model.getStatus() == "optimal":
    
        #print("\nCost: %g" % model.getObjVal())
        #print("\nBuy:")
        travels = []
        trackers = []
        start_times = []
        end_times = []
        start_to_end_times = []
        
        for (v, c, t) in trios:
         
            if y[v, c, t] > 0.0001:
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
    #ax.barh(df["Trackers"], df["start_to_end_time"], left=df['start_time'])
    #plt.savefig(ruta_imagen + "\\static\\tmp\\planificacion.png")
    #plt.show()
    
    directory = os.getcwd()
    delete(directory)
    datos = merge(df2, df)
    datos = process_result(datos)
    datos.to_excel(directory + '\\static\\tmp\\planificacion2.xlsx')

    carta_gantt_trackers(datos, start, end, mostrar_info)
    cargar_modelo(datos)
    
    
    df = pd.DataFrame(df)
    df.to_excel(ruta_imagen + "\\static\\tmp\\planificacion.xlsx", index=False)
    
    return df






def remove_last_element(lst):
    if lst:
        return lst.pop()
    else:
        print("The list is already empty.")
        return None

def secuencial_problem(asignados, tipo_viaje, tipo_tracker, df2, i, Fv, Iv, max_trackers, trackers1, olgura, start, end, mostrar_info):
    trackers = trackers1
    total_camioneros = trackers
    print("no compatibles")
    no_comp = no_compatible(Iv, i, Fv, olgura)
    for n_trackers in range(max_trackers, 0, -1):
        print("todos los posibles")
        trios = combinations(i, trackers, tipo_viaje, tipo_tracker)
        print("definicion del problema")
  
        m, x, x_values = problem3(asignados, tipo_viaje, tipo_tracker, trios, no_comp, i, Iv, trackers, False)
        y = x_values
        print("ejecucion")
        #execute(m)
        element = remove_last_element(trackers)
        
        if m.getStatus() == "optimal" or m.getStatus() == "feasible":
            try:
                df = plotSolution(m, x, y, trios, Fv, df2, start, end, mostrar_info,  True)
            except:
                print("error al plotear la solución")
            print("Con " + str(len(trackers)) + " camioneros")
            directory = os.getcwd()
            delete(directory)
            #print(df.columns, df2.columns)
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

    df = plotSolution(m, x, y, trios, Fv, df2, start, end, mostrar_info,  True)
    directory = os.getcwd()
    delete(directory)
    datos = merge(df2, df)
    datos = process_result(datos)
    datos.to_excel(directory + '\\static\\tmp\\planificacion2.xlsx')

    cargar_modelo(datos)
    carta_gantt_trackers(datos, start, end, mostrar_info)
    print("final")

    try:  
        df = plotSolution(m1, x1, y1, trios, Fv, df2, start, end, mostrar_info,  True)
    except:
        print("error al plotear la solución")
        
    m.freeProb()
    return df, len(trackers) , len(total_camioneros)
            





