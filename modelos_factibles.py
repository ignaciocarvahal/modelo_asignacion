

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



            






def n_asociados_por_control_retiros(n_total_retiros, n_porteadores, n_asociado_cumplen, n_asociado_no_cumplen, n_asociado_desastre):


    # Create an empty model
    model = scip.Model("assignment2")

    
    # Crear una lista de índices de ejemplo
    variables = ["c_min_no_cumplen", "c_min_desastre"]
    
    # Crear un diccionario para las variables
    x = {}
    
    # Crear variables enteras
    for var in variables:
        x[var] = model.addVar(vtype="INTEGER", name="locate[" + str(var) + "]")
        



    #restriccion de maximos valores
    model.addCons( x["c_min_no_cumplen"]  <=  1 )
    model.addCons( x["c_min_no_cumplen"]  >=  0 )
    model.addCons( x["c_min_desastre"]  <=  2 )
    model.addCons( x["c_min_desastre"]  >=  0 )
    
    #los desastres portean mas que los que no cumplen
    model.addCons( x["c_min_desastre"]  >=  x["c_min_no_cumplen"]  )
    
    if  n_total_retiros - 5*n_porteadores > 0:
        #sea factible en el problema maestro    
        model.addCons( n_asociado_desastre*x["c_min_desastre"] + n_asociado_no_cumplen*x["c_min_no_cumplen"] <= n_total_retiros - 5*n_porteadores )
    else:
        model.addCons( n_asociado_desastre*x["c_min_desastre"] + n_asociado_no_cumplen*x["c_min_no_cumplen"] <= 0 )

        

    # Set the objective function
    model.setRealParam('limits/gap', 0.01)
    model.setParam('limits/solutions', 3)
    #m1.setObjective(1 , sense="maximize")
    
    
    model.setObjective( x["c_min_no_cumplen"] + x["c_min_desastre"],sense="maximize")
    
    # Resolver el modelo y medir el tiempo de resolución
    start_time = time.time()
    model.optimize()
    end_time = time.time()

    # Obtener el tiempo de resolución en segundos
    solve_time = end_time - start_time
    print("Demoro " + str(solve_time/60) + " minutos")
       
    # Obtener la mejor solución encontrada
    sol = model.getBestSol()
    
    # Obtener los valores de las variables x en la solución
    x_values = {}
    if sol is not None:
        for var in x:
            x_values[var] = model.getSolVal(sol, x[var])
            print(var, x_values[var])
    else:
        print("No feasible solution found within the time limit.")
    
    return x_values["c_min_desastre"], x_values["c_min_no_cumplen"]
#n_asociados_por_control_retiros(600, 10, 40, 5, 1)




def n_asociados_por_control_presentaciones(n_total_presentaciones, n_cumplen, n_no_cumplen, n_propios ):
    #df_control_retiros = query_control_porteos()

    
    # Create an empty model
    model = scip.Model("assignment2")

    
    # Crear una lista de índices de ejemplo
    variables = ["c_min_presentaciones_asociados_cumplen", "c_min_presentaciones_asociados_no_cumplen"]
    
    # Crear un diccionario para las variables
    x = {}
    
    # Crear variables enteras
    for var in variables:
        x[var] = model.addVar(vtype="INTEGER", name="locate[" + str(var) + "]")


    #restriccion de maximos valores
    model.addCons( x["c_min_presentaciones_asociados_cumplen"]  <=  1 )
    model.addCons( x["c_min_presentaciones_asociados_cumplen"]  >=  0 )

    model.addCons( x["c_min_presentaciones_asociados_no_cumplen"]  <=  1 )
    model.addCons( x["c_min_presentaciones_asociados_no_cumplen"]  >=  0 )
    
    model.addCons( x["c_min_presentaciones_asociados_cumplen"]  >=   x["c_min_presentaciones_asociados_no_cumplen"] )
    
    #sea factible en el problema maestro    
    model.addCons( n_total_presentaciones - n_propios >= x["c_min_presentaciones_asociados_cumplen"]*n_cumplen + x["c_min_presentaciones_asociados_no_cumplen"]*n_no_cumplen)
    

    # Set the objective fu
    nction
    model.setRealParam('limits/gap', 0.01)
    model.setParam('limits/solutions', 3)
    #m1.setObjective(1 , sense="maximize")
    
    
    model.setObjective( x["c_min_presentaciones_asociados_cumplen"] + x["c_min_presentaciones_asociados_no_cumplen"],sense="maximize")
    
    # Resolver el modelo y medir el tiempo de resolución
    start_time = time.time()
    model.optimize()
    end_time = time.time()

    # Obtener el tiempo de resolución en segundos
    solve_time = end_time - start_time
    print("Demoro " + str(solve_time/60) + " minutos")
       
    # Obtener la mejor solución encontrada
    sol = model.getBestSol()
    
    # Obtener los valores de las variables x en la solución
    x_values = {}
    if sol is not None:
        for var in x:
            x_values[var] = model.getSolVal(sol, x[var])
            print(var, x_values[var])
    else:
        print("No feasible solution found within the time limit.")
    
    return  x_values["c_min_presentaciones_asociados_cumplen"], x_values["c_min_presentaciones_asociados_no_cumplen"]


"""

def n_asociados_por_control_presentaciones(n_total_presentaciones, n_asociado, n_propios ):
    #df_control_retiros = query_control_porteos()

    
    # Create an empty model
    model = scip.Model("assignment2")

    
    # Crear una lista de índices de ejemplo
    variables = ["c_min_presentaciones_asociados"]
    
    # Crear un diccionario para las variables
    x = {}
    
    # Crear variables enteras
    for var in variables:
        x[var] = model.addVar(vtype="INTEGER", name="locate[" + str(var) + "]")


    #restriccion de maximos valores
    model.addCons( x["c_min_presentaciones_asociados"]  <=  1 )
    model.addCons( x["c_min_presentaciones_asociados"]  >=  0 )


    
    #sea factible en el problema maestro    
    model.addCons( n_total_presentaciones - n_propios >= x["c_min_presentaciones_asociados"]*n_asociado)
    

    # Set the objective function
    model.setRealParam('limits/gap', 0.01)
    model.setParam('limits/solutions', 3)
    #m1.setObjective(1 , sense="maximize")
    
    
    model.setObjective( x["c_min_presentaciones_asociados"],sense="maximize")
    
    # Resolver el modelo y medir el tiempo de resolución
    start_time = time.time()
    model.optimize()
    end_time = time.time()

    # Obtener el tiempo de resolución en segundos
    solve_time = end_time - start_time
    print("Demoro " + str(solve_time/60) + " minutos")
       
    # Obtener la mejor solución encontrada
    sol = model.getBestSol()
    
    # Obtener los valores de las variables x en la solución
    x_values = {}
    if sol is not None:
        for var in x:
            x_values[var] = model.getSolVal(sol, x[var])
            print(var, x_values[var])
    else:
        print("No feasible solution found within the time limit.")
    
    return x_values["c_min_presentaciones_asociados"]
#n_asociados_por_control_presentaciones(82,45,20)
"""



def contador_tipos_conductor(camioneros, tipo_tracker, limite_mayor, limite_menor):

    df_control_retiros = query_control_porteos()
    
    n_cumplen = 0
    n_no_cumplen = 0
    n_desastre = 0
    
    n_propios = 0
    n_asociados = 0
    n_porteadores = 0
    
    for j in camioneros:
        
        c_retiros = obtener_count(df_control_retiros, 1, eval(j)[4])
        c_presentaciones = obtener_count(df_control_retiros, 2, eval(j)[4])

        if c_presentaciones != 0:
            r = c_retiros/c_presentaciones
        else:
            r = c_retiros/1
        
        #print(eval(j)[0],eval(j)[1],eval(j)[2],eval(j)[3], r)

        
        if eval(j)[1] == 'ASOCIADO':
            if r>=limite_mayor:
                n_cumplen += 1
         
            elif r>=limite_menor and r<limite_mayor:
                n_no_cumplen += 1
        
            else:
                n_desastre += 1
  
        
        
      
        if eval(j)[1] == 'PROPIO':
            n_propios += 1
 
        if eval(j)[1] == 'ASOCIADO':
            n_asociados += 1

        if eval(j)[1] == 'PORTEADOR':
            n_porteadores += 1

    
    return n_cumplen, n_no_cumplen, n_desastre, n_propios, n_asociados, n_porteadores
    

def contador_tipos_viajes(viajes, tipo_viaje):
    n_retiros = 0
    n_presentaciones = 0 
    for v, t in viajes.items():
        if tipo_viaje[v] == 'retiro_sai':
            n_retiros += 1
        if tipo_viaje[v] == 'presentacion':
            n_presentaciones += 1
    
    return n_retiros, n_presentaciones
        
        
        
#n_retiros, n_presentaciones = contador_tipos_conductor(viajes, tipo_viaje)
#n_cumplen, n_no_cumplen, n_desastre, n_propios, n_asociados, n_porteadores = contador_tipos_conductor(camioneros, tipo_tracker)

