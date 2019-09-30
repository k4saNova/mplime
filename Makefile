ENV_PATH = $(PWD)/env
VPYTHON = $(ENV_PATH)/bin/python
VPIP = $(ENV_PATH)/bin/pip
VPYTEST = $(ENV_PATH)/bin/pytest
PYTHON = `which python3`

.PHONY: env test
env:
	@ virtualenv $(ENV_PATH) --python=$(PYTHON)
	@ $(VPIP) install -r requirements-dev.txt
	@ $(VPYTHON) setup.py install

test:
	@ $(VPYTEST) test/* --capture=no

install:
	@ $(PYTHON) setup.py install

clean:
	@ rm $(PWD)/build/ $(PWD)/dist/ $(ENV_PATH) -rf

