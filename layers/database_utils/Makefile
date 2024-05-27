PYPATH = $(ARTIFACTS_DIR)/python

build-DatabaseUtilsLayer:
	mkdir -p "$(PYPATH)"
	python -m pip install -r requirements.txt -t "$(PYPATH)"
	cp src/*.py $(PYPATH)