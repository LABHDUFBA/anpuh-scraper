# title: anpuh-scraper.py
# description: Scraper de resumos dos Simpósios Nacionais de história
# da Anpuh entre 2013 e 2021
# author: Eric Brasil
# email: ericbrasiln@protonmail.com
# github: ericbrasiln
# date: July, 29th, 2021
# License: MIT License

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pprint import pprint

dic = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
now = datetime.now()
date = now.strftime("%Y-%m-%d_%H-%M-%S")

print('\nRaspador dos resumos dos Simpósios Nacionais de História da Associação Nacional de História - Anpuh.\n'
      'O programa raspa todos os resumos dos SNH 27, 28, 29, 30 e 31, respectivamente dos anos de 2013, 2015, 2017, 2019 e 2021\n'
      'Autoria: Eric Brasil  (IHL-UNILAB, LABHDUFBA)\n')
print('-=-'*30)

snhYears= list()
while True:
    snhYears.append(int(input('Digite o ano do primeiro evento [entre 2013, 2015, 2017, 2019 e 2021] que deseja raspar: ')))
    resp = str(input('Deseja inserir outro ano para raspagem? [S/N] '))
    if resp in 'Nn':
        print('-=-'*50)
        break
snhYears.sort()

snhList = str(snhYears)
for r in ",[]":
    snhList = snhList.replace(r,'')
snhList = snhList.replace(' ','_')

listaFinal=[]

def cleanAbstract(abstract):
    '''
    Função que limpa o resumo do evento
    '''
    abstract = abstract.replace('\n', ' ')
    abstract = abstract.replace('Resumo: ','')
    abstract = abstract.replace('Ocultar','')
    abstract = abstract.replace('RESUMO','')
    return abstract

def saveDF(listaFinal,date):
    '''
    Função que salva o DataFrame com os resumos dos simpósios Nacionais de História da Anpuh
    '''
    df = pd.DataFrame(listaFinal, columns=['Ano', 'Evento', 'Cidade', 'ST', 'Coordenadores', 'Autor(es)/Instituições', 'Título', 'Resumo'])
    df.to_csv(f'resumos_anpuh_{snhList}_{date}.csv')

def getAbstract(bs, year, listaFinal):
    '''
    Função que raspa os resumos de cada simpósio Nacional de História
    '''
    if year == 2013:
        city = 'Natal'
        event = 'XXVII'
    if year == 2015:
        city = 'Florianópolis'
        event = 'XXVIII'
    if year == 2017:
        city = "Brasília"
        event = 'XXIX'
    if year == 2019:
        city = 'Recife'
        event = 'XXX'
    if year == 2021:
        city = 'Rio de Janeiro'
        event = 'XXXI'
    if year in [2013, 2015]:
        STContent = bs.find(class_='content-interna')
    elif year in [2017, 2019]:
        STContent = bs.find(id='conteudo-spacer')
    else:
        STContent = bs.find(class_='col-xl-9 col-lg-8 pl-4 pr-4 pt-3 pb-3 w-100')
    if year == 2021:
        STInfos = STContent.find(class_='container')
        STtitle = STInfos.find('h3').text
        coordinators = STInfos.find('b').text
        ST_table = STInfos.find('table')
        sts = ST_table.find_all('tr')
    else:
        STInfos = STContent.find_all('table')
        STInfosGeral = STInfos[0]
        sttest = STInfosGeral.find_all('tr')
        STtitle = sttest[0].find('h3').text
        coordinators = sttest[1].find('b').text
        print(f'{STtitle}\n{coordinators}\n')
        sts = STInfos[1].find_all('td')
    for paper in sts:
        author = paper.find('i').text
        title = paper.find('b').text
        print(f'{author}\n{title}\n')
        if year in [2013, 2015]:
            abstract = paper.find(style='font-size:11px;').text.strip()
            abstract = cleanAbstract(abstract)
            listaInterna = [year, event, city, STtitle, coordinators, author, title, abstract]
        else: 
            abstract = paper.find(style='display:none;font-size:11px;').text.strip()
            abstract = cleanAbstract(abstract)
            listaInterna = [year, event, city, STtitle, coordinators, author, title, abstract]
        listaFinal.append(listaInterna)

def stList(bs, className, year):
    '''
    Função que raspa a lista de Simpósios Temáticos
    '''
    STBoxe = bs.find('table', class_= className)
    for st in STBoxe:
        try:
            if year == 2021:
                st = st.find('h4')
            else:
                st = st.find('h3')
            STlink = st.find('a')['href']
            reqopen = Request(STlink)
            req = urlopen(reqopen)
            soup = BeautifulSoup(req.read(), 'lxml')
            getAbstract(soup, year, listaFinal)
        except:
            pass

def request (url, dic, year):
    '''
    Função que acessa a URL com urlopen e faz o parse do html com BeautifulSoup
    '''
    reqopen = Request(url, headers=dic)
    req = urlopen(reqopen)
    bs = BeautifulSoup(req.read(), 'lxml')
    stList(bs, 'txtConteudo', year)

def baseUrl(snhYears):
    '''
    Função para definir a URL base para a raspagem dos resumos
    '''
    for year in snhYears:
        url = f'http://snh{year}.anpuh.org/simposio/public'
        request(url,dic, year)

baseUrl(snhYears)
saveDF(listaFinal,date)
