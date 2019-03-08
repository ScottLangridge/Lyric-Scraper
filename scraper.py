from bs4 import BeautifulSoup

import requests
import unicodedata
import os


def main():
    artists = input_from_file()

    for i in range(len(artists)):
        if len(artists[i]) == 1:
            artists[i] = guess_url(artists[i][0])

    count = 1
    for artist in artists:
        print('ARTIST: ' + artist[0] + ' - (' + str(count) + ' of ' +
              str(len(artists)) + ')')
        count += 1

        album_count = 1
        albums = album_links(artist[1])
        for album in albums:
            print('  ALBUM: ' + album[0] + ' - (' + str(album_count) + ' of ' +
                  str(len(albums)) + ')')
            album_count += 1

            song_count = 1
            songs = song_links(album[1])
            for song in songs:
                print('    SONG - (' + str(song_count) + ' of ' +
                      str(len(songs)) + ')')
                song_count += 1

                lyrics = song_lyrics(song)
                save(artist[0], album[0], lyrics[0][1], lyrics[1])


def input_from_file():
    FILENAME = 'input.txt'

    with open(FILENAME, 'r') as f:
        raw = f.readlines()

    artists = []
    out = []
    for line in raw:
        artists.append(line.split(','))
        out.append([])
        for i in artists[-1]:
            out[-1].append(i.strip('\n').strip(' '))

    return out


def scrape(url):
    data_object = requests.get(url)
    content = data_object.text
    return BeautifulSoup(content, features='html5lib')


def guess_url(artist):
    root = 'https://www.lyricsfreak.com/'
    if artist[:4] == 'The ':
        start = 4
    else:
        start = 0
    return [artist, root + artist[start].lower() + '/'
            + artist[start:].lower().replace(' ', '+')]


def save(artist, album, title, lyrics):
    replacements = [(' ', '-'), ('/', '\\')]
    elements = [artist, album, title]
    for i in range(len(elements)):
        for r in replacements:
            elements[i] = elements[i].replace(r[0], r[1])
    artist = elements[0]
    album = elements[1]
    title = elements[2]

    if not os.path.exists('lyrics'):
        os.mkdir('lyrics')
    os.chdir('lyrics')

    if not os.path.exists(artist):
        os.mkdir(artist)
    os.chdir(artist)

    if not os.path.exists(album):
        os.mkdir(album)
    os.chdir(album)

    with open(title + '.txt', 'w+') as f:
        f.write(lyrics)

    os.chdir('../../..')


def album_links(artist_url):
    soup = scrape(artist_url)
    links = soup.find_all('a')

    album_links = []
    for link in links:
        if link.has_attr('href') and '/album/' in link['href']:
            title = link['title'][:-7]
            href = 'https://www.lyricsfreak.com' + link['href']
            album_links.append([uni_to_ascii(title), uni_to_ascii(href)])
    return album_links


def song_links(album_url):
    soup = scrape(album_url)
    links = soup.find_all('a')

    song_links = []
    for link in links:
        if link.has_attr('href') and link.has_attr('title')\
                and '.html' in link['href']:
            song_links.append('https://www.lyricsfreak.com' + link['href'])

    return song_links


def song_lyrics(url):
    soup = scrape(url)
    divs = soup.body.find_all('div')
    text = None
    for div in divs:
        if div.has_attr('class'):
            pass
        if div.has_attr('class') and u'l_title' in div['class']:
            raw = div.get_text()
            meta = (raw.strip()[:-7]).split(' ' + u'\u2013' + ' ')
            meta[1] = meta[1].split('\n')[0][:-7]
            for i in range(len(meta)):
                meta[i] = uni_to_ascii(meta[i])

        elif div.has_attr('class') and u'lyrictxt' in div['class']:
            text = div.get_text().strip()
            text = uni_to_ascii(text)
            break

    if text is None:
        text = 'Lyrics Missing - Likely for licencing reasons'

    return [meta, text + '\n']


def uni_to_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')


main()
