# dogtail *development* Makefile

all: install3 install2

install: clean
	python setup.py build
	python setup.py install --root=$(DESTDIR)


install3: clean3
	python3 setup.py build
	python3 setup.py install --root=$(DESTDIR)

install2: clean2
	python2 setup.py build
	python2 setup.py install --root=$(DESTDIR)

clean:
	rm -rf api_docs/
	rm -f MANIFEST
	rm -rf build dist
	find . -name '*.pyc' -exec rm {} \;

clean2: clean
	python2 setup.py clean

clean3: clean
	python3 setup.py clean

check:
	pep8 --max-line-length=120 dogtail/*.py tests/*.py scripts/* sniff/sniff

test:
	LC_ALL=C nose2 tests

tarball:
	python3 setup.py sdist

rpm: tarball
	# Build using the custom rpmrc in the rpms/ sub-dir
	rpmbuild -tb dist/dogtail-*.tar.gz
	# Move the source and binary RPMs to dist/
	mv ~/rpmbuild/RPMS/noarch/* dist/

srpm: rpm_prep
	# Build using the custom rpmrc in the rpms/ sub-dir
	rpmbuild --rcfile /usr/lib/rpm/rpmrc:/usr/lib/rpm/redhat/rpmrc:`pwd`/rpms/tmp.rpmrc  -ts dist/dogtail-*.tar.gz
	# Move the source and binary RPMs to dist/
	mv rpms/SRPMS/* dist/
	rm -rf rpms/

apidocs: apidocs_html apidocs_pdf

apidocs_html:
	epydoc --html --config epydoc.conf

apidocs_pdf:
	epydoc --pdf --config epydoc.conf
	mv api_docs/api.pdf api_docs/dogtail.pdf

update_apidocs: apidocs
	# Sadly, I'm still the only one who can update the API docs.
	ssh zmc@fedorapeople.org rm -rf \~/public_html/dogtail/epydoc/*
	scp api_docs/*.{html,css,png,pdf} zmc@fedorapeople.org:~/public_html/dogtail/epydoc/
