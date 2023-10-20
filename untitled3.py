# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 15:37:30 2023

@author: Ignacio Carvajal
"""

import numpy as np

def kmeans_with_constraint(X, K, max_iters=1000, constraint_value=10):
    best_centroids = None
    best_labels = None
    
    for _ in range(max_iters):
        # Inicializar los centroides de manera aleatoria
        centroids = X[np.random.choice(len(X), K, replace=False)]
        
        for _ in range(max_iters):
            # Calcular las distancias entre cada punto y los centroides
            distances = np.linalg.norm(X[:, np.newaxis, :2] - centroids[:, :2], axis=2)
            
            # Asignar cada punto al cluster del centroide más cercano
            labels = np.argmin(distances, axis=1)
            
            # Calcular la suma de la columna extra para cada cluster
            cluster_sums = np.array([X[labels == k][:, 2].sum() for k in range(K)])
            
            # Verificar si la suma supera la restricción y ajustar los centroides si es necesario
            if np.all(cluster_sums <= constraint_value):
                best_centroids = centroids
                best_labels = labels
                break
        if best_centroids is not None:
            break
        
    if best_centroids is None:
        print("No se encontró una clusterización que cumpla con la restricción.")
        return None, None
    
    return best_centroids, best_labels

# Ejemplo de uso
if __name__ == "__main__":
    # Generar datos de ejemplo con una columna extra
    np.random.seed(0)
    data = np.random.rand(200, 3)
  
    # Aplicar K-Means con restricción
    K = 3
    constraint_value = 50
    centroids, labels = kmeans_with_constraint(data, K, constraint_value=constraint_value)
    
    if centroids is not None:
        # Imprimir resultados
        for k in range(K):
            cluster_points = data[labels == k]
            cluster_sum = cluster_points[:, 2].sum()
            print(f"Cluster {k + 1}:")
            print("Centroide:", centroids[k, :2])
            print("Puntos en el cluster:", cluster_points)
            print(f"Suma de la columna extra en el cluster: {cluster_sum}")
            print("\n")
