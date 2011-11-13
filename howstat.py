import sys
import csv
import os.path
from urllib import urlencode
import httplib2
from lxml import etree

BASE = 'http://www.howstat.com'

# Create a cache folder under where this script is located
h = httplib2.Http(os.path.join(os.path.split(__file__)[0], ".cache"))

def get(uri, method="GET", **kwargs):
    head, body = h.request(uri, method, **kwargs)
    return etree.HTML(body)

def players_by_country(country):
    # yields the player details for each player in a country
    # country = AFG|AUS|BAN|BER|CAN|EAF|ENG|HOK|IND|IRE|KEN|MAL|MOR|
    #           NAM|NED|NZL|PAK|SCO|SIN|SAF|SRL|UAE|USA|WAL|WIN|ZIM
    url = BASE + '/cricket/Statistics/Players/PlayerCountryList.asp'
    tree = get(url, 'POST',
        body = urlencode({'cboCountry': country}),
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    )

    for link in tree.findall('.//a'):
        href = link.get('href', '')
        if href.startswith('PlayerOverview'):
            yield {
                'id': href.split('=')[-1],
                'Name': link.text
            }

def player_odi_batting(playerid):
    url = (BASE + '/cricket/Statistics/Players/PlayerProgressBat_ODI.asp?' +
           urlencode({'PlayerId': playerid}))
    tree = get(url)
    table = tree.findall('.//table')
    if len(table) > 2:
        table = table[-2]
        rows = table.findall('tr')
        header = [t.text.strip() for t in rows.pop(0).findall('td')]
        count = 1
        for row in rows:
            v = dict(zip(header, [t.text.strip() for t in row.findall('td')]))
            if 'Runs' in v:
                v['Runs'] = v['Runs'].replace('DNB', '')
                if v['Runs'].find('*') >= 0:
                    v['Runs'] = v['Runs'].replace('*', '')
                    v['Not Out'] = 1
                else:
                    v['Not Out'] = 0

                v['Match'] = count
                count += 1

                yield v

def player_odi_bowling(playerid):
    url = (BASE + '/cricket/Statistics/Players/PlayerProgressBowl_ODI.asp?' +
           urlencode({'PlayerId': playerid}))
    tree = get(url)
    table = tree.findall('.//table')
    if len(table) > 2:
        table = table[-2]
        rows = table.findall('tr')
        header = [t.text.strip() for t in rows.pop(0).findall('td')]
        count = 1
        for row in rows:
            v = dict(zip(header, [t.text.strip() for t in row.findall('td')]))
            if 'Wkts' in v:
                v['Match'] = count
                count += 1
                yield v


def odi_batting(countries, stream):
    out = None
    for country in countries:
        for player in players_by_country(country):
            sys.stderr.write(player['id'] + ': ' + player['Name'] + '\n')
            sys.stderr.flush()
            for match in player_odi_batting(player['id']):
                match['Name'] = player['Name']
                match['Country'] = country
                if out is None:
                    keys = match.keys()
                    out = csv.DictWriter(stream, keys, lineterminator='\n')
                    out.writerow(dict(zip(keys, keys)))
                out.writerow(match)


def odi_bowling(countries, stream):
    out = None
    for country in countries:
        for player in players_by_country(country):
            #sys.stderr.write( 'in Bowling'+ '\n')
            sys.stderr.write(player['id'] + ': ' + player['Name'] + '\n')
            sys.stderr.flush()
            for match in player_odi_bowling(player['id']):
                match['Name'] = player['Name']
                match['Country'] = country
                if out is None:
                    keys = match.keys()
                    out = csv.DictWriter(stream, keys, lineterminator='\n')
                    out.writerow(dict(zip(keys, keys)))
                out.writerow(match)

if __name__ == '__main__':
    odi_batting(sys.argv[1:], sys.stdout)
    odi_bowling(sys.argv[1:], sys.stdout)
