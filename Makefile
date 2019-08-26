check: fix lint test
	# SHIP IT!

ship: check
	rm -rf pycheck/ dist/
	virtualenv --python=python3 pycheck
	pycheck/bin/pip install .
	py3/bin/python setup.py sdist
	# run: py3/bin/twine upload dist/*


init:
	# python2
	virtualenv --python=python2 py2
	py2/bin/pip install pytest pyyaml
	py2/bin/pip install -r requirements.txt
	# python3
	virtualenv --python=python3 py3
	py3/bin/pip install pytest pyyaml
	py3/bin/pip install yapf pylint twine
	py3/bin/pip install -r requirements.txt

fix:
	py3/bin/yapf --in-place -r wake/ tests
	jsonnetfmt --in-place --indent 4 --comment-style h \
		$$(find wake -type f \( -name "*.libsonnet" -o -name "*.jsonnet" \))

lint:
	# TODO: remove -E
	py3/bin/pylint wake/ -E

test2:
	# Testing python2
	PYTHONHASHSEED=42 py2/bin/py.test -vvv

test3:
	# Testing python3
	py3/bin/py.test -vvv

testdbg:
	py3/bin/py.test -sxvvv --pdb

test: test3 test2

clean:
	rm -rf py2 py3 dist wake.egg-info .wake/
