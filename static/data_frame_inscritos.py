# -*- coding: utf-8 -*-

import pandas as pd
import csv
from json import dumps, loads

from os import path
import sys


def gerar_data_frame(data, coluna):
    global all_candidatos
    data=pd.DataFrame(data, columns=coluna)
    # new columns
    all_candidatos=data.assign(**new_column)
    file=montpath(get_var('file'))
    all_candidatos.to_csv( file, sep='\t', index=0, encoding='utf-8')
    cursos=all_candidatos.NO_CURSO.unique().tolist()
    d={}
    for i in cursos:
        dados=all_candidatos.query(f'NO_CURSO == "{i}"')[['NO_MODALIDADE_CONCORRENCIA','QT_VAGAS']].drop_duplicates().values
        l=[]
        for j,n in list(dados):
            l.append([j, int(n)])
        d.update({i:dict(l)})    
    with open(montpath(get_var('csv_vagas_materias')),'w',encoding='utf-8') as mat:
        mat.write(dumps(d, indent=4, ensure_ascii=False))
        mat.close()

def seq_de_chamada():
    for i in range(1,20):
        sys.argv['chamada'][0]=str(i)
        yield i

    
def salvar_cahamda(data='F'):
    global seq
    
    ll=['NU_CPF_INSCRITO','MATRICULA']
    att={'index':0,'sep':'\t'}
    file=montpath(get_var('csv_chamada'))
    if type(data) == str:
        all_candidatos[ll].to_csv(file,**att)
    else:
        data[ll].to_csv(file,**att)
    next(seq)
    return True


def alter_inscrito(index, campo, valor):
    all_candidatos.loc[index, campo]=valor
    salvar_csv()
    return True


def data_filtro(query=False):
    if not query:
        return all_candidatos
    return all_candidatos.query( query )
     

def reload_candidatos(valor=0):
    global all_candidatos
    file=montpath(get_var('file'))
    if not path.exists(file):
        return False
    with open(file ,'r',encoding='utf8')   as arq:
        ll=list(csv.reader(arq, delimiter='\t'))
        all_candidatos=pd.DataFrame(ll[1:], columns=ll[0])
    return True

def salvar_csv():
    all_candidatos.to_csv(montpath(get_var('file')) ,sep='\t',index=0)

def get_data_frame():
    return all_candidatos



new_column={
    "EMAIL_ENVIADO":"N",
    "DADOS_CONFIRMADOS":'N',
    "DADOS_ALTENTICADOS":'N',
    "CORRETO":"S",
    "NU_PROCESSO":'1',
    "SEM_PDF":'NONE',
    "MATRICULA":'N',
    "FALTA_DE_DOCS":'N',
    "DATA_MATRICULA":'',
    "RASTRO_ANALISADOR":''
}

seq=seq_de_chamada()

montpath=lambda file: f'{get_var("path_csv")}{get_var("chamada")}_{file}'

get_var = lambda v: sys.argv[v]

reload_candidatos()