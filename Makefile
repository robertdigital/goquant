# make file for goquant-trading
project := goquant
ENV := env

$(ENV): $(ENV)/bin/pip
	$(ENV)/bin/pip install --upgrade pip && \
	$(ENV)/bin/pip install -r requirements.txt
	ipython kernel install --name $(ENV)

install: $(ENV)


$(ENV)/bin/pip:
	virtualenv -p python3 env
	$(ENV)/bin/pip install --upgrade pip

test: $(ENV)
	RUNTIME_ENV=test PYTHONPATH=$(ENV)/bin/python:. py.test -rxs --tb short

lint:
	autopep8 --in-place --recursive --aggressive controller entity handler gateway repository tests
