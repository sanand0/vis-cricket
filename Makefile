all: batting-plain.xhtml batting-adjusted.xhtml

batting-%.xhtml: odi_batting.csv template.html
	python D:/ext/vis/vis.py odi_batting.csv template.html IND $* > $@

odi_batting.csv: howstat.py
	python howstat.py AUS ENG IND NZL PAK SAF SRL WIN > $@

