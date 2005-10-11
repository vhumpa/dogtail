# dogtail *development* Makefile

all:
	exit 1

clean:
	python setup.py clean
	rm -f MANIFEST
	rm -rf build dist
	
	find . -name '*.pyc' -exec rm {} \;

# Dollar signs must be escaped with dollar signs in variables.
export camelCAPS='[a-z_][a-zA-Z0-9_]*$$'
export StudlyCaps='[a-zA-Z_][a-zA-Z0-9_]*$$'

check:
	pylint --indent-string="	" --class-rgx=${StudlyCaps} --function-rgx=${camelCAPS} --method-rgx=${camelCAPS} --variable-rgx=${camelCAPS} --argument-rgx=${camelCaps} dogtail sniff/sniff examples/*.py

tarball: clean
	python setup.py sdist

rpm: tarball
ifneq ($(id -u),0)
	echo "Attempting to use sudo to build the RPM..."
	sudo rpmbuild -ta dist/dogtail-*.tar.gz
else
	rpmbuild -ta dist/dogtail-*.tar.gz
endif

deb:
	fakeroot debian/rules clean
	dpkg-buildpackage -rfakeroot -us -uc

apidocs:
	rm -rf website/doc/*
	#find website/doc -not -type d -not -regex '.*/\.svn/.*' -exec rm {} \;
	happydoc -d website/doc/ -t "Documentation" dogtail && \
	mv website/doc/dogtail/* website/doc/ && \
	rm -rf website/doc/dogtail/

