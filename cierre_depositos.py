# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 17:20:24 2024

@author: Ignacio Carvajal
"""

import pandas as pd



def alcanza_a_volver(fk_servicio):
        
    CIERRE_DEPOSITOS = {
        'agunsa': {
            'santiago': {
                'semana': '19:00',
                'sabado': '15:00'
            },
            'san_antonio': {
                'semana': '22:00',
                'sabado': '18:00'
            },
            'valparaiso': {
                'semana': '20:00',
                'sabado': '15:00'
            }
        },
        'medlog': {
            'santiago': {
                'semana': '19:30',
                'sabado': '13:30'
            },
            'san_antonio': {
                'semana': '22:00',
                'sabado': '18:00'
            },
            'valparaiso': {
                'semana': '22:00',
                'sabado': '18:00'
            }
        },
        'sitrans': {
            'santiago': {
                'semana': '20:00',
                'sabado': '13:00'
            },
            'san_antonio': {
                'semana': '22:00',
                'sabado': '17:00'
            },
            'valparaiso': {
                'semana': '19:00',
                'sabado': '13:00'
            }
        },
        'contopsa': {
            'santiago': {
                'semana': '18:00',
                'sabado': '12:30'
            },
            'san_antonio': {
                'semana': '22:00',
                'sabado': '18:00'
            },
            'valparaiso': {
                'semana': '00:00',
                'sabado': '00:00'
            }
        },
        'dyc': {
            'santiago': {
                'semana': '20:00',
                'sabado': '15:00'
            },
            'san_antonio': {
                'semana': '22:00',
                'sabado': '18:00'
            },
            'valparaiso': {
                'semana': '20:00',
                'sabado': '15:00'
            }
        }
    }


    horario_cierre = CIERRE_DEPOSITOS['dyc']['santiago']['semana']
    print(horario_cierre)



    
    hora_pandas = pd.to_timedelta(hora_texto + ':00')
    
    if hora_pandas < hora_fin_servicio:
        return '10:00'
    else:
        return hora
    