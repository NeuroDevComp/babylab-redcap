.PHONY: changelog, version-patch

changelog:
	powershell.exe -Command 'git log -1 --pretty=format:"- %s" | Out-File -Append -FilePath ./CHANGELOG.md -Encoding utf8'

venv:
	python -m venv .venv

serve:
	python -m flask --app babylab.app run

debug:
	python -m flask --app babylab.app run --debug

freeze:
	python -m pip freeze -l > requirements.txt 

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -v -p no:cacheprovider

cov:
	python -m pytest -p no:cacheprovider --cov-report html --cov=babylab tests/

publish:
	hatch build
	hatch publish

version-patch:
	hatch version patch
	$version = hatch version
	$versionWithV = "v" + $version
	git add babylab/__about__.py
	git commit -m $versionWithV
	git tag -l "$versionWithV"
	git push

version-minor:
	hatch version minor
	$version = hatch version
	$versionWithV = "v" + $version
	git add babylab/__about__.py
	git commit -m $versionWithV
	git tag -l "$versionWithV"
	git push

version-major:
	hatch version major
	$version = hatch version
	$versionWithV = "v" + $version
	git add babylab/__about__.py
	git commit -m $versionWithV
	git tag -l "$versionWithV"
	git push

docker-build:
	docker build --tag babylab-redcap .

docker-run:
	docker run -d -p 5000:5000 babylab-redcap