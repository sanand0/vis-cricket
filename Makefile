COUNTRIES = AUS ENG IND NZL PAK SAF SRL WIN World

all: $(foreach COUNTRY,$(COUNTRIES),batting-$(COUNTRY)-plain.xhtml batting-$(COUNTRY)-adjusted.xhtml)

batting-%.xhtml: odi_batting.csv template.html
	python D:/ext/vis/vis.py odi_batting.csv template.html $* > $@

odi_batting.csv: howstat.py
	python howstat.py $(COUNTRIES) > $@

