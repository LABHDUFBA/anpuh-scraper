from urllib.request import Request, urlopen, urlretrieve
from bs4 import BeautifulSoup
import re
import os
import urllib
import pandas as pd
from pprint import pprint

dic = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

snhYears= list()
while True:
    snhYears.append(int(input('Digite o ano do evento [entre 2013, 2015, 2017 e 2019]: ')))
    resp = str(input('Deseja inserir outro ano? [S/N] '))
    if resp in 'Nn':
        break
snhYears.sort()

snhList = str(snhYears)
for r in ",[]":
    snhList = snhList.replace(r,'')
snhList = snhList.replace(' ','_')

listaFinal=[]
def saveDF(listaFinal):
    df = pd.DataFrame(listaFinal, columns=['Ano', 'ST', 'Coordenadores', 'Autor(es)/Instituições', 'Título', 'Resumo'])
    df.to_csv(f'anais-anpuh-resumos-{snhList}.csv')

def getAbstract(bs, year, listaFinal):
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
            print(f'Autor(es): {author}\nTítulo: {title}\nResumo: {abstract}\n')
        else:
            abstract = paper.find(style='display:none;font-size:11px;').text.strip()
            print(f'Autor(es): {author}\nTítulo: {title}\nResumo: {abstract}\n')
        listaInterna = [year, STtitle, coordinators, author, title, abstract]
        listaFinal.append(listaInterna)

def stList(bs, className, year):
    STBoxe = bs.find('table', class_= className)
    for ST in STBoxe:
        try:
            ST = ST.find('h3')
            STlink = ST.find('a')['href']
            STtitle = ST.text
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
        #pasta = os.path.join('Anais  Anpuh', 'resumos')
        #if not os.path.exists(pasta):
        #    os.makedirs(pasta)
        #pastaEvento = os.path.join(pasta, f'SNH_{year}')
        #if not os.path.exists(pastaEvento):
        #    os.makedirs(pastaEvento)
        request(url,dic, year)

baseUrl(snhYears)
saveDF(listaFinal)

