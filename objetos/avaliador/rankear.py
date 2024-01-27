from static.data_frame_inscritos import get_data_frame, salvar_cahamda

def rankeamento():
    data=get_data_frame()
    cursos={i:[] for i in data['NO_CURSO'].unique()}
    modalidades=data['NO_MODALIDADE_CONCORRENCIA'].unique()
    dd={i: data.query(f'NO_CURSO == "{i}"')[['NU_CPF_INSCRITO','NU_NOTA_CANDIDATO','NO_MODALIDADE_CONCORRENCIA']].to_dict('records') for i in cursos}


    for curso in list(cursos):      ## sequiencia de cursos
        candidatos=[k['NU_CPF_INSCRITO'] for k in dd[curso]]    # lista todos os cpf do cuso  [cpf, cpf]
        ld={lll:[] for lll in modalidades}  #separa por modalidade     { modalidade:[] } 

        [ld.get(ii['NO_MODALIDADE_CONCORRENCIA']).append([ii['NU_CPF_INSCRITO'],ii['NU_NOTA_CANDIDATO']]) for ii in dd[curso]]  #adiciona na lista de cada modalidade   {'modlidade':[[cpf,nota],[cpf,nota]]}

        ## implemente cpf em todas as modalidades possiveis ##--##--##--##--##

        [ld.get(i).sort(key=lambda x: x[1],reverse=True) for i in ld]   # organisa por maior nota  {'modlidade':[[cpf,nota]]}

        ld={i_ld:[cpf[0] for cpf in ld[i_ld]] for i_ld in ld}    # retira a nota  {'modlidade':[cpf,cpf]}

        mod={i:[] for i in modalidades}
        for cpf in candidatos:   ## verifica a melhor posição do cpf
            pp=-1
            mod_conco=''
            for ii in ld:
                if cpf in ld[ii]:
                    p=ld[ii].index(cpf)
                    if p > pp:
                        pp = p
                        if mod_conco!='':
                            mod[mod_conco].remove(cpf)
                        mod[ii].append([cpf,pp])
                        mod_conco=ii

        for i in mod:  ## organiza o json de saída
            for ii in mod[i]:
                pox=mod[i].index(ii)
                mod[i].remove(ii)
                nota=data.query(f'NU_CPF_INSCRITO == "{ii[0]}"')['NU_NOTA_CANDIDATO'].values.tolist()[0]
                mod[i].insert(pox,{'NU_CPF_INSCRITO':ii[0],'NU_NOTA_CANDIDATO':nota,'POSICAO':ii[1]})
        
        cursos[curso]=mod
    data = get_data_frame()
    data = data.assign(NOVA_MODALIDADE='')
    data = data.assign(NOVA_POSICAO='')
    for curso in cursos:
        for modalidade in cursos[curso]:
            for cpf in cursos[curso][modalidade]:
                index=data[data['NU_CPF_INSCRITO']==cpf['NU_CPF_INSCRITO']].index[0]
                data.loc[index,"NOVA_MODALIDADE"]=modalidade
                data.loc[index,"NOVA_POSICAO"]=int(cpf['POSICAO'])+1
    
    salvar_cahamda(data)
    return mod
           
            
