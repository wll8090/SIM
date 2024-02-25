from conexao_db import inserir_no_banco, delete_do_banco, connection_db
from static_csv.data_frame_inscritos import *
from datetime import datetime
from hashlib import sha256
from login_ldap import login_user
from random import randint
from send_email import enviar_email
from threading import Thread, active_count
from time import sleep
from static_csv.alter_materias import *
from . import rankear
from shutil import copyfile

#from conf import *
#from os.path import exists
#from os import path
#from os import listdir
#from json import loads, dumps


#import csv
#import pandas as pd
#import sys
import io
import load_sys



csv.field_size_limit(10_000_000)
reload_candidatos()


class usuario:
    def validar_token(funk):                     ####### decorator para validar o tokem de usuario
        def new_funk(self, data):
            if data.get('Bearer') == self.token and data.get('ip') == self.ip or True:
                self.data=self.date_now(h=True)
                return funk(self, data)
            else:
                return {'response':'false', 'msg':'token invalido'}
        return new_funk


    def __init__(self, nome, pwd , ip, IO):
        self.nome=nome
        self.ip=ip
        self.filtro={}
        self.filtro_autenticar={}
        self.pwd=pwd
        self.IO=IO
        self.gerar_sokk()
        self.dados_inscrito={}
        self.token_file={}
        self.acao = ''
        self.data=self.date_now()

    
    def __alter__(self, index, data):
        for campo in data:
            alter_inscrito(index , campo, data[campo])
        alter_inscrito(index,'RASTRO_ANALISADOR',self.nome)

    
    def get_info(self, cpf , lista=False):
        dados=data_filtro(f'NU_CPF_INSCRITO == "{cpf}"')
        if dados.empty:
            return False
        index=dados.index.to_list()[0]
        dados=dados.to_dict('records')[0]
        if lista:
            dados={i:dados[i] for i in lista}
        dados['INDEX']=index
        return dados

    
    def dados(self) :
        dd={"user":self.nome, 
            "token": self.token }
        return dd
    
    def enviar_sok(self, dado, space=1):
        space=f'/{self.nome}' if space else False
        self.IO.emit('on_cliente',dado , namespace=space)
        return 1
    
    def gerar_sokk(self):
        @self.IO.on('on_server', namespace=f'/{self.nome}')
        def on(dado):
            self.enviar_sok('acho que não tem nada por aqui!')
            pass
    
    def date_now(self, h=False):
        txt='%d-%m-%Y'
        if h:
            txt +=' %H:%M:%S'
        return datetime.now().strftime(txt)
    
    def login(self):
        self.nonce=randint(10**15,10**30)
        v=login_user(self.nome, self.pwd)
        if v=='000':
            return '000'
        if v:
            dia=self.date_now()
            #self.token='1010'   # <<<------ tokem fake  # del
            self.token=sha256(f'{dia}{self.ip}{self.nome},{self.nonce}'.encode()).hexdigest()
            return 1
        return 0

    
    @validar_token
    def listar_candidatos(self, data, oo=False):
        campo=data.get('campo')
        filtro=data.get('filtro')
        acao=data.get('acao')
        if not reload_candidatos():  # restartarta o arquivo de usuarios
            return {"response": False, "msg": "lista ainda não carregada"}

        if filtro :
            if acao == 'add' and campo:
                self.filtro.update({campo:filtro})
            elif acao == 'del':
                if campo in self.filtro:
                    self.filtro.pop(campo)
        elif acao == 'cls':
            self.filtro={}

        query=' and '.join([f'{a} == "{aa}"' for a,aa in zip(self.filtro.keys(), self.filtro.values())])
        reload_candidatos()
        alunos_filtrados=data_filtro(query)
        self.alunos_filtrados=alunos_filtrados['NU_CPF_INSCRITO'].to_list()

        if oo: return {'response':True}
        valores={i: alunos_filtrados[i].unique().tolist() for i in lista_de_filtro}
        alunos=self.__to_dict(alunos_filtrados, lista_simples)
        q=len(alunos)
        return {'response':True, 'filtro':self.filtro, 'campos_valores':valores, 'alunos': alunos, 'quantidade':q}

    
    @validar_token
    def get_dados_inscrito(self, data):
        reload_candidatos()
        cpf=data.get('cpf')
        dd=self.get_info(cpf)
        if not dd:
            return {'response':False,'dados':{}}

        return {'response':True,'dados':dd}


    #####################################################################################################################################
    #####################################################################################################################################
    def _sende_mail(self, candidato, lista_thread, lista_de_espera): ## função para disparar o email de fato
        file=f'{sys.argv.get("path_templates")}{sys.argv.get("email_init")}'
        envioEmail=enviar_email(open(file,encoding='utf8').read())
        envioEmail.connect()
        candidato = self.get_info(candidato , lista_completa)
        if not candidato:
            print(f'erro {candidato}')
            self.erro_brutal.append(candidato)
            return False
        destino=candidato.get('DS_EMAIL')

        pwd=f'Acesso@{randint(10**5, 10**6-1)}'     #<< ------ senha fake para inscrito
        hash_pwd=sha256(pwd.encode()).hexdigest()
        candidato['PWD']=hash_pwd
        candidato['pwd_sem_hash']=pwd
        envioEmail.format_texto(candidato)
        index=candidato['INDEX']

        if candidato['EMAIL_ENVIADO'] == 'S':
            print(f'ja enviado para {destino}')
            lista_thread.pop(0)
            return False

        try:
            #########################################
            if '@' not in destino:
                self.__alter__(index,{'EMAIL_ENVIADO':'E'})
                return False
            envioEmail.disparo(destino,'Informação para matrícula na UFNT')   # envia email   << ----- envia email
            print(f'enviada para {destino}')
            envioEmail.desconect()
            self.add_in_db.append(candidato)
            data={'EMAIL_ENVIADO':'S','NU_PROCESSO':'2'}
            self.__alter__(index,data)
            ##########################################

        except :
            print(f'erro para {destino}')
            delete_do_banco(candidato)
            self.__alter__(index,{'EMAIL_ENVIADO':'E'})
            self.erros_ao_enviar+=1
            return False

        lista_de_espera.pop()
        lista_thread.pop(0)
        return candidato
    
    def __validar_thread(self,th0,  lista_de_espera):                          #  valida a quantidade de thread ativa   >>  salva no banco depois que todas morrerem
        cont=0
        q=len(lista_de_espera)
        while th0.is_alive() or len(lista_de_espera) > 0:
            if cont == 20:
                print('breakoo')
                break
            print('esperando para salvar no BANCO_SIM')
            print(lista_de_espera)
            sleep(1)
            if q == len(lista_de_espera):
                cont +=1
            else:
                q=len(lista_de_espera)
                cont=0

        sleep(2)
        if len(self.add_in_db)>0:
            inserir_no_banco(self.add_in_db)
        self.enviar_sok(f'end : {self.erros_ao_enviar} erros', space=True)
        salvar_csv()
        self.enviar_sok('reload')
        return 1
        Falaaa.json

    
    @validar_token
    def enviar_email(self, data):                                              # aqui preprapa a o envio do email
        lista_thread=[]
        self.enviados=[]
        self.erros_ao_enviar=0
        self.erro_brutal=[]
        send=data.get('NU_CPF_INSCRITO')
        self.reload=False
        if not send: return {'response': False , 'msg': 'valor invalido'}
        if not self.filtro:                                                    # se não tiver filtrado recarrega a lista, evita erro
            re= self.listar_candidatos({'Bearer':self.token})
            if not re.get('response'):
                return {'response': False, 'msg':'not reload in .csv'}

        self.add_in_db=list()
        if send == 'all':                                                       ############## envia par todos via thread
            lista_de_espera=[i for i in range(len(self.alunos_filtrados))]      # quantidade de thread a ser iniciada
            for candidato in self.alunos_filtrados:
                while len(lista_thread) > 11:
                    sleep(.5)
                sleep(.1)
                lista_thread.append(candidato)
                th0=Thread(target= self._sende_mail, args=(candidato, lista_thread, lista_de_espera), daemon=1)  #inicia as threads de disparo de email
                th0.start()
            Thread(target=self.__validar_thread, args=(th0, lista_de_espera), daemon=1).start()
            return {'response':True}

        else:                                                                    ############## envia email para apenas um, sem uso de thread
            re=self._sende_mail(send, [0], [0])
            if re:
                if inserir_no_banco([re]) == 0:
                    return {'response':True, 'msg':'salvo'}
            return {'response':False, 'msg':'processo já realizado'}

            

    @validar_token
    def upload_csv(self, data):
        global all_candidatos 
        if sys.argv.get('chamada_1'):
            if data.get('pwd') != self.pwd:
                return {'response': False, 'msg': 'erro na senha, arquivo já existe'}
        file=data['file']
        if file.filename.endswith('.csv'):
            nome_csv='./tempore.csv'
            file.save(nome_csv)
            gerar_data_frame(nome_csv)
            load_materias()
            load_sys.set_sys('chamada_1',True)
            return {'response': True, 'msg': 'Arquivo CSV salvo'}
        else:
            return {'response': False, 'msg': 'Apenas formato .CSV'}
    

    @validar_token
    def up_csv_espera(self, data):
        interesse=data['interesse']
        socioeconomica=data['socioeconomica']
        if not (socioeconomica.filename.endswith('.csv') and interesse.filename.endswith('.csv')):
            return {'response':False, 'msg':'arquivos não são .CSV'}
        buf1=io.BytesIO() #interesse.csv
        interesse.save(buf1)
        with open('interesse.csv','w',encoding='utf8') as arq:
            arq.write(buf1.getvalue().decode('utf8'))

        buf2=io.BytesIO() #'socioeconomica.csv'
        socioeconomica.save(buf2)
        with open('socioeconomica.csv','w',encoding='utf8') as arq:
            arq.write(buf2.getvalue().decode('latin1'))

        copyfile('./socioeconomica.csv','./para_rankear_socioeconomica.csv')
        return {'response':True, 'msg':'ok'}
    
    @validar_token
    def criar_csv_vagas(self,data):
        if data['file']:
            file=data['file']
            bufe=io.BytesIO()
            file.save(bufe)
            bufe.seek(0)
            dd=pd.read_excel(bufe,index_col=0)
            dd=dd.transpose()
            index=[nome_modalidade.get(i) for i in dd.index.to_list()]
            dd.index=index
            dd=loads(dd.to_json(force_ascii=0))
            file=f'{sys.argv.get("path_csv")}{sys.argv.get("csv_vagas_materias")}'
            dd_vagas=loads(open(file,'r',encoding='utf8').read())
            for mat in dd:
                for mod in dd[mat]:
                    if mod not in dd_vagas[mat]:
                        v=dd[mat][mod]
                        dd_vagas[mat][mod]=[v,v]
                    else:
                        dd_vagas[mat][mod][0]=dd[mat][mod]
            with open(file,'w',encoding='utf8') as arq:
                arq.write(dumps(dd_vagas, indent=4, ensure_ascii=0))
                arq.close()
                load_materias()
            return {"response":True, "msg": 'vagas atualizadas'}
        dd=get_materias().copy()
        dd={materias:{sigla_modalidade[mod]:dd[materias][mod][0] for mod in dd[materias]} for materias in dd}
        dd=pd.DataFrame(dd)
        dd=dd.transpose().sort_index().sort_index(axis=1)
        dd=dd.fillna(0).astype(int)
        bufer=io.BytesIO()
        dd.to_excel(bufer)
        bufer.seek(0)
        self.token_file={}
        token='1011'#sha256(f'{randint(10**20,10**21):X}'.encode()).hexdigest()   #<<<------token de send file
        file_name='csv_vagas.xlsx'
        self.token_file[token]=file_name
        sys.argv[file_name]=bufer        
        return {"response":True, "token": token}


    @validar_token
    def rankear(self,data):
        nome_csv='./para_rankear_socioeconomica.csv'
        completo_csv='./interesse.csv'
        if not exists(nome_csv):
            return {'response':False,'msg':'lista de espera não carregada'}
        file=rankear.rankeamento(nome_csv, completo_csv)  #(csv socioeconomica , csv de espera)
        seq_de_chamada()
        gerar_data_frame(file)
        load_materias()
        return {'response':True,'msg':f'chamada {sys.argv.get("chamada")} em adamento'}
    

    def __enviao_email_simples(self,cpf,html, msg=''):
        envioEmail=enviar_email(open(html,encoding='utf8').read())
        envioEmail.connect()
        candidato = self.get_info(cpf , lista_completa)
        candidato['MENSAGEM']=msg
        destino=candidato.get('DS_EMAIL')
        envioEmail.format_texto(candidato)
        index=candidato['INDEX']
        envioEmail.disparo(destino,'Informação para matrícula na UFNT')   # envia email   << ----- envia email
        print(f'enviada para {destino}')
        envioEmail.desconect()
        return True

    
    @validar_token
    def autenticar(self, data):
        reload_candidatos()
        def listar(data):  # ()
            camp_val={}
            campos=['NO_CURSO','SIGLA_MODALIDADE_CONCORRENCIA']
            lista=['NO_INSCRITO','NU_CPF_INSCRITO','DS_EMAIL','NO_CURSO',
                    'SIGLA_MODALIDADE_CONCORRENCIA','DADOS_ALTENTICADOS','MATRICULA']

            camp_val={}
            campos=['NO_CURSO','SIGLA_MODALIDADE_CONCORRENCIA']
            campo=data.get('campo')
            valor=data.get('valor')
            if campo:
                if valor == 'del':
                    self.filtro_autenticar.pop(campo)
                else:
                    self.filtro_autenticar.update({campo:valor})

            dd=data_filtro('DADOS_CONFIRMADOS == "S"')

            for i in campos:
                v=dd[i].unique().tolist()
                camp_val.update({i:v})
            for i in self.filtro_autenticar:
                dd=dd.query(f'{i} == "{self.filtro_autenticar[i]}"')

            if dd.empty:
                return {'response': False, 'msg':'sem lista'}
            return {'response': True, 'inscritos':self.__to_dict(dd,lista) , 'quantia':len(dd), 'campos_valores':camp_val,"filtro":self.filtro_autenticar}


        def ver(data):  #(cpf )
            file=f'{sys.argv.get("path_docs")}{cpf:0>11}.pdf'
            if not exists(file) and False:
                return {'response':False, 'msg':'candidato não encontrado'}
            self.dados_inscrito['file']=file
            query=f'DADOS_CONFIRMADOS == "S" and NU_CPF_INSCRITO == "{cpf}"'
            inscrito=data_filtro(query)
            if inscrito.empty:
                return {'response': False,  'msg':'usuario não encontrado'}
            self.dados_inscrito['index']=inscrito.index.to_list()[0]
            dd=self.__to_dict(inscrito)
            if not dd:
                return {'response': False,  'msg':'erro nos dados'}
            token=sha256(f'{randint(10**20,10**21):X}'.encode()).hexdigest()   #<<<------token de send file
            self.token_file[token]=file
            self.dados_inscrito.update(dd[0])
            return {'response': True,  'inscrito':dd[0],'token':token}

        
        def devolver(data):  #(cpf, texto )
            inscrito=data_filtro(f'NU_CPF_INSCRITO == "{cpf}"')
            v=inscrito['DADOS_CONFIRMADOS'].to_list()
            if v:
                if v[0] not in ['S','P']:
                    return {'response':False,'msg':'incrito  não iniciou o processo'}
                index=inscrito.index.to_list()[0]
                texto=data.get('texto')
                html=f'{sys.argv.get("path_templates")}{sys.argv.get("devolvido")}'
                self.__enviao_email_simples(cpf,html,texto)
                data={'CORRETO':'S' ,
                        'DADOS_CONFIRMADOS':'N' ,
                        'MATRICULA':'DEVOLVIDO',
                        'NU_PROCESSO':'0',
                        'DADOS_ALTENTICADOS':'N'}
                self.__alter__(index, data)
                return {'response':True,'msg':f'Um e-mal foi enviado para {self.dados_inscrito.get("DS_EMAIL")} para refazer o processo'}

            else: return {'response':False,'msg':'incrito  não encontrado'}

        
        def indeferir(data): #(cpf, txt)
            inscrito=self.get_info(cpf,['DADOS_CONFIRMADOS','NO_CURSO','NO_MODALIDADE_CONCORRENCIA','DADOS_ALTENTICADOS','MATRICULA'])
            index=inscrito['INDEX']
            if not inscrito:
                return {'response':False,'msg':'incrito  não encontrado'}
            if inscrito['DADOS_ALTENTICADOS'] not in ['I','S','P']:
                return {'response':False,'msg':'incrito  não iniciou o processo'}
            if inscrito['MATRICULA'] == 'INDEFERIDO':
                return {'response':False,'msg':f'Inscrito ja foi indeferido'}
            
            texto=data.get('texto')
            html=f'{sys.argv.get("path_templates")}{sys.argv.get("indeferido")}'
            data={'CORRETO':'S' ,
                    'DADOS_CONFIRMADOS':'S' , 
                    'NU_PROCESSO':'8',
                    'MATRICULA':'INDEFERIDO',
                    'DADOS_ALTENTICADOS':'S'}
            
            self.__enviao_email_simples(cpf,html,texto)
            self.__alter__(index, data)
            msg=''
            if inscrito['MATRICULA'] in ['PROVISORIA','DEFERIDO']:
                msg=f'e-mail enviado'
                alter_materias(inscrito['NO_CURSO'],inscrito['NO_MODALIDADE_CONCORRENCIA'], q= +1) #libera uma vaga

            return {'response':True,'msg':f'Matricula indeferida {msg}'}


        
        def deferir(data):  #(cpf, alter, pendente)
            v=self.get_info(cpf,['DADOS_CONFIRMADOS','NO_CURSO','NO_MODALIDADE_CONCORRENCIA','DADOS_ALTENTICADOS','MATRICULA'])
            index=v['INDEX']

            if v['DADOS_CONFIRMADOS']=='S':
                falta_doc=data.get('texto')
                temp=sys.argv.get("deferido")
                msg='matricula realizada'
                data={'DADOS_ALTENTICADOS':'S',
                      'MATRICULA':'DEFERIDO',
                       'NU_PROCESSO':'6',
                      'FALTA_DOCS':falta_doc,}
                if falta_doc:
                    temp=sys.argv.get("email_matricula_provisoria")
                    msg='matricula provisoria'
                    data['MATRICULA']='PROVISORIA'
                    data['NU_PROCESSO']='7'
                html=f'{sys.argv.get("path_templates")}{temp}'
                msg=''
                if v['MATRICULA'] !='DEFERIDO':
                    self.__enviao_email_simples(cpf,html,falta_doc)
                    msg='email enviado'
                self.__alter__(index, data)
                alter_materias(v['NO_CURSO'],v['NO_MODALIDADE_CONCORRENCIA'])
                return {'response':True, 'msg':f'dados atualizados apenas {msg}'}

            return {'response':False, 'msg':'ainda não validados'}

        
        def editar(data): #(cpf:str, alter:dict)
            v=self.get_info(cpf,['DADOS_CONFIRMADOS','NO_CURSO','NO_MODALIDADE_CONCORRENCIA','DADOS_ALTENTICADOS'])
            index=v['INDEX']
            if v['DADOS_CONFIRMADOS']=='S':
                dd=data.get('alter')
                dd['CORRETO']=''
                for i in dd:
                    alter_inscrito(index, i, dd[i].upper())
                return {'response':True, 'msg':f'dados atualizados: {" ".join(dd.keys())}'}

        ##---------
        re=locals().get(data.get('acao'))
        if re:
            cpf=data.get("cpf")
            return locals().get(data.get('acao'))(data)
        else:
            return {'response': False, 'msg': 'erro na opção'}

    
    @validar_token
    def sair(self, data):
        self.nome=b'cui34r9o8w4yntwtwg'
        self.ip=b'cui34r9o8w4yntwtwg'
        self.filtro=b'cui34r9o8w4yntwtwg'
        self.pwd=b'cui34r9o8w4yntwtwg'
        self.IO=b'cui34r9o8w4yntwtwg'
        self.dados_inscrito=b'cui34r9o8w4yntwtwg'
        return {'response':True}

    
    def __to_dict(self, data, lista=False):
        if not lista:
            lista=lista_completa
        return [data.iloc[i][lista].to_dict() for i in range(len(data))]
    
    def return_file(self, token, ip):
        if ip != self.ip:
            return False
        if token in self.token_file:
            return self.token_file.get(token)
        else: return False

    
    @validar_token
    def relatorio_de_materias(self, data):
        return get_materias()

    @validar_token
    def relatorio_matriculados(self, data):
        dd=data_filtro('DADOS_ALTENTICADOS == "S" | DADOS_CONFIRMADOS == "P"')
        if not dd.empty:
            file=f'./{sys.argv.get("csv_matriculados")}'
            dd[colunas_csv+['MATRICULA','FALTA_DOCS']].to_csv(file, sep=';', index=0, encoding='utf-8')
            token=sha256(f'{randint(10**20,10**21):X}'.encode()).hexdigest()   #<<<------token de send file
            self.token_file[token]=file
            return {'response': True, 'token': token }
        return {'response': False, 'msg': 'sem usuario autemticados' }

    
    @validar_token
    def alter_templates(self, data):
        acao=data.get('acao')
        if  acao== 'listar':
            l=listdir(sys.argv.get('path_templates'))
            l.remove('doc.html')
            return {'response': True, 'files':l}
        elif acao == 'tags':
            return {'response': True, 'tags':'kkk'}   ## continue
        elif acao == 'edit':
            texto=data.get('texto')
            file=data.get('file')+'.html'
            l=listdir(sys.argv.get('path_templates'))
            l.remove('doc.html')
            if file in listdir(sys.argv.get('path_templates')):
                with open(file) as file:
                    file.write(texto)
                    file.close()
                    return {'response': True, 'msg':'texto edidato'}
            else:
                return {'response': False, 'msg':f'{file[:-5]} não é um template'}
    
    @validar_token
    def revog_matricula(self, data):
        cpf=int(data.get('cpf'))
        files=[i for i in listdir(f"{sys.argv.get('path_csv')}") if i.endswith(sys.argv.get('csv_chamada')[4:])]
        for file in files:
            dd=pd.read_csv(f'{sys.argv.get("path_csv")}{file}',sep=';')
            v=dd.query(f'NU_CPF_INSCRITO == {cpf}')
            if v.empty:
                continue
            else:
                chamada=file.split('_')[0]
                file=f'{sys.argv.get("path_csv")}{chamada}_{sys.argv.get("file")}'
                data=pd.read_csv(file,sep=';')
                inscrito=data.query(f'NU_CPF_INSCRITO == {cpf}')
                index=inscrito.index.tolist()[0]
                curso,modalidade=inscrito[['NO_CURSO','NO_MODALIDADE_CONCORRENCIA']].values.tolist()[0]
                v=data.loc[index,'MATRICULA']
                if v=='S':
                    return {'response':False,'msg':'inscrito não matriculado'}
                data.loc[index,'MATRICULA']='N'
                data.loc[index,'RASTRO_ANALISADOR']=self.nome
                alter_materias(curso, modalidade , +1)
                return {'response':True,'msg':f'vaga liberada em {curso} {modalidade}'}

        return {'response':False,'msg':'cpf não encontrado'}


    def get_var(self):
        load_sys.set_sys('valor', 1000)
        return {'a':f'{sys.argv}'}

    
    def insert_in_db(self,data):
        cpf=data.get("cpf")
        if not cpf:
            return {'response':True, 'msg':'comunicação OK'}
        cpf=f'{int(cpf)}'
        pwd=data.get('pwd')

        dd={'Bearer':self.token}
        dd['cpf']=cpf

        inscrito=self.get_dados_inscrito(dd).get('dados')
        pwd=sha256(pwd.encode()).hexdigest()
        inscrito['PWD']=pwd

        #return {'response':True, 'msg':f'{inscrito}'}
        re=inserir_no_banco([inscrito])
        if re == 0:
            return {'response':True, 'msg':f'salvo {re}'}
        return {'response':False, 'msg':f'não salvo {inscrito}'}





lista_simples=[
    'NO_CAMPUS',
    'EMAIL_ENVIADO',
    'NO_INSCRITO',
    'DS_EMAIL',
    'DT_NASCIMENTO',
    'DS_MATRICULA',
    'NU_CPF_INSCRITO',
    'TP_SEXO',
    'SIGLA_MODALIDADE_CONCORRENCIA',
    'NO_CURSO',
    'DADOS_CONFIRMADOS'
        ]

lista_de_filtro=[
    'DS_TURNO',
    'DS_FORMACAO',
    'TP_SEXO',
    'ST_OPCAO',
    'NO_MODALIDADE_CONCORRENCIA',
    'ST_BONUS_PERC',
    'QT_BONUS_PERC',
    'NO_ACAO_AFIRMATIVA_BONUS',
    'NU_CLASSIFICACAO',
    'NO_IES',
    'SG_IES',
    'SG_UF_IES',
    'NO_CURSO',
    'NO_CAMPUS',
    'EMAIL_ENVIADO',
    'SIGLA_MODALIDADE_CONCORRENCIA',
    'DADOS_CONFIRMADOS',    # N  ou  S  ou  P  -> sem pdf
    'DADOS_ALTENTICADOS'
]


## new columns
new_columns=list(new_column)


colunas_csv=[
    'NO_CAMPUS',
    'CO_IES_CURSO',
    'NO_CURSO',
    'DS_TURNO',
    'DS_FORMACAO',
    'QT_VAGAS_CONCORRENCIA',
    'CO_INSCRICAO_ENEM',
    'NO_INSCRITO',
    'NO_SOCIAL',
    'NU_CPF_INSCRITO',
    'DT_NASCIMENTO',
    'TP_SEXO',
    'NU_RG',
    'NO_MAE',
    'DS_LOGRADOURO',
    'NU_ENDERECO',
    'DS_COMPLEMENTO',
    'SG_UF_INSCRITO',
    'NO_MUNICIPIO',
    'NO_BAIRRO',
    'NU_CEP',
    'NU_FONE1',
    'NU_FONE2',
    'DS_EMAIL',
    'NU_NOTA_L',
    'NU_NOTA_CH',
    'NU_NOTA_CN',
    'NU_NOTA_M',
    'NU_NOTA_R',
    'CO_CURSO_INSCRICAO',
    'ST_OPCAO',
    'NO_MODALIDADE_CONCORRENCIA',
    'ST_BONUS_PERC',
    'QT_BONUS_PERC',
    'NO_ACAO_AFIRMATIVA_BONUS',
    'NU_NOTA_CANDIDATO',
    'NU_NOTACORTE_CONCORRIDA',
    'NU_CLASSIFICACAO',
    'DS_MATRICULA',
    'DT_OPERACAO',
    'CO_IES',
    'NO_IES',
    'SG_IES',
    'SG_UF_IES',
    'SIGLA_MODALIDADE_CONCORRENCIA',
]

para_não_exibir=[
    'NU_NOTA_L',
    'NU_NOTA_CH',
    'NU_NOTA_CN',
    'NU_NOTA_M',
    'NU_NOTA_R',
    'CO_CURSO_INSCRICAO',
    'NU_NOTA_CANDIDATO',
    'NU_NOTACORTE_CONCORRIDA',
    'CO_IES'
]


lista_completa=colunas_csv + new_columns
for i in para_não_exibir:
    lista_completa.remove(i)
