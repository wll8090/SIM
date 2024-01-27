import pandas as pd
import csv


with open('candidatos.csv', encoding='utf8') as arq:
    ll=list(csv.reader(arq, delimiter='\t'))
    data=pd.DataFrame(ll[1:],columns=ll[0])

    



