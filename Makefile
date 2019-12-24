# make file for goquant
project := goquant
ENV := env
ENV_TEST := test
ENV_DEV := development
ENV_PROD := production

UNIT_TEST := unit
INTEGRATION_TEST := integration
TEST_LEVEL := unit

LINT_FOLDER := controller entity handler gateway tests

$(ENV): $(ENV)/bin/pip
	$(ENV)/bin/pip install --upgrade pip && \
	$(ENV)/bin/pip install -r requirements.txt

install:
	pip3 install virtualenv
	python3 -m virtualenv $(ENV)
	make python-env

clean:
	rm -rf $(ENV)
	rm -rf .coverage

python-env:
	$(ENV)/bin/pip install --upgrade pip && \
	$(ENV)/bin/pip install -r requirements.txt

research:
	ipython kernel install --name $(ENV)
	pip install jupyter
	jupyter notebook

# run CI 
jenkins:
	make clean
	make install
	make test

test:
	TEST_LEVEL=$(UNIT_TEST) RUNTIME_ENV=$(ENV_TEST) PYTHONPATH=$(ENV)/bin/python:. $(ENV)/bin/py.test --cov-config .coveragerc --cov util --cov controller --cov config --cov entity --cov gateway --cov handler -rxs --tb short
	@echo 'NOTE: integration test is skipped, please run `make test_all` full test before submit'

test_all:
	TEST_LEVEL=$(INTEGRATION_TEST) RUNTIME_ENV=$(ENV_TEST) PYTHONPATH=$(ENV)/bin/python:. $(ENV)/bin/py.test --cov-config .coveragerc --cov util --cov controller --cov config --cov entity --cov gateway --cov handler -rxs --tb short

lint:
	pip install flake8
	pip install autopep8
	# stop the build if there are Python syntax errors or undefined names
	#flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 $(LINT_FOLDER) --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	autopep8 --in-place --recursive --aggressive $(LINT_FOLDER)
