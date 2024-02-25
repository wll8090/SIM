import sys
import pandas as pd
from static_csv.alter_materias import get_materias ,troca_vaga
from static_csv.data_frame_inscritos import nome_modalidade

sequencia_modalidade=['A1','A2','AC','LI_EP','LI_PCD','LI_PPI','LB_EP','LB_PCD','LB_Q','LB_PPI']

class incremente_in_sequecia:
    def __init__(self,curso) -> None:
        self.sequecia={i:[] for i in sequencia_modalidade}
        self.curso=curso
    
    def __repr__(self):
        return self.curso
    
    def insert(self,candidatos,dd, modalidade, q):
        re=dd.query(f'MODALIDADE_CONCORRENCIA == "{nome_modalidade[modalidade]}"')[['CPF','CLASSIFICACAO','CANDIDATO']]
        if re.empty:
            return dd, candidatos
        ll=re.values.tolist()
        ll.sort(key=lambda x: x[1])
        ll=ll[:q]
        self.sequecia[modalidade]+=ll
        for i in ll:
            cpf=i[0]
            dd=dd.query(f'CPF != {cpf}')
            candidatos=candidatos.query(f'CPF != {cpf}')
        return dd, candidatos

    def get(self):
        return self.sequecia
    
    def vaga(self, mod):
        re=len(self.sequecia[mod])
        return re
    


def rankeamento(file ,file2):  #( economica, interesse)
    candidatos=pd.read_csv(file, sep=';', encoding='utf8')
    candidatos=candidatos.assign(CHAMADA='')
    materias=get_materias()
    lista_convocados=[]
    for materia in materias:  # percorre  todas as materias
        #print(f'{materia:=<30}')
        obj_sequencia=incremente_in_sequecia(materia)   # cria um objeta para manipular os candidatos
        dd=candidatos.query(f'CURSO == "{materia}"')

        seq={i:sequencia[i][:] for i in sequencia}   # faz uma copy desvinculada do dict "sequencia" para essa materia

        for modalidade in sequencia_modalidade: 
            remaneja=seq[modalidade]
            vag=materias[materia]
            vagas=vag[nome_modalidade[modalidade]]
            vagas[0]
            ll=dd.query(f'MODALIDADE_CONCORRENCIA == "{nome_modalidade[modalidade]}"')[['CPF','CLASSIFICACAO','CANDIDATO']].values.tolist()

            if vagas[0] == 0:  # pula por não ter vaga
                #print(f'{modalidade} não tem vaga')
                continue
            q=len(ll)   #quantidade de inscrito
            sobra_vaga= vagas[0] - q
            #print(f'{modalidade: >6} {vagas[0]: >2} --> vem {q: >3} inscritos')
            if q > 0 :
                if vagas:
                    qq=vagas[0]-obj_sequencia.vaga(modalidade)
                    dd,candidatos=obj_sequencia.insert(candidatos, dd, modalidade, qq)
                if sobra_vaga < 1:
                    continue
            if modalidade == 'AC':
                continue
            cont=1
            while sobra_vaga > 0:
                i=remaneja[cont] # percorre a sequencia do remanejamento para a modalidade
                
                ll=dd.query(f'MODALIDADE_CONCORRENCIA == "{nome_modalidade[i]}"')[['CPF','CLASSIFICACAO','CANDIDATO']].values.tolist()
                q=len(ll)
                vag=materias[materia]
                vaga_i=vag[nome_modalidade[i]][0] - obj_sequencia.vaga(i)
                #print(f' --> {i} ', end='')
                if q > vaga_i:
                    if q > sobra_vaga:
                        q=sobra_vaga
                    
                    sobra_vaga-=q

                    #print(f' ainda tem {q} inscritos ::  jogou {q} para {i}    resta {sobra_vaga}')
                    materias=troca_vaga(materia, q, modalidade, i)  # remaneja a vaga que sobrou
                    dd, candidatos=obj_sequencia.insert(candidatos, dd, i, q)

                if i=='AC':
                    #print(f' ainda tem {q} inscritos ::  jogou {q} para {i}    resta {sobra_vaga}')
                    break
                cont+=1
        lista_convocados.append(obj_sequencia)


    lista_completa=pd.read_csv(file2,sep=';', encoding='utf8')
    colunas=lista_completa.columns.tolist()
    data=[colunas]
    for mat in lista_convocados:
        for mod in mat.get():
            for user in mat.get()[mod]:
                cpf=user[0]
                query=f'NU_CPF_INSCRITO == {cpf}'
                inscrito=lista_completa.query(query)
                inscrito.loc[inscrito.index,'NO_MODALIDADE_CONCORRENCIA']=nome_modalidade[mod]
                inscrito.loc[inscrito.index,'NU_CLASSIFICACAO']=user[1]
                re=inscrito.values.tolist()[0]
                data.append(re)

    candidatos.to_csv(file, sep=';', index=0)
    data=pd.DataFrame(data[1:], columns=data[0])
    file=f'./tempore_{sys.argv.get("chamada")}.csv'
    data.to_csv(file , sep=';', index=0)
    return file



sequencia={'AC' : ['AC'],
        'A1'      :['A1','AC'], 
        'A2'      :['A2','AC'],
        'LB_PPI'  :['LB_PPI',   'LB_Q',     'LB_PCD',   'LB_EP',    'LI_PPI',               'LI_PCD',   'LI_EP',    'AC'],
        'LB_Q'    :['LB_Q',     'LB_PPI',   'LB_PCD',   'LB_EP',    'LI_PPI',               'LI_PCD',   'LI_EP',    'AC'], 
        'LB_PCD'  :['LB_PCD',   'LB_PPI',   'LB_Q',     'LB_EP',    'LI_PPI',               'LI_PCD',   'LI_EP',    'AC'], 
        'LB_EP'   :['LB_EP',    'LB_PPI',   'LB_Q',     'LB_PCD',   'LI_PPI',               'LI_PCD',   'LI_EP',    'AC'], 
        'LI_PPI'  :['LI_PPI',   'LB_PPI',   'LB_Q',     'LB_PCD',   'LB_EP',                'LI_PCD',   'LI_EP',    'AC'],
       #'LI_Q'    :['LI_Q',     'LB_PPI',   'LB_Q',     'LB_PCD',   'LB_EP',    'LI_PPI',   'LI_PCD',   'LI_EP',    'AC'], 
        'LI_PCD'  :['LI_PCD',   'LB_PPI',   'LB_Q',     'LB_PCD',   'LB_EP',    'LI_PPI',               'LI_EP',    'AC'], 
        'LI_EP'   :['LI_EP',    'LB_PPI',   'LB_Q',     'LB_PCD',   'LB_EP',    'LI_PPI',               'LI_PCD',   'AC']
}
