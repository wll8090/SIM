# -*- coding: utf-8 -*-

import pandas as pd
import csv
from json import dumps, loads

from os import listdir 
from os.path import exists
import sys
import load_sys


def gerar_data_frame(file):
    global all_candidatos 
    seq_de_chamada()
    if not exists(file):
        return False
    data=pd.read_csv(f'./{file}',sep=';')
    all_candidatos=data.assign(**new_column)  # new columns
    for i in range(len(all_candidatos)):
        v=all_candidatos.loc[i,'NO_MODALIDADE_CONCORRENCIA']
        all_candidatos.loc[i,'SIGLA_MODALIDADE_CONCORRENCIA']=sigla_modalidade.get(v)
    file=montpath(get_var('file'))
    all_candidatos.to_csv( file, sep=';', index=0, encoding='utf-8')

    file=f'{sys.argv.get("path_csv")}{sys.argv.get("chamada")}_{sys.argv.get("csv_chamada")}'
    all_candidatos[['NU_CPF_INSCRITO','NO_CURSO']].to_csv(file, encoding='utf-8',sep=';')
    cursos=all_candidatos.NO_CURSO.unique().tolist()
    d={}
    for i in cursos:
        dados=all_candidatos.query(f'NO_CURSO == "{i}"')[['NO_MODALIDADE_CONCORRENCIA','QT_VAGAS_CONCORRENCIA']].drop_duplicates().values
        l=[]
        for j,n in list(dados):
            l.append([j, [int(n),int(n)]])
        d.update({i:dict(l)})
    file=f'{sys.argv.get("path_csv")}{sys.argv.get("csv_vagas_materias")}'
    if not exists(file):
        with open(file,'w',encoding='utf-8') as mat:
            mat.write(dumps(d, indent=4, ensure_ascii=False))
            mat.close()
    

def seq_de_chamada():
    l=listdir(f'{sys.argv.get("path_csv")}')
    l=[i.split('_')[0] for i in l if i.endswith(sys.argv.get('file'))]
    if len(l)>0:
        v=max([int(i) for i in l])
        load_sys.set_sys('chamada',f'{v+1}')
    else:
        load_sys.set_sys('chamada','1')
    

def salvar_cahamda(data='F'):
    ll=['NU_CPF_INSCRITO','MATRICULA']
    att={'index':0,'sep':';'}
    file=f'{sys.argv.get("path_csv")}{sys.argv.get("csv_chamada")}'
    if type(data) == str:
        all_candidatos[ll].to_csv(file,**att)
    else:
        data[ll].to_csv(file,**att)
    return True


def alter_inscrito(index, campo, valor):
    all_candidatos.loc[index, campo]=valor
    salvar_csv()
    return True


def data_filtro(query=False):
    if type(all_candidatos) == bool:
        return False
    if not query:
        return all_candidatos
    return all_candidatos.query( query )
     

def reload_candidatos(valor=0):
    global all_candidatos
    file=montpath(get_var('file'))
    if not exists(file):
        return False
    with open(file ,'r',encoding='utf8')   as arq:
        ll=list(csv.reader(arq, delimiter=';'))
        all_candidatos=pd.DataFrame(ll[1:], columns=ll[0])
    return True

def salvar_csv():
    all_candidatos.to_csv(montpath(get_var('file')) ,sep=';',index=0)

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
    "RASTRO_ANALISADOR":'',
    "SIGLA_MODALIDADE_CONCORRENCIA":''
}

montpath=lambda file: f'{get_var("path_csv")}{get_var("chamada")}_{file}'

get_var = lambda v: sys.argv[v]

all_candidatos=False

reload_candidatos()


sigla_modalidade={
    'Ampla concorrência':'AC',
    'Candidatos autodeclarados pretos, pardos ou indígenas, com renda familiar bruta per capita igual ou inferior a 1 salário mínimo e que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':'LB_PPI',
    'Candidatos autodeclarados pretos, pardos ou indígenas, independentemente da renda, que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':'LI_PPI',
    'Candidatos autodeclarados quilombolas, com renda familiar bruta per capita igual ou inferior a 1 salário mínimo e que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':'LB_Q',
    'Candidatos com deficiência, independentemente da renda, que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':'LI_PCD',
    'Candidatos com deficiência, que tenham renda familiar bruta per capita igual ou inferior a 1 salário mínimo e que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012)':'LB_PCD',
    'Candidatos com renda familiar bruta per capita igual ou inferior a 1 salário mínimo que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':'LB_EP',
    'Candidatos que, independentemente da renda, tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':'LI_EP',
    'Indígenas':'A1',
    'Quilombola':'A2'
}


nome_modalidade={valor : chave for chave,valor in sigla_modalidade.items()}
