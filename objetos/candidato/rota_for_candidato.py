from flask import request, jsonify, abort, send_file
from json import loads
from objetos.candidato.obj_candidato import cantidato
from conexao_db import  consultar_usuario
from hashlib import sha256
from os.path import exists
from .get_acesso import acesso
import sys

candidato_logado={}


def login(data):
    global candidato_logado
    dados={"NU_CPF_INSCRITO": str(int(data.get('cpf'))), 
           "DS_EMAIL":data.get('email'),
           "PWD": sha256(data.get('pwd').encode()).hexdigest() }
    re=consultar_usuario(dados)     ## consulta no banco
    if re:
        user=cantidato( dados['NU_CPF_INSCRITO'], data.get('pwd'), data.get('email'), data.get('ip'))
        if user.login():
            candidato_logado[user.ip]=user
            re={'response': True ,'ip':user.ip}
            re.update(user.my_dados())
            return re
    return {'response':False,'msg':'usuario não encontrado'}


def all_data(req):
    data=loads(req.data) if req.data else {}
    ip=request.remote_addr
    ip=request.headers.get('meu-ip-real-telvez-seja').split(',')[0]
    data['ip']=ip
    Berare=req.headers.get('Authorization')
    if Berare:
        data['Bearer']=Berare.split()[-1]
    return data


#####  endoint  --------------------------
def creat_rotas(app):  ## rotas para os candidatos

    @app.route('/matricula/<candidato>/<acao>', methods=['POST','GET'])
    def init_req(candidato, acao):
        data=all_data(request)
        ip=data['ip']

        if request.method=='GET':
            if acao == 'modelo_docs':
                data['file']=request.args['file']
                data['Bearer']=candidato_logado[ip].token
                re=candidato_logado[ip].modelo_doc(data)
                if type(re) == str:
                    return send_file(re)

            return abort(404)


        if candidato == 'login':   
            re=login(data)
        
        elif candidato == 'get_acesso':   
            re=acesso(data)
        
        elif ip in candidato_logado:
            if acao == 'send_dados':
                re=candidato_logado[ip].send_dados(data)
            
            elif acao == 'send_file':
                data['files']=request.files
                re=candidato_logado[ip].send_file(data)
            
            elif acao == 'all_dados':
                re=candidato_logado[ip].all_dados(data)
            
            elif acao == 'etapa':
                re=candidato_logado[ip].etapa(data)
            
            elif acao == 'meu_pdf':
                re=candidato_logado[ip].meu_pdf(data)
            
            elif acao == 'modelo_docs':
                re=candidato_logado[ip].modelo_doc(data)
            
            elif acao == 'sair':
                re=candidato_logado[ip].sair(data)
                if re:
                    candidato_logado.pop(ip)
                    print(candidato_logado)
                else:
                    re= {'response':False}
            else:
                return abort(404)

        else: re= {'response':False,'msg':'precisa fazer login'}
        re['ip']=ip
        re['aviso']=open('aviso.txt', encoding='utf8').read()
        return jsonify(re)
    

    @app.route('/get_var_user')
    def get_var():
        print(candidato_logado)
        re=candidato_logado['192.168.40.102'].get_var_user()
        return f'{re}'
