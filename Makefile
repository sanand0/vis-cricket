all: batting.xhtml

batting.xhtml: ind_odi_batting.csv template.html
	python D:/ext/vis/vis.py ind_odi_batting.csv template.html > $@

ind_odi_batting.csv: howstat.py
	python howstat.py

