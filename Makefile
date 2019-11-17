# make file for goquant
project := goquant
ENV := env
ENV_TEST := test
ENV_DEV := development
ENV_PROD := production

$(ENV): $(ENV)/bin/pip
	$(ENV)/bin/pip install --upgrade pip && \
	$(ENV)/bin/pip install -r requirements.txt

install:
	python3 -m virtualenv $(ENV)
	make python-env

clean:
	rm -rf $(ENV)

python-env:
	$(ENV)/bin/pip install --upgrade pip && \
	$(ENV)/bin/pip install -r requirements.txt

research:
	ipython kernel install --name $(ENV)

# run CI 
jenkins:
	make clean
	make install
	RUNTIME_ENV=$(ENV_TEST) make test

test:
	RUNTIME_ENV=test PYTHONPATH=$(ENV)/bin/python:. $(ENV)/bin/py.test -rxs --tb short

lint:
	autopep8 --in-place --recursive --aggressive controller entity handler gateway repository tests
