main:
	python -m main

venv:
	python -m venv .venv

serve:
	python -m flask --app babylab.app run

debug:
	python -m flask --app babylab.main run --debug 

freeze:
	python -m pip freeze -l > requirements.txt 

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -v 
	python -m pytest --cov-report html --cov=babylab tests/

docker-build:
	docker build --tag babylab-redcap . 

docker-run:
	docker run --rm -it -p 5000:5000 --name babylab-redcap-container babylab-redcap
