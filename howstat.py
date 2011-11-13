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

def player_stats(path, playerid):
    url = (BASE + '/cricket/Statistics/Players/' + path + '?' +
           urlencode({'PlayerId': playerid}))
    tree = get(url)
    table = tree.findall('.//table')
    if len(table) > 2:
        table = table[-2]
        rows = table.findall('tr')
        header = [td.text.strip() for td in rows.pop(0).findall('td')]
        for row in rows:
            values = [td.text.strip()
                      for td in row.findall('td')]
            yield dict(zip(header, values))

def player_odi_batting(playerid):
    for row in player_stats('PlayerProgressBat_ODI.asp', playerid):
        if 'Runs' in row:
            row['Runs'] = row['Runs'].replace('DNB', '')
            if row['Runs'].find('*') >= 0:
                row['Runs'] = row['Runs'].replace('*', '')
                row['Not Out'] = 1
            else:
                row['Not Out'] = 0

            yield row

def player_odi_bowling(playerid):
    career_balls, career_runs = 0, 0
    for row in player_stats('PlayerProgressBowl_ODI.asp', playerid):
        if 'Wkts' in row and '/' in row['Wkts']:
            # The wickets column looks like this: 3/24 (3 wickets for 24 runs)
            row['Wkts'], row['Runs'] =  row['Wkts'].split('/')

            # #overs isn't available. But E/R = 6*career_runs/career_balls
            career_runs += int(row['Runs'])
            new_career_balls = int(0.5 + 6 * career_runs / float(row['E/R']))
            row['Balls'] = new_career_balls - career_balls
            career_balls = new_career_balls

            yield row

def country_stats(method, countries, stream):
    out = None
    for country in countries:
        for player in players_by_country(country):
            sys.stderr.write(player['id'] + ': ' + player['Name'] + '\n')
            sys.stderr.flush()
            for match in method(player['id']):
                match['Name'] = player['Name']
                match['Country'] = country
                if out is None:
                    keys = match.keys()
                    out = csv.DictWriter(stream, keys, lineterminator='\n')
                    out.writerow(dict(zip(keys, keys)))
                out.writerow(match)

if __name__ == '__main__':
    country_stats(player_odi_batting, sys.argv[1:], sys.stdout)
    country_stats(player_odi_bowling, sys.argv[1:], sys.stdout)
