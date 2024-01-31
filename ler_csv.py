import pandas as pd
import csv


with open('./static/1_candidatos.csv', encoding='utf8') as arq:
    ll=list(csv.reader(arq, delimiter=';'))
    data=pd.DataFrame(ll[1:],columns=ll[0])

    



