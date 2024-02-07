from json import loads , dumps
import sys
from os.path import exists

file='./load_sys.json'

def load_sys():
    if exists(file):
        with open(file,'r')as arq:
            dd=loads(arq.read())
            sys.argv.update(dd)
            arq.close()
    else:
        salve_sys()
        print('file criado')

def salve_sys():
    with open(file,'w') as arq:
        arq.write(dumps(sys.argv,indent=4))
        arq.close()

def set_sys(campo,valor):
    sys.argv[campo]=valor
    salve_sys()

load_sys()
