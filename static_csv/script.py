import json

vagas={
    'Candidatos autodeclarados pretos, pardos ou indígenas, com renda familiar bruta per capita igual ou inferior a 1 salário mínimo e que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':[4,4],
    'Candidatos autodeclarados pretos, pardos ou indígenas, independentemente da renda, que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':[4,4],
    'Candidatos autodeclarados quilombolas, com renda familiar bruta per capita igual ou inferior a 1 salário mínimo e que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':[1,1],
    'Candidatos com deficiência, independentemente da renda, que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':[1,1],
    'Candidatos com deficiência, que tenham renda familiar bruta per capita igual ou inferior a 1 salário mínimo e que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012)':[1,1],
    'Candidatos com renda familiar bruta per capita igual ou inferior a 1 salário mínimo que tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':[1,1],
    'Candidatos que, independentemente da renda, tenham cursado integralmente o ensino médio em escolas públicas (Lei nº 12.711/2012).':[1,1],
    'Indígenas':[1,1],
    'Quilombola':[1,1]
}


def adicionar_indigenas(dados_json):
    for materia in dados_json:
        for mod in vagas:
            if mod not in dados_json[materia]:
                dados_json[materia][mod]=vagas[mod]

# Caminho para o seu arquivo JSON
caminho_json = "./vaga_materias.json"

# Lendo o JSON do arquivo
with open(caminho_json, "r", encoding="utf-8") as arquivo:
    dados_json = json.load(arquivo)

# Chamando a função para adicionar a categoria "Indígenas"
adicionar_indigenas(dados_json)

def sav():
    # Escrevendo de volta no arquivo
    with open(caminho_json, "w", encoding="utf-8") as arquivo:
        json.dump(dados_json, arquivo, ensure_ascii=False, indent=4)

sav()
