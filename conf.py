import sys


######------ constantes------------
##  host app

host_app= '0.0.0.0'
port= 5001
debug= True

## host LDAP
host_sli= '10.253.251.13'

## banco de dados mysql
DB_HOST='container_mysql_sim'
DB_PORT='3306'
DB_USER='root'
DB_PASSWORD='root'
database = 'BANCO_SIM'
tabela_candidato="Candidato"


######---------variaveis--------------

sys.argv={
"docs_modelos":"./modelo_docs/",
"path_docs":"./docs/",
"inicio_chamda_1" : "" ,
"fim_chamada_1" : "" ,
"intervalo_entre_chamadas" : "" ,
"fim_das_matriculas" : "" ,
"file" : "candidatos.csv" ,
"path_csv" : "./static/" ,
"csv_vagas_materias" : "vaga_materias.json" ,
"csv_lista_espera" : "lista_espera.csv" ,
"csv_chamada" : "chamada.csv" ,
"chamada" : '1',
"csv_matriculados":"matriculados.csv"
}

## email
conf_email={
    "path_templates":"./templates/",
    "email_init":"email_boa_vindas.html",
    "indeferido":"email_indeferido.html",
    "deferido":"email_deferido.html",
    "roda_pe":"roda_pe.html"
}
sys.argv.update(conf_email)
