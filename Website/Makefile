DESTHOST=yourname@example.com
DESTTOP=yourname/public
DESTDIR=CodePlugORama

GENERATED_HTML = index.html help.html

all:	${GENERATED_HTML}

index.html: index.ezt

# Generating the index file is a two-step process. First, index.md is
# processed through a markdown processor to generate index.ezt. Then a
# custom tool reads a config file to convert the .ezt file to index.html.
# If you're not familiar with EZT, a copy is included under Tools and it's
# a super simple and useful macro processor.
#
# The markdown processor is non-standard, so markdown.ezt is checked into git
# so you don't have to regenerate it.

index.html: index.ezt
	Tools/genhtml.py config.txt $< > $@

%.html:	%.md Makefile header.html trailer.html
	markdown.py -i $< -o $@ -T "Code Plug O'Rama" -H header.html -t trailer.html

%.ezt:	%.md Makefile header.html trailer.html
	markdown.py -i $< -o $@ -T "Code Plug O'Rama" -H header.html -t trailer.html

upload:	all *.css *.js
	rsync -avzL --exclude-from=EXCLUDES ./ ${DESTHOST}:${DESTTOP}/${DESTDIR}
	cd ../Tools; rsync -avzL --exclude-from=EXCLUDES --delete-excluded ./ ${DESTHOST}:${DESTTOP}/${DESTDIR}/Tools
	cd ../Sources; rsync -avzL ./ ${DESTHOST}:${DESTTOP}/${DESTDIR}/Sources

clobber:
	rm ${GENERATED_HTML}

server:
	python3 -m http.server --cgi
