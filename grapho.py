# ------------------------------------------------------------
# Pacotes
# ------------------------------------------------------------
import numpy as np
import pandas as pd
import os
import glob
import re
import unidecode
import Levenshtein
import matplotlib.pyplot as plt
import networkx as nx

# ------------------------------------------------------------
# Funcoes
# ------------------------------------------------------------
from readidlist import readIdList
from extrafuns import *
# ------------------------------------------------------------

# ------------------------------------------------------------
# Função que compara dois títulos
# ------------------------------------------------------------
# Ajustar filtragem quanto ao ano e otimizar
def comparar_Titulos(dfPaperAuthor1, dfPaperAuthor2):
    interac = 0 #Contador de número de interações
    for i in range(len(dfPaperAuthor1)): #Percorre todos artigos do primeiro autor
        titulo1 = dfPaperAuthor1['TITULO AJUSTADO'].iloc[i]
        for j in range(len(dfPaperAuthor2)): #Percorre todos artigos do segundo autor
            titulo2 = dfPaperAuthor2['TITULO AJUSTADO'].iloc[j]
            if(comparar_String(titulo1, titulo2) == 1): print(f"Titulo1: {titulo1}\nTitulo2: {titulo2}")
            interac += comparar_String(titulo1, titulo2) #Chama a função que retorna 1 se houve interação, ou 0 senão, incrementando o retorno ao valor de interac
    return interac 

# ------------------------------------------------------------
# Função que analisa a similaridade entre duas Strings
# ------------------------------------------------------------
def comparar_String(string1, string2):
    if len(string1) == 0 or len(string2) == 0: #Se uma das Strings for vazia, não há similaridade
        return 0
    if len(string1) >= 10 and len(string2) >= 10 and Levenshtein.distance(string1, string2) <= 5: #Se as duas Strings tiverem mais de 10 caracteres e a distância de Levenshtein entre elas for menor que 5, elas são similares
        return 1
    else: #Senão, retorna 0
        return 0

# ------------------------------------------------------------
# Função que ajusta uma String
# ------------------------------------------------------------
def ajustar_String(string):
    string = string.lower() #Toda String fica em caixa baixa
    novaString = unidecode.unidecode(string) #Transforma toda a String em unicode (sem acentos, sem cidilha)
    novaString = novaString.replace(" ", "") #Une toda a string, retirando os espaços
    novaString = re.sub('[^a-zA-Z0-9]', '', novaString) #Exclui caracteres especiais
    return novaString

# ------------------------------------------------------------
# Função que pega o ano inicial e final
# ------------------------------------------------------------
def anosPublicação():
    config_file = open('./config.txt', 'r', encoding='utf-8')
    linhas = config_file.readlines() #Ler todas as linhas do config.txt

    anoInicial = linhas[5].split(':')[1]
    anoInicial = anoInicial.rstrip('\n')
    anoInicial = anoInicial.strip(' ')
    anoInicial = float(anoInicial) #Ler ano inicial

    anoFinal = linhas[6].split(':')[1]
    anoFinal = anoFinal.rstrip('\n')
    anoFinal = anoFinal.strip(' ')
    anoFinal = float(anoFinal) #Ler ano final

    config_file.close()

    return (anoInicial, anoFinal)

# ------------------------------------------------------------
# Função que filtra os projetos de acordo ao ano inicial estabelecido
# ------------------------------------------------------------
def filtrarProjetos(dfppe_uniq, anoInicial):
    dfppe_uniq['YEAR_INI'] = dfppe_uniq['YEAR_INI'].replace('VAZIO', -99) #Onde não tem o ano inicial do projeto, subistitui por 99
    num99 = dfppe_uniq[dfppe_uniq['YEAR_INI'] == -99] #Salva todo o dataFrame sem ano inicial para o projeto
    if len(num99) >= 1: #Se houver projetos sem ano inicial, imprime o número de projetos sem ano inicial
        print('------------------------------------------------------------')
        print('ATENCAO: ' + str(len(num99)) + 'projetos sem ano inicial')
        print('------------------------------------------------------------')
    dfppe_uniq['YEAR_INI'] = dfppe_uniq['YEAR_INI'].apply(ff)
    dfppe_uniq = dfppe_uniq[(dfppe_uniq['YEAR_INI'] >= anoInicial)] #Filtra os projetos com o anoInicial estabelecido no parâmetro

    return dfppe_uniq

# ------------------------------------------------------------
# Função que filtra os periodicos de acordo ao ano de publicação
# ------------------------------------------------------------
def filtrarPeriodicos(dfpaper, dfpaper_uniq, anoInicial, anoFinal):
    #Onde não tem o ano de publicação, subistitui por 99
    dfpaper['YEAR'] = dfpaper['YEAR'].replace('VAZIO', -99) 
    dfpaper_uniq['YEAR'] = dfpaper_uniq['YEAR'].replace('VAZIO', -99) 
    num99 = dfpaper[dfpaper['YEAR'] == -99] #Salva todo o dataFrame sem ano de publicação
    if len(num99) >= 1: #Se houver periódicos sem ano de publicação...
        print('------------------------------------------------------------')
        print('ATENCAO: ' + str(len(num99)) + 'artigos sem ano de publicacao')
        print('------------------------------------------------------------')
    #Transforma todos os anos em float
    dfpaper['YEAR'] = dfpaper['YEAR'].apply(ff)
    dfpaper_uniq['YEAR'] = dfpaper_uniq['YEAR'].apply(ff)
    #Realiza a filtragem do dataFrame, onde o ano de publicação está entre o anoInicial e anoFinal
    dfpaper = dfpaper[(dfpaper['YEAR'] >= anoInicial) & (dfpaper['YEAR'] <= anoFinal)]
    dfpaper_uniq = dfpaper_uniq[(dfpaper_uniq['YEAR']
                                 >= anoInicial) & (dfpaper_uniq['YEAR'] <= anoFinal)]
    #Cria uma nova coluna com os Títulos ajustados para Unicode e sem caracteres especiais
    dfpaper['TITULO AJUSTADO'] = dfpaper.apply(lambda x : ajustar_String(x.TITLE), axis=1)
    dfpaper_uniq['TITULO AJUSTADO'] = dfpaper_uniq.apply(lambda x : ajustar_String(x.TITLE), axis=1)

    return (dfpaper, dfpaper_uniq)

# ------------------------------------------------------------
# Função que calcula as interações entres os autores da rede
# ------------------------------------------------------------
def calcularInteracoes(df_idlist, dfpaper, dataFrameFullname):
    #Cria uma lista com os IDs de um autor, uma outra lista com os IDs dos autores a serem comparados e uma lista da quantidade de interações entre esses dois autores
    lsid = []
    lsid_tocompare = []
    lsinter_qtd = []
    for m in range(len(df_idlist)): #Percorre o dataFrame com os IDs
        id = df_idlist.iloc[m, 0]#Pega o ID de um autor
        dataFrameID = dfpaper[dfpaper['ID'] == id] #Filtra o dataFrame para ter somente as publicações daquele ID
        dataFrameID['TITLE'].to_csv(f"papers_{id}.csv")
        dfids_tocompare = dataFrameFullname[dataFrameFullname['ID'] != id] #Filtra o dataFrame com os nomes e IDs para ter somente os IDs a serem comparados
        for n in range(len(dfids_tocompare)): #Percorre agora este dataFrame
            id_tocompare = dfids_tocompare.iloc[n, 0] #Pega o ID do outro autor a ser comparado
            dataFrameID_tocompare = dfpaper[dfpaper['ID'] == id_tocompare] #Filtra o dataFrame para ter somente as publicações daquele ID
            lsid.append(id)
            lsid_tocompare.append(id_tocompare)
            interac = comparar_Titulos(dataFrameID, dataFrameID_tocompare) #Recebe quantas interaões houve entre esses dois autores
            if(interac > 0):
                print(f'ID: {id}, ID_COMPARE: {id_tocompare}\nInterac: {interac}')
            lsinter_qtd.append(interac)

    return (lsid, lsid_tocompare, lsinter_qtd)

def getgrapho():
    
    df_idlist = readIdList() #Lendo a lista dos IDs e nome dos pesquisadores
    anos = anosPublicação()
    anoInicial = anos[0] #Ler ano inicial para períodicos
    anoFinal = anos[1] #Ler ano final para periódicos

    # ------------------------------------------------------------
    # importadando os data frames gerados pelo gettidy
    # ------------------------------------------------------------
    dfppe_uniq = pd.read_csv('./csv_producao/projetos_uniq.csv',
                             header=0, dtype={'ID':str})
    dfpaper = pd.read_csv('./csv_producao/periodicos_all.csv',
                          header=0, dtype={'ID':str})
    dfpaper_uniq = pd.read_csv('./csv_producao/periodicos_uniq.csv',
                               header=0, dtype={'ID':str})
    # filtrando o ano
    # projetos filtrados
    dfppe_uniq = filtrarProjetos(dfppe_uniq, anoInicial)
    # periodicos filtrados
    periodicos = filtrarPeriodicos(dfpaper, dfpaper_uniq, anoInicial, anoFinal)
    dfpaper = periodicos[0]
    dfpaper_uniq = periodicos[1]
    # ordenando por ano (crescente)
    dfppe_uniq_pesq = dfppe_uniq[dfppe_uniq['NATUREZA'] == 'PESQUISA']
    dfppe_uniq_pesq = dfppe_uniq_pesq.sort_values(['YEAR_INI'])
    dfppe_uniq_ext = dfppe_uniq[dfppe_uniq['NATUREZA'] == 'EXTENSAO']
    dfppe_uniq_ext = dfppe_uniq_ext.sort_values(['YEAR_INI'])
    dfpaper = dfpaper.sort_values(['YEAR'])
    dfpaper_uniq = dfpaper_uniq.sort_values(['YEAR'])
    # carregando dataFrame com dados pessoais
    listaFullnameCSV = glob.glob('./csv_producao/*fullname.csv')
    # dataFrame com nome completo, sobrenome e id
    dataFrameFullname = pd.DataFrame()
    #Percorre todos a lista de csv com o Fullname e o adiciona ao dataFrameFullname
    for i in range(len(listaFullnameCSV)):
        a = pd.read_csv(listaFullnameCSV[i], header=0, dtype='str')
        dataFrameFullname = dataFrameFullname.append(a, ignore_index=False)
    # passando ID para string, para poder comparar com dfpaper
    dataFrameFullname['ID'] = dataFrameFullname['ID'].apply(ss)
    dataFrameFullname = dataFrameFullname.reset_index(drop=True)
    # verificando a interacao de periodicos entre integrantes
    tuplaInterac = calcularInteracoes(df_idlist, dfpaper, dataFrameFullname)
    lsid = tuplaInterac[0]
    lsid_tocompare = tuplaInterac[1]
    lsinter_qtd = tuplaInterac[2]

    dfinterac = pd.DataFrame({'IDD': lsid,
                              'IDD_COMP': lsid_tocompare,
                              'WEIGHT': lsinter_qtd})
    # data frame para profissionais sem interacao em periodicos
    lsnointer_period = []
    for m in range(len(df_idlist)):
        aano = dfinterac[dfinterac['IDD'] == df_idlist.iloc[m, 0]]
        aasum = aano['WEIGHT'].sum()
        aano_a = dfinterac[dfinterac['IDD_COMP'] == df_idlist.iloc[m, 0]]
        aasum_a = aano_a['WEIGHT'].sum()
        if aasum == 0 and aasum_a == 0:
            nointer = dataFrameFullname[dataFrameFullname['ID'] ==
                                 df_idlist.iloc[m, 0]].reset_index(drop=True)
            nointer = nointer.iloc[0, 1]
            lsnointer_period.append(nointer)
    dfnointerac = pd.DataFrame({'NOME': lsnointer_period})
    dfnointerac.to_csv('./csv_producao/periodicos_nointer.csv',
                       index=False, sep=',')
    # DANGER ATTENTION
    # dfinterac.to_csv('test.csv', index=False)
    # eliminando linhas sem interacao
    indexremove = []
    for i in range(len(lsid)):
        if lsinter_qtd[i] == 0:
            indexremove.append(i)
    for index in sorted(indexremove, reverse=True):
        del lsid[index]
        del lsid_tocompare[index]
        del lsinter_qtd[index]
    # ------------------------------------------------------------
    # Grapho
    plt.figure(figsize=(12, 9.5))
    G = nx.Graph()
    for i in range(len(lsid)):
        G.add_edge(lsid[i],
                   lsid_tocompare[i],
                   weight=lsinter_qtd[i])
    
    pos = nx.spring_layout(G, 1.75)
    # colors for nodes
    colours = ['#5a7d9a', 'red', 'green', 'yellow',
               'gray', 'orange', 'blue', 'magenta',
               '#00555a', '#f7d560', 'cyan',    '#b6b129',
               '#a1dd72', '#d49acb', '#d4a69a', '#977e93',
               '#a3cc72', '#c60acb', '#d4b22a', '#255e53',
               '#77525a', '#c7d511', '#c4c22b', '#c9b329',
               '#c8dd22', '#f75acb', '#b1a40a', '#216693',
               '#b1cd32', '#b33acb', '#c9a32b', '#925e11',
               '#c5dd39', '#d04205', '#d8a82a', '#373e29']
    lsgroup_uniq = df_idlist['GROUP'].unique()
    dic_colours = {}
    for i in range(len(lsgroup_uniq)):
        dic_colours[lsgroup_uniq[i]] = colours[i]
    a = list(G.nodes())
    node_colours = []
    for i in range(len(a)):
        x = df_idlist[df_idlist['ID_LATTES'] == a[i]]
        x = x.iloc[0, 2]
        c = dic_colours[x]
        node_colours.append(c)
    # nodes
    nx.draw_networkx_nodes(G, pos,
                           node_size=400,
                           node_shape='o',
                           node_color=node_colours,
                           alpha=0.7)
    # labels
    nn = list(G.nodes)
    diclabel = {}
    for i in range(len(nn)):
        x = df_idlist[df_idlist['ID_LATTES'] == nn[i]]
        xid = x.iloc[0, 0]
        xname = x.iloc[0, 1]
        diclabel[str(xid)] = xname
    # edges
    nx.draw_networkx_edges(G, pos,  # edgelist=lsinter_qtd,
                           width=1, edge_color='orange')
    # labels
    nx.draw_networkx_labels(G, pos, labels=diclabel, font_size=16,
                            font_family='sans-serif')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('./relatorio/figures/grapho.png')
    nx.write_gexf(G, "test.gexf")