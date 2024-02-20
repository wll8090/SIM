from .obj_candidato import cantidato

class obj_travado(cantidato):
    def __init__(self, cpf, pwd, email, ip):
        super().__init__(cpf, pwd, email, ip)
    
    def __travado(self):
        return {'response':False, 'msg': f'Seu processo de chamada já terminou, olhe seu email'}
        
    @cantidato.validar_token
    def all_dados(self, data):
        return self.__travado()
   
    @cantidato.validar_token
    def send_dados(self, data):
        return self.__travado()
    
    @cantidato.validar_token
    def send_file(self, data):
        return self.__travado()
    
    @cantidato.validar_token
    def sair(self, data):
        return {'response':True}
    
    @cantidato.validar_token
    def meu_pdf(self,data):
        return self.__travado()
    
    @cantidato.validar_token
    def modelo_doc(self, data):
        return self.__travado()
    
    @cantidato.validar_token
    def aviso(self,data):
        return 'Seu processo de chamada já terminou, olhe seu email\n'

    @cantidato.validar_token
    def etapa(self, data):
        return {'response':True,'etapa':'Processo da matrícula 1° chamada terminou'}
