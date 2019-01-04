version = $(shell cat version.txt)

all: levels

sdist: levels
	python3 setup.py sdist

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
	python setup.py clean
	rm -f zkarel/levels.json
	rm -fr build-deb
	rm -f *.deb

distclean: clean
	find . -name "*~" -delete
	rm -fr dist
