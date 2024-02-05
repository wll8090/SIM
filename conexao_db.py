import mysql.connector
from mysql.connector import errorcode
from conf import DB_HOST, DB_PASSWORD, DB_PORT, DB_USER, database, tabela_candidato
from time import sleep


def connection_db():# Configurar a conexão com o banco de dados
    global cursor, connection
    connection = mysql.connector.connect(**{'host': DB_HOST, 'port': DB_PORT, 'user': DB_USER, 'password': DB_PASSWORD})
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            return cursor,connection
        else:
            return 0,0
    except:
        return 0,0 

def decora(funk):   #decorador para conexão do banvo BANCO_SIM    inicia e fecha a conexão
    def new(data):
        cursor , conn = connection_db()
        re=funk(cursor, conn ,data)
        conn.close()
        return re
    return new


@decora
def criar_db(cursor, conn ,data):
    if cursor == 0:
        return 'erro na conexão com DB'
    criar_banco=f'''
create database IF NOT EXISTS {database} character set utf8 collate utf8_general_ci;
'''
    create_table_login = f'''
CREATE TABLE IF NOT EXISTS {database}.{tabela_candidato} (
NU_ID INT AUTO_INCREMENT PRIMARY KEY,
NO_INSCRITO VARCHAR(100),
NO_MAE VARCHAR(100),
NU_CPF_INSCRITO VARCHAR(15) UNIQUE,
DS_EMAIL VARCHAR(50),
DT_NASCIMENTO  VARCHAR(20),
PWD VARCHAR(64) NOT NULL
);'''

    cursor.execute(criar_banco)
    print(f'banco "{database}" criado')
    cursor.execute(create_table_login)
    print(f'tabela "{tabela_candidato}" criado')
    conn.commit()
    print('processo realizado com sucesso!\nde nada !')


@decora
def drop_db(cursor, conn ,data):
    try:
        cursor.execute(f'drop database {database};')
        conn.commit()
        return 1
    except: 
        return 0

@decora
def inserir_no_banco(cursor, conn, dados):
    re=__consuta(cursor, dados[0].get('NU_CPF_INSCRITO'))
    if len(re) >= 1:
        return re
    colunas=["NO_INSCRITO", "NO_MAE", "NU_CPF_INSCRITO", "DS_EMAIL", "DT_NASCIMENTO", "PWD"]
    valores=[[i.get(j) for j in colunas] for i in dados]
    C_myqsl=f"""INSERT INTO {database}.{tabela_candidato} ({', '.join(colunas)}) VALUES ({('%s, '* len(colunas))[:-2]});"""
    cursor, conn = connection_db()
    cursor.executemany(C_myqsl, valores)
    conn.commit()
    print('salvo no banco')
    return 0

@decora
def delete_do_banco(cursor, conn, dados):
    cpf=dados.get("NU_CPF_INSCRITO")
    C_myqsl=f"""delete from  {database}.{tabela_candidato} where NU_CPF_INSCRITO like "{cpf}";"""
    cursor.execute(C_myqsl)
    conn.commit()
    return True

@decora   
def consultar_usuario(cursor, conn ,dados):
    cpf=dados['NU_CPF_INSCRITO']
    email=dados['DS_EMAIL']
    pwd=dados['PWD']
    if not cpf:
        return 0
    C_myqsl=f"""select * from {database}.{tabela_candidato} where 
                    NU_CPF_INSCRITO like "{cpf}" 
                &&  DS_EMAIL like "{email}"
                &&  PWD like "{pwd}"
                ;"""
    
    cursor.execute(C_myqsl)
    re=cursor.fetchall()
    return re

def __consuta(cursor, cpf):
    C_myqsl=f"""select * from {database}.{tabela_candidato} where 
                NU_CPF_INSCRITO like "{cpf}";"""

    cursor.execute(C_myqsl)
    re=cursor.fetchall()
    return re



if __name__ == '__main__':
    criar_db({})
