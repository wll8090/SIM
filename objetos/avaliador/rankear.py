import sys
from static_csv.alter_materias import get_materias ,load_materias
import pandas as pd

sequencia_modalidade=[
    "Ampla concorrência",
    "Candidatos que, independentemente da renda, tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).",
    "Candidatos com deficiência, independentemente da renda, que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).",
    "Candidatos autodeclarados pretos, pardos ou indígenas, independentemente da renda, que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).",

    "Candidatos com renda familiar bruta per capita igual ou inferior a 1 salário mínimo que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).",
    "Candidatos com deficiência, que tenham renda familiar bruta per capita igual ou inferior a 1 salário mínimo e que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012)",
    "Candidatos autodeclarados quilombolas, com renda familiar bruta per capita igual ou inferior a 1 salário mínimo e que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).",
    "Candidatos autodeclarados pretos, pardos ou indígenas, com renda familiar bruta per capita igual ou inferior a 1 salário mínimo e que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).",
    
    "Indígenas",
    "Quilombola" ]

def rankeamento(file):
    candidatos=pd.read_csv(file, sep=';')
    candidatos=candidatos.assign(CHAMADA='')
    materias=get_materias()
    nova_chamada=[candidatos.columns.to_list()]
    for materia in materias:
        for modalidade in sequencia_modalidade:
            dd=candidatos.query(f'NO_CURSO == "{materia}"')
            vag=materias.get(materia)
            vagas=vag.get(modalidade)
            if not vagas:
                continue
            ll=dd.query(f'NO_MODALIDADE_CONCORRENCIA == "{modalidade}"')[['NU_CPF_INSCRITO','NU_CLASSIFICACAO','NO_INSCRITO']].values.tolist()
            ll.sort(key=lambda x: x[1])
            ll=ll[:vagas[1]]
            for i in ll:
                cpf=i[0]
                req=f'NU_CPF_INSCRITO == {cpf} & NO_MODALIDADE_CONCORRENCIA == "{modalidade}"'
                nova_chamada.append(candidatos.query(req).values.tolist()[0])
                dd=dd.query(f'NU_CPF_INSCRITO != {cpf}')
                candidatos=candidatos.query(f'NU_CPF_INSCRITO != {cpf}')
    candidatos.to_csv(file,sep=';', index=0)
    data=pd.DataFrame(nova_chamada[1:], columns=nova_chamada[0])
    file=f'./tempore_{sys.argv.get("chamada")}.csv'
    data.to_csv(file , sep=';', index=0)
    return file
