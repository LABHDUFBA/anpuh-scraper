"""
Código para raspagem dos resumos submetidos aos Simpósio nacionais de História da Anpuh entre 2013 e 2019.
Autoria: Eric Brasil (IHL-UNILAB, LABHDUFBA)
"""
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pprint import pprint

dic = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
now = datetime.now()
date = now.strftime("%Y-%m-%d_%H-%M-%S")

print('\nCódigo para raspagem dos resumos submetidos aos Simpósio nacionais de História da Anpuh entre 2013 e 2019.\n'
      'Autoria: Eric Brasil\n')
print('-=-'*30)

snhYears= list()
while True:
    snhYears.append(int(input('Digite o ano do primeiro evento [entre 2013, 2015, 2017 e 2019]que deseja raspar: ')))
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
def saveDF(listaFinal,date):
    df = pd.DataFrame(listaFinal, columns=['Ano', 'Evento', 'Cidade', 'ST', 'Coordenadores', 'Autor(es)/Instituições', 'Título', 'Resumo'])
    df.to_csv(f'resumos_anpuh_{snhList}_{date}.csv')

def getAbstract(bs, year, listaFinal):
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
    if year in [2013, 2015]:
        STContent = bs.find(class_='content-interna')
    else:
        STContent = bs.find(id='conteudo-spacer')                
    STInfos = STContent.find_all('table')
    STtitle = STInfos[0].find('h3').text
    print(STtitle)
    coordinators = STInfos[0].find('b').text
    print(f'Coordenador(es): {coordinators}\n')
    abstracts = STInfos[1].find_all('tr')
    for paper in abstracts:
        author = paper.find('i').text
        title = paper.find('b').text
        if year in [2013, 2015]:
            abstract = paper.find(style='font-size:11px;').text.strip()
        else:
            abstract = paper.find(style='display:none;font-size:11px;').text.strip()
        listaInterna = [year, event, city, STtitle, coordinators, author, title, abstract]
        listaFinal.append(listaInterna)

def stList(bs, className, year):
    STBoxe = bs.find('table', class_= className)
    for ST in STBoxe:
        try:
            ST = ST.find('h3')
            STlink = ST.find('a')['href']
            pprint(STlink)
            reqopen = Request(STlink)
            req = urlopen(reqopen)
            soup = BeautifulSoup(req.read(), 'lxml')
            getAbstract(soup, year, listaFinal)
        except:
            pass

def request (url, dic, year):
    reqopen = Request(url, headers=dic)
    req = urlopen(reqopen)
    bs = BeautifulSoup(req.read(), 'lxml')
    stList(bs, 'txtConteudo', year)

def baseUrl(snhYears):
    for year in snhYears:
        url = f'http://snh{year}.anpuh.org/simposio/public'
        request(url,dic, year)

baseUrl(snhYears)
saveDF(listaFinal,date)
