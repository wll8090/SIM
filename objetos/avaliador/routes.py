from flask import render_template, request, jsonify, abort, send_file
from objetos.avaliador.obj import usuario
from flask_socketio import SocketIO
from flask_cors import CORS
from os.path import exists

import sys

users_logado={}

def login(data,IO):
    if not 'user' in data:
        return {"response":False, 'msg':"erro no HTML"}
    login=data.get('user')
    ip=data.get('ip')
    pwd=data.get('pwd')
    user=usuario(login, pwd, ip, IO)
    v=user.login()
    if v=='000':
        return {"response":False, 'msg':"erro no vervidor LDAP"} 
    if v:
        users_logado[f'{login}-{ip}']=user
        file=f'{sys.argv.get("path_csv")}1_{sys.argv.get("csv_chamada")}'
        return {"response":True, 'msg':"usuario logado", 'token':user.token,
                'csv':exists(file),'ip':f'{ip}','csv_espera':exists('./socioeconomica.csv'),
                'chamada':f'{sys.argv.get("chamada")}'}
    return {"response":False, 'msg':"erro no login"}

def all_data(req):
    if request.data:
        data=request.json
    else: data={}
    ip=request.remote_addr
    #ip=request.headers.get('meu-ip-real-telvez-seja')
    if not ip:
        return abort(404)
    data['ip']=ip.split(',')[0]
    beare=request.headers.get('Authorization')
    data['Bearer']=None
    if beare:
        beare=beare.split()
        if len(beare) > 1:
            data['Bearer']=beare[-1]
    return data



def rotas(app ):
    CORS(app)
    IO=SocketIO(app)

    @app.route('/<key>/<acao>/<args>', methods=['post', 'get'])   #### rotas do sitema
    def rotas(key, acao, args):
        data=all_data(request)
        if request.method=='GET':
            key=f'{key}-{data["ip"]}'
            if key in users_logado:
                ip=request.remote_addr
                p=request.headers.get('meu-ip-real-telvez-seja').split(',')[0]
                if acao == 'file':                  ## autanticar candidato
                    token=request.args.get('file')
                    re=users_logado[key].return_file(token, ip)
                    if re:
                        nome=re
                        if nome in sys.argv:
                            re=sys.argv[nome]
                            sys.argv.pop(nome)
                        return send_file(re, download_name=nome)

            return abort(404)


        ################  para usuario ligin de usuario
        elif key == 'login' and acao == 'entrar':
            re=login(data, IO)
        
        ################# para usuarios de coordenação ja logado
        elif f'{key}-{data["ip"]}' in users_logado:
            key=f'{key}-{data["ip"]}'             
            if acao=='upcsv':                           ## para enviar csv
                data['file']=request.files['filecsv']   ## recebe o .csv
                re=users_logado[key].upload_csv(data)
                
            elif acao == 'up_csv_espera':                  ## upload de csv de lista de espera
                data['interesse']=request.files['interesse']
                data['socioeconomica']=request.files['socioeconomica']
                re=users_logado[key].up_csv_espera(data)

            elif acao == 'candidatos':                  ## para listar e filtrar os candidatos
                re=users_logado[key].listar_candidatos(data)
               
            elif acao == 'enviar_email':                ## para enviar email para os candidatos
                re=users_logado[key].enviar_email(data)
                
            elif acao == 'delete_csv':                  ## deletar o arquivo
                re=users_logado[key].delete_csv(data)
            
            elif acao == 'autenticar':                  ## autanticar candidato
                re=users_logado[key].autenticar(data)
            
            elif acao == 'get_dados_inscrito':                  ## retornar dados do inscriot pelo cpf
                re=users_logado[key].get_dados_inscrito(data)

            elif acao == 'alter_templates':                  ## retornar e modifica os templates de e-mail
                re=users_logado[key].alter_templates(data)

            elif acao == 'revog_matricula':                  ## retornar e modifica os templates de e-mail
                re=users_logado[key].revog_matricula(data)       

            elif acao == 'criar_csv_vagas':                ## para arquivo csv de vagas
                data['file']=request.files.get('file')
                re=users_logado[key].criar_csv_vagas(data) 

            elif acao == 'insert_in_db':
                re=users_logado[key].insert_in_db(data) 

            elif acao == 'aviso':
                av=open('aviso.txt', encoding='utf8').read()
                re={'response':True,'aviso':av}

            elif acao == 'rankear':
                re=users_logado[key].rankear(data) 

            elif acao == 'relatorio_matriculados':                  ## gerar o relatorio de matricula e deixa disponivel em /file?token=token
                re=users_logado[key].relatorio_matriculados(data)
                print(re)
            
            elif acao == 'sair':                        ## sair
                re=users_logado[key].sair(data)
                if re: 
                    users_logado.pop(key)
                else: re={'response': False}

            else:
                return abort(404)

        else: return abort(404)
        re['ip']=f'{data["ip"]}'
        return jsonify(re)

        
    @app.route('/doc/')   ## rota de documentação
    def doc():
        return render_template('doc.html')
        

    return IO

