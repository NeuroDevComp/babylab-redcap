main:
	python -m main

venv:
	python -m venv .venv

serve:
	python -m flask --app babylab.main run

debug:
	python -m flask --app babylab.main run  --debug 

freeze:
	python -m pip freeze -l > requirements.txt 

install:
	python -m pip install -r requirements.txt

test:
	pytest

docker-build:
	docker build --tag babylab-redcap . 

docker-run:
	docker run --rm -it -p 5000:5000 --name babylab-redcap-container babylab-redcap

version-patch:
	hatch version patch
	$VERSION = hatch version
	$TAG = "v$VERSION"
	git add babylab/__about__.py
	git commit -m $TAG
	git tag $TAG main
	git push
	git push --tags
