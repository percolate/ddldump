develop:
	python setup.py develop

undevelop:
	python setup.py develop --uninstall

test:
	flake8 ddldump

clean:
	rm -rf dist/
	rm -rf ddldump.egg-info

release: clean
	python setup.py sdist
	twine upload dist/*
