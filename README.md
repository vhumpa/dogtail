TODO lets do something comprehensive



How To Install current version:
- git checkout devel/release-1.0 branch
- python3 -m build
- sudo pip3 install dist/dogtail-1.0-py3-none-any.whl --force-reinstall


Config in 1.0:
- Changing casing to snake_case, but still have backwards compatibility to camelCase.
- Custom keys and values: users can define their own config values in .ini file.
- Type checking: users will get ValueError when trying to set e.g. bool to value defined as float in config.ini.
- Improved getter and setter.


Atspi API references
====================
http://lazka.github.io/pgi-docs/#Atspi-2.0
https://docs.gtk.org/atspi2/index.html


What happened to
- versions
- screenshot in utils
- procedural
- distro
- i18n
- errors
- sessions

No mailing list, no IRC
- use Issues

New documentation

New test suites

New pipeline for testing

sniff is and candidate for someone to take and improve

