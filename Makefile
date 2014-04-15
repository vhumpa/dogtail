# dogtail *development* Makefile

all:
	python setup.py build

install:
	python setup.py install --root=$(DESTDIR)

clean:
	rm -rf api_docs/
	python setup.py clean
	rm -f MANIFEST
	rm -rf build dist
	
	find . -name '*.pyc' -exec rm {} \;

# Dollar signs must be escaped with dollar signs in variables.
export camelCAPS='[a-z_][a-zA-Z0-9_]*$$'
export StudlyCaps='[a-zA-Z_][a-zA-Z0-9_]*$$'

check:
	pylint --indent-string="    " --class-rgx=${StudlyCaps} --function-rgx=${camelCAPS} --method-rgx=${camelCAPS} --variable-rgx=${camelCAPS} --argument-rgx=${camelCaps} dogtail sniff/sniff examples/*.py recorder/dogtail-recorder scripts/*.py

tarball:
	python setup.py sdist

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
