pep8:
	pep8 --max-line-length=100 --ignore E128,E261,E301,E302,E309,E501 --repeat --show-source --exclude=.tox,dist,docs,build,*.egg .

isort:
	isort -rc .
