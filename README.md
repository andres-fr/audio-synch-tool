# python3-template   [![Build Status](https://travis-ci.org/andres-fr/python3-template.svg?branch=master)](https://travis-ci.org/andres-fr/python3-template) [![PyPI version](https://badge.fury.io/py/dummypackage-dummyname.svg)](https://badge.fury.io/py/dummypackage-dummyname) [![Documentation Status](https://readthedocs.org/projects/python3-template/badge/?version=latest)](https://python3-template.readthedocs.io/en/latest/?badge=latest)


Dummy Python3 project providing structure for development, unit testing, runtime/memory benchmarking, PEP8 check, [autodocumentation](https://python3-template.readthedocs.io), and deployment to [PyPI](https://pypi.org/project/dummypackage-dummyname) and [GitHub Releases](https://github.com/andres-fr/python3-template/releases), automated via [Travis CI](https://travis-ci.org/andres-fr/python3-template) (online and locally).


* The actual code is to be developed in the `dummypackage` library, and used in an application like `dummyapp.py`, which can be run with `python dummyapp.py`. **To ensure proper function of the tools, all subdirectories must include an `__init.py__` file**.

* The unit tests are developed in the `utest` directory. They can also be arbitrarily nested, but also **must include an `__init.py__` file in each test directory**.

* Reports for runtime and memory benchmarks can be generated into `timebenchmark` and `memorybenchmark` respectively.

* Autodocs are also generated using `sphinx` into the `docs` directory, in PDF as well as HTML (which can be deployed [online](https://python3-template.readthedocs.io)).

* A `setup.py` script to create an OS-agnostic package into `dist` is provided, as well as functionality to keeping track of versioning and deploying into git releases and PyPI.

* All these tasks can be performed manually as explained later on, and also are automated via Travis CI as it can be seen in the `.travis.yml` file, and the `ci_scripts` directory, for maximal efficiency and efficacy.


This readme has been developed for Ubuntu-like systems, but with the intention of it being as much OS-agnostic as possible (all Python examples should transfer well to other systems). Also note that this has been tested for Python 3 only, make sure that your `python` command invokes a Python 3 binary (or that you adapt the exmples presented here).


# Dependencies:

Some general dependencies are listed under the `addons` tag in the `.travis.yml` file. See `requirements.txt` for the python-specific dependencies. Also, if not using `conda`, add this line to your .bashrc to allow executing binaries installed with `pip --user`:

```bash
export PATH=${PATH}:$HOME/.local/bin
```

# Unit Testing:

All unit test files must fulfill the following requirements (see the examples for more details):

* They have to be in the `utest` directory
* Their name has to end in `_test.py` (although this is customizable)
* They import functionality from the package like this: `from dummypackage.foo_module import Foo`
* They import functionality from each other like this: `from .foo_test import FooTestCaseCpu`
* They import `unittest` and extend `unittest.TestCase` classes
* All test method names from the extended unittest classes begin with `test` (also customizable)
* Nested directories are allowed. However, **each test directory has to contain an empty `__init__.py` file**

If these conditions are met, all the tests can be run from the CLI or within Python.

**Note**: the `utest` directory includes a special test case, `tautology.py` which should always pass and can be used to ensure that the testing facilities work correctly. Its name doesn't end in `_test.py`, so it doesn't get included in the ordinary tests and has to be called explicitly.

### Run from CLI:

```bash
# run all existing tests
python -m unittest discover -s utest -t . -p "*_test.py" -v
# Run individual test modules (from the repo root dir)
python -m unittest utest/foo_test.py -v
python -m unittest utest/bar_test.py -v
python -m unittest utest/nestedtests/nested_test.py -v
# Run individual classes
python -m unittest utest.foo_test.FooTestCaseCpu -v
python -m unittest utest.nestedtests.nested_test.QuackTestCaseCpu -v
# Run individual methods
python -m unittest utest.bar_test.BarTestCaseCpu.test_inheritance -v
```

### Run within Python:

```python

# run all existing tests and collect results
import utest
results = utest.run_all_tests()
print(results)

# run all tests for a given module and collect results
import utest.foo_test
results = utest.run_module(utest.foo_test);
print(results)

# run for several modules:
import utest
import utest.foo_test as f
import utest.nestedtests.nested_test as n
results = utest.run_modules([f, n]);
print(results)

# run for a single testcase
import utest
from utest.foo_test import FooTestCaseCpu
results = utest.run_testcase(FooTestCaseCpu);
print(results)

# run for several testcases
import utest
from utest.foo_test import FooTestCaseCpu
from utest.bar_test import BarTestCaseCpu
results = utest.run_testcases([FooTestCaseCpu, BarTestCaseCpu]);
print(results)

# run for a single method
import utest
results = utest.run_testmethod("utest.foo_test.FooTestCaseCpu.test_loop");
print(results)

# run for several methods
import utest
results = utest.run_testmethods(["utest.foo_test.FooTestCaseCpu.test_loop",
                                "utest.bar_test.BarTestCaseCpu.test_loop"]);
print(results)
```


# Code Coverage:

Code coverage determines how much of the implemented code do the unit tests go through. Although not particularly sound, it can be used as a way to check that the unit testing relates closely to the developed code. Plus, it is easy to automate.

### From CLI:

The usage is very similar to running with `python`, but prepending `coverage run` instead, and adding a `--source` directory, which contains the actual code pool being inspected:

```
# define the location for the coverage file:
export COVERAGE_FILE=codecoverage/coverage`date "+%Y%m%d_%H%M%S"`

# Run whatever you want to run but prepending 'coverage run'
# the --branch flag activates branch coverage (as opposed to statement coverage)
# the -a flag will accumulate the reports
coverage run --source dummypackage --branch -m unittest discover -s utest -t . -p "*_test.py" -v

# Print report on terminal
coverage report -m

# more elaborated XML report:
coverage xml -o $COVERAGE_FILE.xml

# interactive HTML report
coverage html -d $COVERAGE_FILE\_html
firefox $COVERAGE_FILE\_html/index.html
```

### Within Python:

This sample script performs unit testing AND test coverage wthout creating any files (see the script `ci_scripts/utest_with_coverage.py`):

```python

import coverage
import utest

# same as with the CLI. A suffix will be automatically added
COVERAGE_FILE = "codecoverage/coverage"

# wrap the testing with the coverage analyzer:
c = coverage.Coverage(data_file=COVERAGE_FILE, data_suffix=True, branch=True,
                      source=["dummypackage"])
c.start()
test_results = utest.run_all_tests()
c.stop()

# at this point c.save() and c.html_report(outfile=etc) would generate files.
# This instead handles the data within Python, as coverage.CoverageData
percentage = c.report()

print("This script did", test_results.testsRun, "tests in total.")
print("No. of test errors:", len(test_results.errors))
print("No. of test failures:", len(test_results.failures))
print("Code coverage of tests (percentage):", percentage)
```





# CPU Runtime Benchmarking:


### Run and print on terminal, sorted by total time:

```bash
python -m cProfile -s tottime dummyapp.py
```

It can be sorted by any of these:
```
calls (call count)
cumulative (cumulative time)
cumtime (cumulative time)
file (file name)
filename (file name)
module (file name)
ncalls (call count)
pcalls (primitive call count)
line (line number)
name (function name)
nfl (name/file/line)
stdname (standard name)
time (internal time)
tottime (internal time)
```

Sample output:

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      100    1.496    0.015    1.496    0.015 {method 'index' of 'list' objects}
        1    0.023    0.023    0.023    0.023 bar_module.py:15(__init__)
     93/1    0.016    0.000    1.590    1.590 {built-in method builtins.exec}
        1    0.010    0.010    1.590    1.590 dummyapp.py:6(<module>)
       47    0.005    0.000    0.005    0.000 {built-in method marshal.loads}
  229/227    0.004    0.000    0.011    0.000 {built-in method builtins.__build_class__}
```


### Save to file and explore interactively with web browser using `snakeviz`:

```bash
python -m cProfile -o timebenchmark/dummyapp.`date "+%Y%m%d_%H%M%S"` dummyapp.py
# open results in browser using the snakeviz server
snakeviz timebenchmark/dummyapp.20190112_195256
```

### Within Python:

This small snippet prints the results to the terminal and returns some relevant figures (see the script `ci_scripts/runtime_benchmark.py`):

```
import cProfile
import pstats
from io import StringIO

def get_total_time_and_calls(fn, sort_by="time"):
    """
    This function calls the given a parameterless functor while benchmarking
    it via cProfile. A report is printed to the terminal and the tuple
    (n_seconds, n_calls) is returned.
    """
    pr = cProfile.Profile()
    pr.enable()
    fn()
    pr.disable()
    #
    s = StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.strip_dirs().sort_stats(sort_by)
    ps.print_stats()
    print(s.getvalue())
    #
    return ps.total_tt, ps.total_calls

get_total_time_and_calls(lambda: 2+2)
```


# Memory Benchmarking:

This package reports memory usage of the Python process, line-by-line or as a function of time. As with the runtime profiler, there are several ways to run this functionality.


### Decorators:

This way requires to import and use the `@profile` decorator in the desired `def` declarations of your Python files. Unlike the other methods, it has the drawback that it requires to alter or duplicate the source code. To perform the profiling, run the decorated files (see e.g. the `memorybenchmark` directory) with the python interpreter. Sample output:


```
Filename: memorybenchmark/loop_benchmark.py
Line     Mem usage    Increment   Line Contents
================================================
    21     14.6 MiB     14.6 MiB   @profile  # decorator for (https://pypi.org/project/memory-profiler/)
    22                             def do_loop(clss, memsize, loopsize):
    23                                 """
    24                                 Create a Foo instance and loop it.
    25                                 """
    26     14.6 MiB      0.0 MiB       x = clss(memsize)
    27     14.6 MiB      0.0 MiB       x.loop(loopsize)

    21     14.6 MiB     14.6 MiB   @profile  # decorator for (https://pypi.org/project/memory-profiler/)
    22                             def do_loop(clss, memsize, loopsize):
    23                                 """
    24                                 Create a Foo instance and loop it.
    25                                 """
    26     53.3 MiB     38.7 MiB       x = clss(memsize)
    27     53.3 MiB      0.0 MiB       x.loop(loopsize)
```



### Time-based memory usage:

The module provides the `mprof` binary to perform time-based analysis. Calling `mprof run loop_benchmark.py` will generate a `mprofile_TIMESTAMP.dat` file, which can be visualized with `mprof plot`(if pylab/matplotlib is installed) and looks like this:

```
FUNC __main__.do_loop 14.4766 1547322141.5961 14.4766 1547322141.5963
FUNC __main__.do_loop 14.4766 1547322141.5964 14.8281 1547322143.1454
CMDLINE /usr/bin/python dummyapp.py
MEM 1.511719 1547322141.5060
MEM 31.281250 1547322141.6064
MEM 53.195312 1547322141.7067
MEM 53.195312 1547322141.8071
MEM 53.195312 1547322141.9074
MEM 53.195312 1547322142.0078
MEM 53.195312 1547322142.1081
MEM 53.195312 1547322142.2085
```

The available `mprof` commands are:
```bash
mprof run: running an executable, recording memory usage
mprof plot: plotting one the recorded memory usage (by default, the last one)
mprof list: listing all recorded memory usage files in a user-friendly way.
mprof clean: removing all recorded memory usage files.
mprof rm: removing specific recorded memory usage files
```

Further information can be found in the package homepage.

### Within Python:


This small snippet returns memory usage as a function of time (see the script `ci_scripts/runtime_benchmark.py`). Line-by-line analysis using the `LineProfiler` class doesn't seem to be supported by this method, see the first and second approaches for alternatives:

```
from memory_profiler import memory_usage

def fn(times=1000, message="hello!"):
    l = []
    for i in range(times):
        l.append(message)
    for i in range(times**2):
        l.append(message)

usage = memory_usage((fn, (1000, "goodbye")), interval=0.05)
print(usage)

```


# Codestyle Check:

Using it is pretty straightforward: simply call `flake8` or `python -m flake8` in the repository root directory. If any errors are present, the command will print them and return with error status.

Note that some "errors" are actually design decissions. These can be bypassed with the `noqa` directive, like this: `import environment  # noqa: F401`. The `noqa` directives themselves can be ignored by running `flake8 --disable-noqa`.




# Autodoc:

This project provides a script that generates the package's autodocs as HTML and PDF from scratch, using `sphinx` (and `LaTeX` for the PDF). Usage example:

```
python ci_scripts/make_sphinx_docs.py -n dummypackage -a "Dummy Dumson" -f .bumpversion.cfg -o docs -l
```

The docs will be generated into `docs/_build` (they are also being uploaded to the repository as they aren't filtered by `.gitignore`).


Optionally, you can deploy your docs into https://readthedocs.org/ by synchronizing it with your github account. Importing the repository should be straightforward: the page will automatically find your `conf.py` and generate the docs. The docs homepage of the project should provide a badge like the one at the top of this README and a link to the online docs. Note that the advertisment can be removed in the "Admin" tab. This repo's docs are being deployed to https://python3-template.readthedocs.io

By default, it will provide two versions of the doc: `latest` and `stable`. See this link about versioning in readthedocs: [here](https://docs.readthedocs.io/en/stable/versions.html).


### From CLI:

The Python script provided follows closely what a CLI user would do with something like the following bash script:


```
# usage example: ./make_sphinx_docs "compuglobalhypermeganet" "Homer Simpson"
# ONLY CALLABLE FROM REPO ROOT

PACKAGE_NAME=$1
AUTHOR=$2
VERSION=`grep "current_version" .bumpversion.cfg | cut -d'=' -f2 | xargs`
CONF_PY_PATH="docs/conf.py"
rm -rf docs/*

sphinx-quickstart -q -p "$PACKAGE_NAME" -a "$AUTHOR" --makefile --batchfile --ext-autodoc --ext-imgmath --ext-viewcode --ext-githubpages  -d version="$VERSION" -d release="$VERSION" docs/

# the following is needed to change the html_theme flag?
sed -i '/html_theme/d' "$CONF_PY_PATH" # remove the html_theme line
sed -i '1r ci_scripts/sphinx_doc_config.txt' "$CONF_PY_PATH" # add the desired config after line 1
echo -e "\nlatex_elements = {'extraclassoptions': 'openany,oneside'}" >> "$CONF_PY_PATH" # override latex config at end of file to minimize blank pages

# cleanest way to allow apidoc edit index.rst without altering conf.py?
rm docs/index.rst
sphinx-apidoc -F "$PACKAGE_NAME" -o docs/

make -C docs clean && make -C docs latexpdf && make -C docs html
```




# Versioning, Build and Deploy:


### Tagging:

Once we reach a given milestone, we can label that specific commit with a version tag (like `v1.0.13`). The basics are discussed here: `https://git-scm.com/book/en/v2/Git-Basics-Tagging`. Especially, **note that tags have to be explicitly included in the push**: `git push --follow-tags`, otherwise, they won't be sent to the server. If you want this to be the default behaviour (as assumed in this project), call `git config --global push.followTags true`, after that every regular `git push` will also push all the valid existing tags.

There are different ways of handling the tag system, the `git` CLI and `gitpython` being very popular among them. Since we want here very specific functionality, we use the `bump2version` third-party library: It allows to automatically increment and set the version tag following semantic versioning (see `https://semver.org/`), which is highly encouraged. It works as follows:

* The `.bumpversion.cfg` file holds the current version and the configuration.
* Calling `bump2version <ADVANCE>` will automatically update the version in the `.bumpversion.cfg` and other specified files, and add the corresponding tag to the git repo. The `<ADVANCE>` parameter can be either **major**, **minor**, or **patch**.

So we just need to start our repo by setting the desired version in the `.bumpversion.cfg` file (usually `0.1.0`), and then commit normally. The process of adding a tag will be something like:

1. Once a milestone is reached, **UPDATE THE `CHANGELOG.md` FILE** with the changes since last version. To maintain an optimal changelog, see `https://keepachangelog.com`. 
  * Ideally, you have kept an `Unreleased` section at the top that you can easily name into the upcoming release.  Added for new features.
  * The main tokens to list are `added, changed, deprecated, removed, fixed, and security`.
  * State clearly and extensively the deprecations and things that will break backward compatibility.
  * Follow semantic versioning for each tag, and add a date to it.
2. Make sure you saved all files and commited to avoid `Git working directory is not clean` error. Also make sure that all specified files in the `.bumpversion.cfg` file exist (e.g. `docs/conf.py`)
3. Call `bump2version <LABEL>` with the corresponding increment label: `major, minor or patch`.
4. `git push` to see the changes! Depending on your branch, this will trigger a Travis build/deploy.


Note that the `ci_scripts/bumpversion_utils.py` script provides some functionality to interact with bumpversion within Python (like e.g. getting the current version). As a quickfix from CLI, the following would work:
```
version=`grep "current_version" .bumpversion.cfg | cut -d'=' -f2 | xargs`
```


### Build and Local Install:

The `setup.py` script will build the package in *source dist* (`sdist`) and *wheel* forms. The package will be in the `dist` directory, and some files will be generated into the `build` directory too. **Important**: remember to adapt the variables in the `setup` function call to your repo's needs (except `version`, which as we seen is handled by `bump2version`).

```
# optionally clean cache to prevent side effects
python setup.py clean --all
rm -r *.egg-info
# package the software
python setup.py sdist bdist_wheel
# now something like this will install the package locally:
pip install dist/dummypackage_dummyname-0.0.1-py3-none-any.whl
# this will update it
pip install -U dist/dummypackage_dummyname-0.0.1-py3-none-any.whl
# and this will remove it:
pip uninstall dist/dummypackage_dummyname-0.0.1-py3-none-any.whl
```

Note that in principle it is not necessary to build the package manually if you have automated the deployment via Travis.

### GitHub Release:

We saw that tags get automatically tracked by GitHub. But for each release, we want to add two things to this default behaviour:

1. Specify a changelog
2. Pip-installable package in [wheel](https://pythonwheels.com/) format.

This can be performed manually via browser in the GitHub webpage, and also via CLI as explained in the [GitHub API](https://developer.github.com/v3/repos/releases/).

Note that in principle it is not necessary to deploy manually if you have automated the deployment via Travis.

### PyPI Release:


The built package can also be released to *PyPI*, a popular global repository for Python packages. The following command uploads then everything in the `dist` directory. You will need to provide your *PyPI* credentials (make a user if you don't have one):

```
twine upload dist/*
```

Note that in principle it is not necessary to deploy manually if you have automated the deployment via Travis.




# Travis CI:


### Intro:

In the context of of CD/CI, a git repository (or any other similar object to automatize tasks on) is regarded as a **material**, with its specific set of **trigger actions** (e.g. commit or pull request in a git repo, or certain API requests in a custom REST system). It probably helps to think of materials as *classes*, and the actions as their *methods*.

For each of those actions, a **CD/CI pipeline** may be defined, which will be executed by the CD/CI system upon trigger by some event. Depending on the CI system, the pipelines allow some complexity like branching, but it is best practice to keep them as simple as possible.

Although different materials have different sets of actions, the spirit is in general similar, in what is known as CI. [Quoting](https://github.com/mbonaci/mbo-storm/wiki/Integrate-Travis-CI-with-your-GitHub-repo):

> "Continuous Integration is the umbrella for various techniques and practices that every self-respecting software project should employ:
> 
> * **Build automation** - every commit/push to an scm repo automatically triggers a new build (anything in the master branch is deployable)
> * **Test automation** - tests are evaluated as integral part of the build process (that's old news, right?)
> * **SCM integration** - primarily to facilitate build automation, but also to be able to report on issues, versions, milestones, ...
> * **Project management integration** - Basecamp, Campfire, Acunote and other PM tools (people, tasks, schedules, ...)
> * **Project Dashboard** - everything is out in the open (generally without any read access restrictions, making it available to all interested parties)



### Travis and this repo:

* https://docs.travis-ci.com
* https://docs.travis-ci.com/user/languages/python/

Travis is a CI/CD tool that can be easily linked to a GitHub account for free, and managed through a `travis.yaml` file present at the repo's root (More info: https://docs.travis-ci.com/user/languages/python/). The goal for this repository is to trigger Travis after each **commit** to master, to perform the following tasks:

1. Run in parallel:
   1. Check coding style with flake
   2. Check that the tautology is true
   3. Check that all unit tests are passing
   4. Check that code coverage ratio is above a number
   5. Check that running a given routine never surpasses a certain memory usage
   6. Check that running a given routine never exceedes a certain duration

2. If all checks success, build the docs and `dummypackage` into our desired architectures.

3. Deploy package in a way that can be installed via `pip`+ repo link


For that, Travis implements two basic concepts, **stages** and **jobs**: A stage is a group of jobs that are allowed to run in parallel. However, each one of the stages runs one after another, and will only proceed if all jobs in the previous stage have passed successfully. If one job fails in one stage, all other jobs on the same stage will still complete, but all jobs in subsequent stages will be canceled, and the build fails.

Each job can be mapped to a "script", which is a call to a program. If the script returns a nonzero status, deployment is considered a failure, and the build will be marked as “errored”.

By default, Travis starts a new virtual machine **from scratch for every single job**. All the required dependencies have to be installed prior to running the jobs. This can take a while, so it is helpful to design the CI pipeline in a way that minimizes overhead. Some of the dependencies can be shared across jobs using the `cache` keyword. Additionaly, the file cleanup that happens prior to some tasks can be also skipped.




### Steps:

1. sync your GitHub account with Travis, and allow access etc to your repositories. Finally, "activate" the desired repo in Travis. You should see the typical `[build | failing]` badge. Click on it and copy the markdown link into the main `README` of the repo, as shown on the top of this file.

2. In your GitHub `activated_repo->settings->webhooks`, select which events you want to notify to Travis. In our case we will activate **commits** and **pull requests**. Any time any of these happens, GitHub will send a request to Travis with all the infos involved.

3. Now both sides know about each other, make sure you understand the `.travis.yml` file and customize it as desired.

4. For deployment, Travis will need your user credentials. As it wouldn't be safe to distribute your passwords in plain text, Travis offers you the possibility of encrypting them. In this project, we will need credentials for **PyPI** and **GitHub**:



#### GitHub releases config:

Travis can be configured to upload to GitHub releases by running `travis setup releases`. If you do this yourself, be careful because **this will reformat the `travis.yml` file**, deleting all comments and blank lines (although the functionality won't be affected). A temporary backup will help with this.

In the repo root, run `travis setup releases` and follow the steps:

1. Confirm repo name
2. Provide GitHub credentials
3. Deploy only from ... -> yes
4. Encrypt API key -> yes

Conveniently, this repo's `travis.yml` already provides structure for releasing into GitHub. You will, in any case, have to replace the credentials with your own ones. You can see how to do that here: `https://docs.travis-ci.com/user/deployment/releases#authenticating-with-an-oauth-token`.

Also note that the release can be customized with keywords like `name, body, draft, prerelease`.

`https://docs-staging.travis-ci.com/user/deployment/releases/`.

#### PyPI release config:

As with GitHub releases, the `.travis.yml` file already provides structure for deploying to PyPI. You just have to replace the credentials with your own. To encrypt your password, use the following command (more info here: `https://docs.travis-ci.com/user/encryption-keys/`). Again, be careful because **this will reformat the `travis.yml` file**, deleting all comments and blank lines (although the functionality won't be affected). A temporary backup will help with this:

```
travis encrypt <PASSWORD> --add deploy.password
```

For that, make sure you installed the Travis CLI (see `https://github.com/travis-ci/travis.rb#installation`).


#### Branching:

Travis builds get triggered on `master` and tagged builds only. Regular work can be done on a `dev` branch:

```
# create branch right after a commit:
git checkout -b dev
# work normally on it...
...
# track the new branch if you want to implicitly push to it:
git push -u origin dev # the first time, then `git push`

# once a milestone is reached, merge into master:
xx
```
