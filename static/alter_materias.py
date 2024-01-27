from json import loads, dumps
from os.path import exists 
import sys


def write_materias():
    global materias
    with open(montpath(get_var('csv_vagas_materias')) ,'w', encoding='utf-8') as mat:
        mat.write(dumps(materias, indent=4, ensure_ascii=False))
        mat.close()

def load_materias():
    global materias
    file=montpath(get_var('csv_vagas_materias'))
    with open(file,'r',encoding='utf-8') as mat:
        materias=loads(mat.read())
    
def alter_materias(curso, modalidade):
    new=materias.get(curso).get(modalidade)-1
    materias[curso][modalidade]=new
    write_materias()


def get_materias():
    return materias

get_var = lambda v: sys.argv[v]
montpath = lambda file: f'./{get_var("path_csv")}/{get_var("chamada")}_{file}'

if exists(montpath(get_var('csv_vagas_materias'))):
    load_materias()
