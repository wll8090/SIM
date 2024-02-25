from json import loads, dumps
from os.path import exists 
import sys
from static_csv.data_frame_inscritos import nome_modalidade


file=f'{sys.argv.get("path_csv")}{sys.argv.get("csv_vagas_materias")}'

def write_materias():
    global materias
    with open(file ,'w', encoding='utf-8') as mat:
        mat.write(dumps(materias, indent=4, ensure_ascii=False))
        mat.close()

def load_materias():
    global materias
    with open(file,'r',encoding='utf-8') as mat:
        materias=loads(mat.read())
    
def alter_materias(curso, modalidade, q=-1):
    max=materias.get(curso).get(modalidade)[0]
    new=materias.get(curso).get(modalidade)[1]+q
    if new>max:
        return('maximo de vaga')
    elif new < 0:
        return('todas as vagas ocupadas')
    materias[curso][modalidade][1]=new
    write_materias()


def get_materias():
    return materias


if exists(file):
    load_materias()



def troca_vaga(curso, q, de, para):
    materias[curso][nome_modalidade[de]][0]-=q   #retira vaga
    materias[curso][nome_modalidade[para]][0]+=q     #acrescenta
    write_materias()
    return materias
