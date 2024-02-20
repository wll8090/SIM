from static_csv import data_frame_inscritos
from unidecode import unidecode
from send_email import enviar_email
import sys
from hashlib import sha256
import conexao_db
from random import randint

def acesso(data):
    cpf=data.get('cpf')
    mae=data.get('mae')
    nome=data.get('nome')
    email=data.get('email')
    cpf=cpf.replace('.','').replace('-','')
    filter=f'NU_CPF_INSCRITO == "{int(cpf)}"'
    return{'response':False, 'msg':'Seu periodo de chamada terminou'}
    dd=data_frame_inscritos.data_filtro(filter)
    index=dd.index.values.tolist()[0]
    if dd.empty:
        return {'response':False, 'msg': 'usuario não encontrado'}
    ll=[unidecode(mae.upper()),unidecode(nome.upper())]
    lll=dd[['NO_MAE','NO_INSCRITO']].values.tolist()[0]
    lll=[i.upper() for i in lll]
    if ll == lll:
        file=f'{sys.argv.get("path_templates")}{sys.argv.get("email_init")}'
        candidato = dd.to_dict('records')[0]
        pwd=f'Acesso@{randint(10**5, 10**6-1)}'     #<< ------ senha fake para inscrito   
        hash_pwd=sha256(pwd.encode()).hexdigest()
        candidato['PWD']=hash_pwd
        candidato['pwd_sem_hash']=pwd
        candidato['DS_EMAIL']=email
        if candidato['EMAIL_ENVIADO'] == 'N':
            return {'response':False, 'msg':f'seu email ainda não foi enviado, aguarde!'}
        
        envioEmail=enviar_email(open(file,encoding='utf8').read())
        envioEmail.connect()
        envioEmail.format_texto(candidato)
        try:
            #########################################
            envioEmail.disparo(email,'Aprovação na graduação')   # envia email   << ----- envia email
            print(f'enviada para {email}')
            envioEmail.desconect()
            data={'EMAIL_ENVIADO':'S','NU_PROCESSO':'2','DS_EMAIL': email}
            for campo in data:
                data_frame_inscritos.alter_inscrito(index , campo, data[campo])
            conexao_db.delete_do_banco(candidato)
            conexao_db.inserir_no_banco([candidato])
            ##########################################
                
        except :
            print(f'erro para {email}')
            conexao_db.delete_do_banco(candidato)
            data_frame_inscritos.alter_inscrito(index ,'EMAIL_ENVIADO','E')
            return {'response':False, 'msg':f'erro'}
        return {'response':True, 'msg':f'email enviado para : {email}'}
    

    return {'response':False, 'msg': 'usuario não encontrado'}

