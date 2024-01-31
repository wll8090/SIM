from static import data_frame_inscritos
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
    filter=f'NU_CPF_INSCRITO == "{cpf}"'
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
        pwd='1010' #f'Acesso@{randint(10**5, 10**6-1)}'     #<< ------ senha fake para inscrito   
        hash_pwd=sha256(pwd.encode()).hexdigest()
        candidato['PWD']=hash_pwd
        candidato['pwd_sem_hash']=pwd
        
        if candidato['EMAIL_ENVIADO'] == 'R':
            print(f'ja enviado para {email}')
            return {'response':False, 'msg':f'email ja enviado para : {email}'}
        
        envioEmail=enviar_email(open(file,encoding='utf8').read())
        envioEmail.connect()
        envioEmail.format_texto(candidato)
        try:
            #########################################
            envioEmail.disparo(email,'Aprovação na graduação')   # envia email   << ----- envia email
            print(f'enviada para {email}')
            envioEmail.desconect()
            data={'EMAIL_ENVIADO':'R','NU_PROCESSO':'2','DS_EMAIL': email}
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



'''server {
        listen 5001 ssl;
        listen [::]:5001 ssl;

        ssl_certificate /etc/nginx/certs/sistemas.ufnt.edu.br.crt;
        ssl_certificate_key /etc/nginx/certs/sistemas.ufnt.edu.br.key;

        server_name sau_api;

        location /sau {

                proxy_pass https://10.253.251.36:5001/;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                }
        }'''


'''
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
'''