# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 17:20:24 2024

@author: Ignacio Carvajal
"""

import pandas as pd


def cierre_depositos():
        
    CIERRE_DEPOSITOS = {
        'AGUNSA': {
            'SAI': {
                'semana': '19:00',
                'sabado': '15:00'
            },
            'SAI': {
                'semana': '22:00',
                'sabado': '18:00'
            },
            'VAL': {
                'semana': '20:00',
                'sabado': '15:00'
            }
        },
        'MEDLOG': {
            'SCL': {
                'semana': '19:30',
                'sabado': '13:30'
            },
            'SAI': {
                'semana': '22:00',
                'sabado': '18:00'
            },
            'VAL': {
                'semana': '22:00',
                'sabado': '18:00'
            }
        },
        'SITRANS': {
            'SCL': {
                'semana': '20:00',
                'sabado': '13:00'
            },
            'SAI': {
                'semana': '22:00',
                'sabado': '17:00'
            },
            'VAL': {
                'semana': '19:00',
                'sabado': '13:00'
            }
        },
        'CONTOPSA': {
            'SCL': {
                'semana': '18:00',
                'sabado': '12:30'
            },
            'SAI': {
                'semana': '22:00',
                'sabado': '18:00'
            },
            'VAL': {
                'semana': '00:00',
                'sabado': '00:00'
            }
        },
        'DYC': {
            'SCL': {
                'semana': '20:00',
                'sabado': '15:00'
            },
            'SAI': {
                'semana': '22:00',
                'sabado': '18:00'
            },
            'VAL': {
                'semana': '20:00',
                'sabado': '15:00'
            }
        }
    }
    return CIERRE_DEPOSITOS


#str ---> arreglo
def identificador_depositos(nombre_deposito):
    lista_de_palabras = nombre_deposito.split()
    
    
    json_cierre_depositos = cierre_depositos()
    empresas = json_cierre_depositos.keys()
    ciudades = json_cierre_depositos['CONTOPSA'].keys()
    
    for palabra in lista_de_palabras:
        if palabra in empresas:
            empresa_a_revisar = palabra
        if palabra in ciudades:
            ciudad_a_revisar = palabra
        
        if palabra not in empresas and palabra not in ciudades:
            return {}

    
    return json_cierre_depositos[empresa_a_revisar][ciudad_a_revisar]

print(identificador_depositos('MEDLOG VAL'))