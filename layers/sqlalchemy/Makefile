PYPATH = $(ARTIFACTS_DIR)/python
# EXCLUDE_DIRS = pip* docutils* setuptools* wheel* coverage* testfixtures* *.egg-info *.dist-info __pycache__ test tests .pyi *.pyc easy_install.py

build-SQLAlchemyLayer:
	mkdir -p "$(PYPATH)"
	python -m pip install -r requirements.txt -t "$(PYPATH)"
	# @echo "Excluindo arquivos desnecessários..."
	# @for pattern in $(EXCLUDE_DIRS); do \
	# 	find "$(PYPATH)" -name "$$pattern" -exec rm -rf {} +; \
	# done
