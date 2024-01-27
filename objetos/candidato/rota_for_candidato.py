from flask import request, jsonify, abort, send_file
from json import loads
from objetos.candidato.obj_candidato import cantidato
from conexao_db import  consultar_usuario
from hashlib import sha256
from os.path import exists

candidato_logado={}


def login(data):
    global candidato_logado
    dados={"NU_CPF_INSCRITO": str(int(data.get('cpf'))), 
           "DS_EMAIL":data.get('email'),
           "PWD": sha256(data.get('pwd').encode()).hexdigest() }
    re=consultar_usuario(dados)     ## consulta no banco
    if re:
        user=cantidato( data.get('cpf'), data.get('pwd'), data.get('email'), data.get('ip'))
        if user.login():
            candidato_logado[user.ip]=user
            re={'response': True ,'ip':user.ip}
            re.update(user.my_dados())
            return re
    return {'response':False,'msg':'usuario não encontrado'}


def all_data(req):
    data=loads(req.data) if req.data else {}
    data['ip']=req.remote_addr
    Berare=req.headers.get('Authorization')
    if Berare:
        data['Bearer']=Berare.split()[-1]
    return data


#####  endoint  --------------------------
def creat_rotas(app):  ## rotas para os candidatos
    if exists('./static/1_candidatos.csv'):
        login({"pwd":"1010",
        "email":"jvapgold@gmail.com", 
        "cpf":"5765767354",'ip':'192.168.40.102'})
    @app.route('/matricula/<candidato>/<acao>', methods=['POST'])
    def init_req(candidato, acao):
        data=all_data(request)
        ip=request.remote_addr


        if candidato == 'login':   
            re=login(data)
        
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
                if type(re) == str:
                    print('kkkkkkkkkkk')
                    return send_file(re)
            
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
        return jsonify(re)
    

    @app.route('/get_var_user')
    def get_var():
        print(candidato_logado)
        re=candidato_logado['192.168.40.102'].get_var_user()
        return f'{re}'