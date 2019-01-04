version = 0.1.0

KAREL_VERSION = $(version)
export KAREL_VERSION

all: levels

deb: levels
	rm -fr build-deb
	mkdir build-deb
	python3 setup.py install --root=build-deb --install-layout=deb
	fpm			 		\
		-t deb -s dir -C build-deb	\
		-n zkarel -v $(version)		\
		-a all				\
		-d python3			\
		--description 'A environment for learning programming.' \
		.

levels: 
	python3 tools/level2json.py

install: levels
	pip3 install --user .

clean:
	rm -f zkarel/levels.json
	rm -fr zkarel.egg-info
	rm -fr build-deb
	rm -fr build
	rm -f *.deb

distclean: clean
	find . -name "*~" -delete
