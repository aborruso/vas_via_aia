#-------------------------------------------------------------------------------
# Name:        module4
# Purpose:
#
# Author:      giuli
#
# Created:     15/09/2023
# Copyright:   (c) giuli 2023
# Licence:     <your licence>
# nella riga 239 inserire l'url del sito risultato della ricerca per territorio dal sito del ministero
# nella riga 242 scrivere il nome del file di output con il path
# nella riga 252 inserire il numero di pagine del sito del ministero, risultato della ricerca, aumentato di una
#-------------------------------------------------------------------------------
def main():
    pass

if __name__ == '__main__':
    main()

import re
import requests
from bs4 import BeautifulSoup
import csv
from dateutil import parser

# Funzione per estrarre i dati, inclusi i link, dalla tabella
def extract_table(page_url):
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Trova la tabella nel codice HTML
        table = soup.find('table')

        if table:
            # Esegui l'elaborazione dei dati della tabella qui
            rows = table.find_all('tr')
            for row in rows:
                # Estrarre i dati dalle celle della riga
                cells = row.find_all(['td', 'th'])
                row_data = [cell.text.strip() for cell in cells]

                # Trova i due link (se presenti) nella riga
                links = row.find_all('a', href=True)
                link_urls = [link['href'] for link in links]
                row_data.extend(link_urls)

                # Verifica se la riga contiene dati e non è l'intestazione delle colonne
                if any(row_data) and row_data != ['Progetto', 'Proponente', 'Procedura', 'Info', 'Doc']:

                    # Rimuovi le virgole all'interno del campo "Progetto" e sostituiscile con un punto
                    progetto = row_data[0].replace(',', '.').replace(';', '.').replace('"','')

                    # Aggiungi una colonna "stato procedura" qui
                    stato_procedura = get_stato_procedura(row_data[5])  # Supponendo che il link sia nella sesta colonna

                    # Aggiungi una colonna "id" qui
                    id = get_id_from_link(row_data[6])  # Supponendo che il link_doc sia nella settima colonna

                    # Aggiungi una colonna "scadenza osservazioni" qui
                    scadenza_osservazioni = get_scadenza_osservazioni(row_data[5])  # Supponendo che il link_Info sia nella quinta colonna
                    presentazione_istanza = get_avvio(row_data[5])
                    province=get_province(row_data[5])
                    comuni=get_comuni(row_data[5])
                    regioni=get_regioni(row_data[5])
                    tipo=get_tipo(row_data[5])
                    row_data = [progetto] + row_data[1:]  # Sostituisci il campo "Progetto" con il valore corretto
                    row_data.append(stato_procedura)
                    row_data.append(id)
                    row_data.append(scadenza_osservazioni)
                    row_data.append(presentazione_istanza)
                    row_data.append(province)
                    row_data.append(comuni)
                    row_data.append(regioni)
                    row_data.append(tipo)


                    yield row_data

    else:
        print(f"Errore {response.status_code}: Impossibile accedere a {page_url}")

# Funzione per ottenere lo "stato procedura" da un URL
def get_stato_procedura(url):
    if not url:
        return ''  # Restituisci una stringa vuota se l'URL è vuoto

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tag = soup.find_all('td', colspan="5")
        return tag[-1].get_text().strip()
    except Exception as e:
        print(f"Errore durante l'accesso a {url}: {e}")
        return ''  # Gestione degli errori restituendo una stringa vuota

# Funzione per estrarre l'id dal link_doc
def get_id_from_link(link):
    if not link:
        return ''  # Restituisci una stringa vuota se il link è vuoto

    try:
        # Dividi il link utilizzando il carattere '\' e prendi l'ultima parte
        id = link.split('/')[-1].strip()
        return id
    except Exception as e:
        print(f"Errore nell'estrazione dell'id dal link: {e}")
        return ''  # Gestione degli errori restituendo una stringa vuota

# Funzione per ottenere la "Scadenza presentazione osservazioni" da un URL Info

def get_scadenza_osservazioni(url):
    if not url or not url.startswith('http'):
        return ''  # Restituisci una stringa vuota se l'URL è vuoto o non ha uno schema valido

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tag = soup.find('strong', class_='evidenza')
        date_text = tag.get_text().strip()                        #.get_text().strip() consente di restituire il contenuto all'interno del tag
        date_obj = parser.parse(date_text, dayfirst=True)
        formatted_date = date_obj.strftime('%Y-%m-%d')  # Formato 'YYYY-MM-DD'
        return formatted_date

    except Exception as e:
        print(f"Errore durante l'accesso a {url}: {e}")
        return ''  # Gestione degli errori restituendo una stringa vuota


##def get_avvio(row_data):
##    # Cerca direttamente il testo 'Data presentazione istanza:' nei dati della riga
##    label = 'Data presentazione istanza:'
##    for value in row_data:
##        if label in value:
##            # Estrai la data dal testo
##            data_presentazione = value.replace(label, '').strip()
##            date_obj = parser.parse(data_presentazione, dayfirst=True)
##            formatted_date = date_obj.strftime('%Y-%m-%d')  # Formato 'YYYY-MM-DD'
##            return formatted_date
##
##    return ''  # Restituisci una stringa vuota se non trovi la data di presentazione

url = 'https://va.mite.gov.it/it-IT/Oggetti/Info/6879'


def get_avvio(url):
    if not url or not url.startswith('http'):
        return ''  # Restituisci una stringa vuota se l'URL è vuoto o non ha uno schema valido

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Trova l'elemento HTML che contiene la data di presentazione
        data_presentazione_element = soup.find('td', text='Data presentazione istanza:')

        if data_presentazione_element:
        # Estrai la data dal contenuto dell'elemento
            data_presentazione = data_presentazione_element.find_next('td').text.strip()
            date_obj = parser.parse(data_presentazione, dayfirst=True)
            formatted_date = date_obj.strftime('%Y-%m-%d')  # Formato 'YYYY-MM-DD'
        return formatted_date

    except Exception as e:
        print(f"Errore durante l'accesso a {url}: {e}")
        return ''  # Gestione degli errori restituendo una stringa vuota



def get_province(url):
    if not url or not url.startswith('http'):
        return ''  # Restituisci una stringa vuota se l'URL è vuoto o non ha uno schema valido

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')


        # Cerca il testo che inizia con "Province:" seguito da uno spazio e poi cattura il nome della provincia
        province_pattern = re.compile(r'Province:\s*([\w\s]+)')



        # Cerca all'interno degli elementi <p>
        for p in soup.find_all('p'):
            match = province_pattern.search(p.get_text())

            if match:
                provincia = match.group(1)
                break
        else:
            provincia = None

        if provincia:
            return provincia
        else:
            return 'Informazioni sulla provincia non trovate'


    except Exception as e:
        print(f"Errore durante l'accesso a {url}: {e}")
        return ''  # Gestione degli errori restituendo una stringa vuota


def get_comuni(url):
    if not url or not url.startswith('http'):
        return ''  # Restituisci una stringa vuota se l'URL è vuoto o non ha uno schema valido

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')


        # Cerca il testo che inizia con "Province:" seguito da uno spazio e poi cattura il nome della provincia
        comuni_pattern = re.compile(r'Comuni:\s*([\w\s,]+)')



        # Cerca all'interno degli elementi <p>
        for p in soup.find_all('p'):
            match = comuni_pattern.search(p.get_text())

            if match:
                comuni = match.group(1)
                break
        else:
            comuni = None

        if comuni:
            return comuni
        else:
            return 'Informazioni sui comuni  non trovate'


    except Exception as e:
        print(f"Errore durante l'accesso a {url}: {e}")
        return ''  # Gestione degli errori restituendo una stringa vuota

def get_regioni(url):
    if not url or not url.startswith('http'):
        return ''  # Restituisci una stringa vuota se l'URL è vuoto o non ha uno schema valido

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')


        # Cerca il testo che inizia con "Province:" seguito da uno spazio e poi cattura il nome della provincia
        regioni_pattern = re.compile(r'Regioni:\s*([\w\s,]+)')



        # Cerca all'interno degli elementi <p>
        for p in soup.find_all('p'):
            match = regioni_pattern.search(p.get_text())

            if match:
                regioni = match.group(1)
                break
        else:
            regioni = None

        if regioni:
            return regioni
        else:
            return 'Informazioni su regioni non trovate'


    except Exception as e:
        print(f"Errore durante l'accesso a {url}: {e}")
        return ''  # Gestione degli errori restituendo una stringa vuota

def get_tipo(url):
    if not url or not url.startswith('http'):
        return ''  # Restituisci una stringa vuota se l'URL è vuoto o non ha uno schema valido

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')


        # Cerca il testo che inizia con "Province:" seguito da uno spazio e poi cattura il nome della provincia
        tipo_pattern = re.compile(r'Tipologia di opera:\s*([\w\s,]+)')



        # Cerca all'interno degli elementi <p>
        for p in soup.find_all('p'):
            match = tipo_pattern.search(p.get_text())

            if match:
                tipo = match.group(1)
                break
        else:
            tipo = None

        if tipo:
            return tipo
        else:
            return 'Informazioni su tipologia non trovate'


    except Exception as e:
        print(f"Errore durante l'accesso a {url}: {e}")
        return ''  # Gestione degli errori restituendo una stringa vuota

# URL della pagina da cui iniziare lo scraping
base_url = 'https://va.mite.gov.it/it-IT/Ricerca/ViaTerritorio?__RequestVerificationToken=yIC73J1WR3aeNEg6Nz_q4eJSTST8uwNamEaCzaT84o0Q6-zdEEc0keSC3nkp6I1s38D0J1azt79gP1i3HIsnH08_Cga2LzA9BYLAYcBWywfMwEYm0llsn2uLDkm16gzxXUkPTnDR7U6IAgEURpyy6yResXcX5Mxxp0Wd97KAn_U1&macroTipoOggettoID=1&x=11&y=6&pagina={}'

# Apri il file CSV una volta fuori dal ciclo for per non sovrascrivere
with open('C:/Users/giuli/Dropbox/EOLICO 2023/progetti_italia.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=";")

    # Scrivi l'intestazione del CSV
    header = ['Progetto', 'Proponente', 'Procedura', 'Info', 'doc', 'link_Info', 'link_doc', 'stato procedura', 'id', 'scadenza osservazioni','avvio istanza','province','comuni','Regioni','Tipologia']
    csv_writer.writerow(header)  # Personalizza con i nomi delle colonne desiderati

    # Esegui il ciclo attraverso le pagine  AGGIORNARE IL NUMERO DELLE PAGINE WEB RISULTATO DELLA RICERCA + 1 !!!!
    for page_number in range(1, 526):
        page_url = base_url.format(page_number)
        is_first_page = (page_number == 1)
        for row_data in extract_table(page_url):
            csv_writer.writerow(row_data)
