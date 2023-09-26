# Makefile
# AWS CDK Python Workshop
#
# Copyright © 2023 djrlj694.dev. All rights reserved.
#
# Faciliates automation for setting up Unix-based systems.
#
# See:
# 1. https://earthly.dev/blog/python-makefile/
# 2. https://www.gnu.org/prep/standards/html_node/Makefile-Conventions.html
# 3. https://www.gnu.org/software/make
# 4. https://www.gnu.org/software/make/manual/html_node/Include.html
# 5. https://www.gnu.org/software/make/manual/make.html
# 6. https://blog.mathieu-leplatre.info/tips-for-your-makefile-with-python.html
# 7. https://medium.com/aigent/makefiles-for-python-and-beyond-5cf28349bf05
# 8. https://web.mit.edu/gnu/doc/html/make_1.html
# 9. https://ricardoanderegg.com/posts/makefile-python-project-tricks/
# 10. https://stackoverflow.com/questions/24736146/how-to-use-virtualenv-in-makefile
# 11. https://venthur.de/2021-03-31-python-makefiles.html

# SECTION: MAKE OPTIONS ===================================================== #

.ONESHELL:

SHELL = /bin/bash

export

# SECTION: INCLUDES ========================================================= #

-include .env

# SECTION: EXTERNAL VARIABLES =============================================== #

AWS_PROFILE ?= default

CDK ?= cdk
GIT ?= git
PYTEST ?= pytest
PYTHON ?= python

# SECTION: INTERNAL VARIABLES =============================================== #

### Special Characters ###

# C-style octal code representing an ASCI escape character.
esc := \033

### ANSI Escape Sequences ###

# Setting the text intensity/emphasis of STDOUT.
reset := $(esc)[0m
bold := $(esc)[1m
dim := $(esc)[2m

# Setting the text color of STDOUT.
fg_red := $(esc)[0;31m
fg_green := $(esc)[0;32m
fg_yellow := $(esc)[1;33m
fc_cyan := $(esc)[0;36m

### Python ###

# make it work on windows too
ifeq ($(OS), Windows_NT)
    pip=.venv/Scripts/pip
    python=python
else
    pip=.venv/bin/pip
    python=python3
endif

# SECTION: MACROS =========================================================== #

# Prints a message to STDOUT when a makefile target is executed.
define msg
@printf "$(fg_cyan)$(bold)$(1)...$(reset)\n"
endef

# SECTION: PHONY TARGETS ==================================================== #

### General ###

# Force the default target execution sequence to display the online help if no
# target is specified in the command line following "make".

.PHONY: all
all: help

## clean: Removes all temporary project artifacts.
.PHONY: clean
clean: cdk-clean python-clean
	$(call msg,Removing all temporary project artifacts)
	@rm -rf tmp

## install: Completes all initialization activities.
.PHONY: init
init: .env
	$(call msg,Completing all initialization activities)

## test: Runs tests.
.PHONY: test
test: clean python-test
	$(call msg,Testing key makefile targets)

## update: Pulls latest changes to project.
.PHONY: update
update:
	$(call msg,Pulling latest changes to project)
	@$(GIT) pull --all

### AWS ###

## cdk: Deploys an AWS CDK stack.
.PHONY: cdk
cdk:
	AWS_PROFILE=$(AWS_PROFILE) $(CDK) synth
	$(PYTEST)
	AWS_PROFILE=$(AWS_PROFILE) $(CDK) bootstrap
	AWS_PROFILE=$(AWS_PROFILE) $(CDK) deploy

## cdk-clean: Removes all AWS CDK artifacts.
.PHONY: cdk-clean
cdk-clean:
	@rm -fr cdk.out

### Python ###

## python-clean: Removes all Python artifacts.
.PHONY: python-clean
python-clean: python-clean-build python-clean-pyc python-clean-test
	@rm -fr .venv
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

# python-clean-build: Removes Python build artifacts.
.PHONY: python-clean-build
python-clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

# python-clean-pyc: Removes Python caches artifacts.
.PHONY: python-clean-pyc
python-clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
	@find . -name '.mypy_cache' -exec rm -rf {} +

# python-clean-test: Removes Python test and coverage artifacts
.PHONY: python-clean-test
python-clean-test:
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/
	@rm -fr .pytest_cache

## python-dist: Builds Python source and wheel package.
.PHONY: python-dist
python-dist:
	@$(python) setup.py sdist
	@$(python) setup.py bdist_wheel
	@ls -l dist

## python-install: Installs Python package to active Python's site-packages.
.PHONY: python-install
python-install:
	@$(python) setup.py install

# python-venv: Runs Python unit test suites.
.PHONY: python-test
python-test:
	@$(python) --version
	@$(PYTEST)

# python-venv: Creates Python virtual environment.
.PHONY: python-venv
python-venv: .venv/bin/activate requirements.txt requirements-dev.txt
	. .venv/bin/activate
	$(pip) install --upgrade -r requirements.txt
	$(pip) install --upgrade -r requirements-dev.txt

# SECTION: FILE TARGETS ===================================================== #

.env:
	$(eval aws_profile = $(shell read -p "AWS Profile: " var; echo $$var))
	@cat etc/.env.template \
	| envsubst >$@
	@chmod 600 $@

.venv/bin/activate:
	$(python) -m venv .venv

requirements.txt:
	touch $@

requirements-dev.txt:
	touch $@
