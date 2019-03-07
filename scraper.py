from bs4 import BeautifulSoup
import requests
import unicodedata


def scrape(url):
    data_object = requests.get(url)
    content = data_object.text
    return BeautifulSoup(content, features='html5lib')


def song_links(artist_url):
    soup = scrape(artist_url)
    links = soup.find_all('a')

    song_links = []
    for link in links:
        link = str(link)
        if '/lyrics/' in link:
            link = link.split('"')[1]
            link = link.replace('..', 'https://www.azlyrics.com')
            song_links.append(link)
    return song_links


def song_lyrics(url):
    soup = scrape(url)
    lyrics = soup.body.find_all('div')[21].get_text().strip()
    lyrics = unicodedata.normalize('NFKD', lyrics).encode('ascii', 'ignore')
    return lyrics
