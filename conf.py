import sys


######------ contantes------------
##  host app

host_app= '192.168.40.102'
port= 5001
debug= True

## host LDAP
host_sli= '10.253.251.13'

## banco de dados mysql
DB_HOST='localhost'
DB_PORT='3306'
DB_USER='root'
DB_PASSWORD='root'
database = 'BANCO_SIM'
tabela_candidato="Candidato"


######---------variaveis--------------

sys.argv={
"inicio_chamda_1" : "" ,
"fim_chamada_1" : "" ,
"intervalo_entre_chamadas" : "" ,
"fim_das_matriculas" : "" ,
"file" : "candidatos.csv" ,
"path_csv" : "static" ,
"csv_vagas_materias" : "vaga_materias.csv" ,
"csv_lista_espera" : "lista_espera.csv" ,
"csv_chamada" : "chamada.csv" ,
"chamada" : '1'
}