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
	py2/bin/pip install pytest
	py2/bin/pip install -r requirements.txt
	# python3
	virtualenv --python=python3 py3
	py3/bin/pip install pytest yapf pylint twine
	py2/bin/pip install -r requirements.txt

fix:
	py3/bin/yapf --in-place -r wake/ tests

lint:
	# TODO: remove -E
	py3/bin/pylint wake/ -E

test2:
	# Testing python2
	PYTHONHASHSEED=42 py2/bin/py.test -vvv

test2-dbg:
	# Testing python2
	PYTHONHASHSEED=42 py2/bin/py.test --pdb -sxvvv

test3:
	# Testing python3
	py3/bin/py.test -vvv

test3-dbg:
	py3/bin/py.test --pdb -sxvvv

test: test3 test2

clean:
	rm -rf py2 py3 dist wake.egg-info .wake/
