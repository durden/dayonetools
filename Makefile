reinstall:
	pip uninstall dayonetools
	pip install .

upload_test_dist:
	python setup.py register -r pypi-test
	python setup.py sdist upload -r pypi-test

install_test_dist:
	# Must install the requirements separately b/c they aren't
	# available on test server
	pip install python-dateutil
	pip install pytz
	pip install -i https://testpypi.python.org/pypi dayonetools

test_install:
	pip install dayonetools
	dayonetools -h
