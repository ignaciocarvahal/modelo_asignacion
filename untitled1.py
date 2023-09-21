
#import all the libraries
import pyscipopt as scip
import time
import pandas as pd 
import os
from datetime import datetime
import matplotlib.pyplot as plt
from utils2 import merge, delete
from gantt import *



##############################################################################

#print("Tenemos " + str(len(Iv)) + " servicios")
#This parameter models the tolerance of our model towards the lateness of each travel.
#As there is more slack, our model becomes more conservative.


######D####################################################################

def obtener_elementos_mayores(diccionario, valor_limite):
    elementos_mayores = {clave: valor for clave, valor in diccionario.items() if valor > valor_limite}
    return elementos_mayores

def combinations(i, camioneros):
    #here we define all the convinations of the schudeled travels and the trackers that can do it
    trios = []
    #for v in Iv:
    #    for t in i.values():
    for v, t in i.items():
        for j in camioneros:
            trios.append((v, j, t))
    trios = set(trios)
    #print("the number of variables is: " + str(len(trios)))
    #print(trios)
    return trios


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

def problem(trios, no_comp, i, Iv, camioneros, timestop=False):
    # Create an empty model
    m1 = scip.Model("assignment2")
    if timestop == False:
        setMaxTime(m1,240)  # Establece el tiempo máximo a 60 segundos
    else: 
        pass
    # Add a variable for each possible assignment
    x = {}
    for trio in trios:
        x[trio] = m1.addVar(vtype="B", name="locate[" + str(trio) + "]")


    # Crear variables auxiliares y_c
    y = {}
    for c in camioneros:
        y[c] = m1.addVar(vtype="B", name=f"y_{c}")
        
    
    # Add the constraint
    for v, t in i.items():
        m1.addCons(scip.quicksum(x[(v, c, t)] for c in camioneros) >= 1)

    # Add the constraints
    for v, t in no_comp:
        for c in camioneros:
            m1.addCons(x[v[0], c, t[0]] + x[v[1], c, t[1]] <= 1)
            
    # Restricción: Definición de las variables auxiliares y_c si el camionero c tiene un servicio entonces tiene que estar disponible 
    #for c in camioneros:
    #   m1.addCons(y[c] >= sum(x[v, c, t] for v, t in i.items())/len(Iv))
    

    # Set the objective function
    m1.setObjective(scip.quicksum(x[v, c, t] for c in camioneros for v, t in i.items()), sense="minimize")

    #m1.setObjective(1 , sense="maximize")


    return m1, x, y

def problem3(trios, no_comp, i, Iv, camioneros, timestop=False):
    # Create an empty model
    m1 = scip.Model("assignment2")
    if timestop == False:
        setMaxTime(m1, 600)  # Establece el tiempo máximo a 60 segundos
    else: 
        pass
    # Add a variable for each possible assignment
    x = {}
    for trio in trios:
        x[trio] = m1.addVar(vtype="B", name="locate[" + str(trio) + "]")


    # Crear variables auxiliares y_c
    y = {}
    for c in camioneros:
        y[c] = m1.addVar(vtype="B", name=f"y_{c}")
        
    
    # Add the constraint
    for v, t in i.items():
        m1.addCons(scip.quicksum(x[(v, c, t)] for c in camioneros) == 1)

    # Add the constraints
    for v, t in no_comp:
        for c in camioneros:
            m1.addCons(x[v[0], c, t[0]] + x[v[1], c, t[1]] <= 1)
            
    # Restricción: Definición de las variables auxiliares y_c si el camionero c tiene un servicio entonces tiene que estar disponible 
    #for c in camioneros:
    #   m1.addCons(y[c] >= sum(x[v, c, t] for v, t in i.items())/len(Iv))
    

    # Set the objective function
    #m1.setObjective(scip.quicksum(x[v, c, t] for c in camioneros for v, t in i.items()), sense="minimize")

    m1.setObjective(1 , sense="maximize")


    return m1, x, y

    # Call the printSolution() function with the model as an argument
    #printSolution(m)
    # Call the plotSolution() function with the model as an argument
    
    
def problem2(trios, no_comp, i, Iv, camioneros):
    # Create an empty model
    m1 = scip.Model("assignment1")
    
    # Add a variable for each possible assignment
    x = {}
    for trio in trios:
        x[trio] = m1.addVar(vtype="B", name="locate[" + str(trio) + "]")
    print("hola4")

    # Crear variables auxiliares y_c
    y = {}
    for c in camioneros:
        y[c] = m1.addVar(vtype="B", name=f"y_{c}")
    print("hola5")
    # Add the constraint
    for v, t in i.items():
        m1.addCons(scip.quicksum(x[(v, c, t)] for c in camioneros) == 1)
    print("hola6")
    # Add the constraints
    for v, t in no_comp:
        for c in camioneros:
            m1.addCons(x[v[0], c, t[0]] + x[v[1], c, t[1]] <= 1)
    print("hola7")
    # Restricción: Definición de las variables auxiliares y_c si el camionero c tiene un servicio entonces tiene que estar disponible 
    #for c in camioneros:
    #    for v, t in i.items():
    #        m1.addCons(y[c] >= x[v, c, t] )
    
    # Restricción: Definición de las variables auxiliares y_c si el camionero c tiene un servicio entonces tiene que estar disponible 
    for c in camioneros:
        m1.addCons(y[c] * len(Iv) >= sum(x[v, c, t] for v, t in i.items()))
    print("hola8")
    # Set the objective function
    #m1.setObjective(scip.quicksum(x[v, c, t] for c in camioneros for v, t in i.items()), sense="maximize")
    
    # Set the objective function
    m1.setObjective(scip.quicksum(y[c] for c in camioneros), sense="minimize")
    print("hola9")
    #m1.setObjective(1, sense="minimize")
    return m1, x, y

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
    
    if model.getStatus() == "optimal":
        print("\nCost: %g" % model.getObjVal())
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
    
    ax.barh(df["Trackers"], df["start_to_end_time"], left=df['start_time'])
    plt.savefig(ruta_imagen + "\\static\\tmp\\planificacion.png")
    plt.show()
    
    df = pd.DataFrame(df)
    
    df.to_excel(ruta_imagen + "\\static\\tmp\\planificacion.xlsx", index=False)
    
    return df




def hotstart(m1, m2):
    print("fase 1")
    solution = m1.getBestSol()
    variable = m1.getVars()
    n_vars = m1.getNVars()
    newsol = m2.createSol()
    print("fase 2")
    if m1.getStatus() == "OPTIMAL" or m1.getStatus() =="FEASIBLE" :
        print("warmstart")
        for n in range(n_vars):
            print(n)
            newsol[variable[n]] = m1.getSolVal(solution, variable[n])

        m2.trySol(newsol)
    #else: 
    #    m1.optimize()


def remove_last_element(lst):
    if lst:
        return lst.pop()
    else:
        print("The list is already empty.")
        return None

def secuencial_problem(df2, i, Fv, Iv, max_trackers, trackers1, olgura, start, end, mostrar_info):
    trackers = trackers1
    total_camioneros = trackers
    print("no compatibles")
    no_comp = no_compatible(Iv, i, Fv, olgura)
    for n_trackers in range(max_trackers, 0, -1):
        print("todos los posibles")
        trios = combinations(i, trackers)
        print("definicion del problema")
        
        m, x, y = problem3(trios, no_comp, i, Iv, trackers)
        
        print("ejecucion")
        execute(m)
        element = remove_last_element(trackers)
        
        if m.getStatus() == "optimal":
            df = plotSolution(m, x, y, trios, Fv, True)
            
            print("Con " + str(len(trackers)) + " camioneros")
            directory = os.getcwd()
            delete(directory)
            datos = merge(df2, df)
            
            datos.to_excel(directory + '\\static\\tmp\\planificacion2.xlsx')
            
            m1, x1, y1 = m, x, y
            m.freeProb()
            pass

        else:
    
            trackers.append(element)
     
            trios = combinations(i, trackers)
            print("problema final")
  
            print("problema final ejecucion")
       
            break
    delete(directory)
    datos = merge(df2, df)
    datos.to_excel(directory + '\\static\\tmp\\planificacion2.xlsx')
    carta_gantt_trackers(datos, start, end, mostrar_info)
    print("final")
    df = plotSolution(m1, x1, y1, trios, Fv, True)
   
    m1.freeProb()
    return df, len(trackers) , len(total_camioneros)
            



