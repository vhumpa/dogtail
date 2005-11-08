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
	mkdir -p rpms/{BUILD,RPMS/noarch,SOURCES,SPECS,SRPMS}
	# Create an rpmrc that will include our custom rpmmacros file
	echo "%_topdir `pwd`/rpms/" > rpms/tmp.rpmmacros
	echo "macrofiles: /usr/lib/rpm/macros:/usr/lib/rpm/%{_target}/macros:/usr/lib/rpm/redhat/macros:/etc/rpm/macros.*:/etc/rpm/macros:/etc/rpm/%{_target}/macros:~/.rpmmacros:`pwd`/rpms/tmp.rpmmacros" > rpms/tmp.rpmrc
	# Build using the custom rpmrc in the rpms/ sub-dir
	rpmbuild --rcfile /usr/lib/rpm/rpmrc:/usr/lib/rpm/redhat/rpmrc:`pwd`/rpms/tmp.rpmrc  -ta dist/dogtail-*.tar.gz
	# Move the source and binary RPMs to dist/
	mv rpms/SRPMS/* rpms/RPMS/noarch/* dist/
	rm -rf rpms/

deb:
	fakeroot debian/rules clean
	dpkg-buildpackage -rfakeroot -us -uc

apidocs:
	rm -rf website/doc/*
	#find website/doc -not -type d -not -regex '.*/\.svn/.*' -exec rm {} \;
	happydoc -d website/doc/ -t "Documentation" dogtail && \
	mv website/doc/dogtail/* website/doc/ && \
	rm -rf website/doc/dogtail/

