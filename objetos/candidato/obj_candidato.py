from datetime import datetime
from io import BytesIO
from random import randint
from hashlib import sha256
from os import listdir, chdir
from static.data_frame_inscritos import *
from os.path import exists
from json import loads

from PyPDF2 import PdfMerger
import sys


class cantidato:
    def validar_token(funk):
        def new_funk(self, dado):
            if dado.get('Bearer') == self.token:
                return funk(self, dado)
            return {'response':False, 'msg':'erro no token'}
        return new_funk


    def __init__(self, cpf, pwd, email, ip):
        self.pwd=pwd
        self.email=email
        self.cpf=cpf
        self.ip=ip
        self.index=data_filtro(f'NU_CPF_INSCRITO =="{self.cpf}"').index[0]
    
    def __alter__(self, campo, valor):
        alter_inscrito(self.index, campo, valor)
    
    def __my_filtro(self, campo):
        return data_filtro(f'index == {self.index}')[campo].to_list()[0]


    def login(self):
        n=randint(10**5,10**6-1)
        self.token='1001'  #sha256(f'{datetime.now().strftime("%d-%m-%Y")}--{self.ip}--{n}').hexdigest()
        self.dados=data_filtro(f'index == {self.index}')
        self.user=self.dados.get('NO_INSCRITO')
        return True
    
    def my_dados(self):
        dados=self.dados[lista_dados_login].to_dict(orient="records")[0]
        return {'dados':dados ,'token':self.token}
    

    @validar_token
    def all_dados(self, data):
        if self.__my_filtro('DADOS_CONFIRMADOS') == 'N' :
            dd=self.dados[lista_de_valores].to_dict(orient='records')[0]
            return {'response':True, 'dados':dd ,'msg':'ok'}
        return {'response':False, 'msg': 'dados já confirmados','dados':{}}

                
    @validar_token
    def send_dados(self, data):
        reload_candidatos()
        v=self.dados['DADOS_CONFIRMADOS'].to_list()[0]
        print(v,'kkkkk')
        correto=data.get('erro')
        if data.get('confirm'):
            if v == 'P' or v == 'S':
                return {'response':False,'msg':'dado ja confirmado'}
            if correto:
                self.__alter__('CORRETO', correto)
            self.__alter__('DADOS_CONFIRMADOS','P')
            self.__alter__('NU_PROCESSO','3')
            return {'response':True, 'msg':'dados confirmados'}
        return {'response':False,'msg':'formato invalido'}
    
    
    @validar_token
    def send_file(self, data):
        reload_candidatos()
        v=self.__my_filtro('DADOS_CONFIRMADOS')
        if v == 'S':
            return {'response':False,'msg':'arquivo ja foi salvo'}
        elif v == 'N':
            return {'response':False,'msg':'validar dados primeiro'}
        pdf=all([data['files'][i].mimetype=='application/pdf' for i in docs if data['files'].get(i) != None])
        if not pdf:
            return {'response':False,'msg':'algum arquivo não é .pdf'}
        
        merge=PdfMerger()
        text=''
        for file in docs:
            ff=data['files'].get(file)
            if ff:
                merge.append(BytesIO(ff.read()))
            else:
                text+=file+', '
        merge.write(f'./docs/{self.cpf:0>11}.pdf')
        self.__alter__('DADOS_CONFIRMADOS','S')
        self.__alter__('NU_PROCESSO','4')
        self.__alter__('SEM_PDF',text)
        return {'response':True, 'msg':f'Documento salvo| arquivos não eviados: {text}'}
    
    @validar_token
    def etapa(self, data):
        reload_candidatos()
        v=self.__my_filtro('NU_PROCESSO')
        etapa={'0':'0 - Indeferido',
        '1':'1 - Aprovado',
        "2":'2 - Aguradando confirmação de dados',
        "3":'3 - Dados confirmado',
        "4":'4 - Documentos enviados',
        "5":'5 - Documentos autenticados',
        "6":'6 - Deferido, eba!' }
        return {'response':True,'etapa':etapa[v]}
    
    @validar_token
    def sair(self, data):
        return {'response':True}
    
    @validar_token
    def meu_pdf(self,data):
        return {'response':'True','lista':docs}
    
    @validar_token
    def modelo_doc(self, data):
        file=data.get('file')
        if file=='all':
            return  {'response':True,'lista':listdir('./modelo_docs')}
        else: 
            file=f'./modelo_docs/{file}'
            if exists(file):
                return file
            return {'resposne':False,'msg':'arquivo não encontrado'}
    
    def get_var_user(self):
        return f'{sys.argv}'
            


lista_dados_login=[
    'DADOS_CONFIRMADOS',
    'DS_EMAIL',
    'DT_NASCIMENTO',
    'NU_CPF_INSCRITO',
    'NO_INSCRITO',
    'TP_SEXO'
]

lista_de_valores=[
            #'CO_CURSO_INSCRICAO', 
            #'CO_IES', 
            #'CO_IES_CURSO', 
            #'CO_INSCRICAO_ENEM', 
            'DS_COMPLEMENTO',
            'DS_EMAIL', 
            'DS_FORMACAO', 
            'DS_LOGRADOURO', 
            #'DS_MATRICULA',
            'DS_TURNO',
            'DT_NASCIMENTO',
            #'DT_OPERACAO', 
            #'NO_ACAO_AFIRMATIVA_BONUS', 
            'NO_BAIRRO', 
            'NO_CAMPUS', 
            'NO_CURSO', 
            'NO_IES', 
            'NO_INSCRITO',
            'NO_MAE', 
            'NO_MODALIDADE_CONCORRENCIA', 
            'NO_MUNICIPIO', 
            'NO_SOCIAL', 
            'NU_CEP', 
            'NU_CPF_INSCRITO', 
            'NU_FONE1',
            'NU_FONE2', 
            'NU_ENDERECO', 
            #'NU_ETAPA', 
            #'NU_CLASSIFICACAO', 
            #'NU_NOTACORTE_CONCORRIDA', 
            #'NU_NOTA_CANDIDATO',
            #'NU_NOTA_CH', 
            #'NU_NOTA_CN',
            #'NU_NOTA_L', 
            #'NU_NOTA_M', 
            #'NU_NOTA_R', 
            'NU_RG',
            #'QT_BONUS_PERC',
            #'QT_VAGAS', 
            'SG_UF_INSCRITO', 
            #'ST_BONUS_PERC', 
            #'ST_OPCAO',
            'SG_IES', 
            'TP_SEXO',
            'SG_UF_IES', 
            #'1', 
            #'2', 
            #'3',
            #'4', 

            ## new columns
            #'EMAIL_ENVIADO',        # N  ou  S           
            'DADOS_CONFIRMADOS',    # N  ou  S  ou  P  -> sem pdf
            'DADOS_ALTENTICADOS',    # N  ou  S  ou  p  -> sem ver o pdf
            #'CORRETO',              # forma correta a ser corrigido
            ]


docs=['*Frente do RG',
      '*Costa do RG',
      '*CPF',
      '*Cestição de nascimento',
      'Comprovante do estado civil',
      '*Comprovante de residencia',
      '*Certidão de quitacao eleitoral',
      'Resevista',
      '*Certificado de conclusão do ensino médio',
      'Declaração de estudos em escolas públicas',
      '*Histórico escolardo ensino médio',
      'Declaração de inexistência vinculo',
      'Declaração de composisão famíliar',
      'Termo de responsabilidade e veracidade das informações',

      'outros'
      ]