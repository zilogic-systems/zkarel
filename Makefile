version = 0.1.0

KAREL_VERSION = $(version)
export KAREL_VERSION

all:

levels: 
	python3 tools/level2json.py

install: levels
	pip3 install --user .

clean:
	rm -f zkarel/levels.json
	rm -fr zkarel.egg-info

distclean: clean
	find . -name "*~" -delete
