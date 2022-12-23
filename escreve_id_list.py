import pandas as pd

arquivoCSV = pd.read_csv("lista lucyLattes publicacoes indexadas em coautoria - Sheet1.csv", dtype={'ID':str})

ids = arquivoCSV["ID"]
nomes = arquivoCSV["Docente"]

with open("list_id_name.txt", "a", encoding="utf-8") as arq:
    
    for i in range(len(ids)):
        arq.write(f"{ids[i]},{''.join(nomes[i].split())},GROUP\n")
        