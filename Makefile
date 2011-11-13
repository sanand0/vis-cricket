COUNTRIES = Australia England India Pakistan New-Zealand South-Africa Sri-Lanka West-Indies

all: $(foreach COUNTRY,$(COUNTRIES),batting-$(COUNTRY)-plain.xhtml batting-$(COUNTRY)-adjusted.xhtml)

batting-%-plain.xhtml: odi_batting.csv template.html
	python D:/ext/vis/vis.py odi_batting.csv template.html "$(subst -, ,$*)" plain > $@

batting-%-adjusted.xhtml: odi_batting.csv template.html
	python D:/ext/vis/vis.py odi_batting.csv template.html "$(subst -, ,$*)" adjusted > $@
