# Preface
This project provides test-driven-development tools with the goal of adhering to Agency Guidelines.  Tests are ran by vkdash.tap, and their results are built into a static HTML5 site by vkdash. 

A special use case is sharing project status with teams outside of the NASA firewall. 

This document assumes you are familiar with git and system adminstration.


## vkdash

![VKDash](http://i.imgur.com/N5LhE1p.jpg)

vkdash is a Test Anything Protocol (TAP) consumer that is geared
toward unit and regression testing and produces a static HTML
dashboard of test results.  The name vkdash is a homage to the
Voight-Kampff Machine in the movie Blade Runner which was used to test
if a "person" was a replicant.

vkdash can be used to report TAP test results during many stages of development. 
* Locally as part of extreme programming practices
* Locally when a developer commits to a local git repository
* By a server to vet pushed commits to branches before they are merged.
* By a server once a commit is merged

There are two ways vkdash was designed to be used.
To build a HTML page from test results.
```python
vkdash.ConsumeTAPtoHTML(html_file_name, tap_test_results)
```

To integrate all test results in the specified build directory into a HTML dashboard.  This function is not intended to be used regularly by a user.  Its purpose is to provide a holistic view of many repository's test results automatically by a server. 
```python
vkdash.BuildVKDashBoard(build_directory, results_directory)
```


## vkdash.tap
A Test Anything Protocol version 13 producer for evaluation purposes only.


### Example
This example generates an html document called results.html that is placed in the working directory which reports the results of a simple test.

```python
def foo():
    return 1

t.ok(foo() == 1, "Test 1 == 1")
t.ok(foo() != 2, "Test 1 != 2")
t.ok(foo() == 2, "Test failure of 1 == 2", message="1 != 2")
t.ok(foo() == 2, "Test failure of 1 == 2 with silent message")
t.ok("'junk in the expected...'", "Test failure of junk with silent message")

test_results = t.ProduceTAP()
```

A more thorough test example is provided in the file example_tap.py in the examples folder.


# Installation
Clone this repository, and inside its directory, install vkdash with:

```bash
python setup.py install
```

Or install the package in developer mode if you will frequently customize it - to change the HTML layout, for example.

```bash
pip install -e .
``` 


# Githook
A Githook is a script that is triggered when particular git events occur.  For further reading : https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks

To run tests automatically just before you try to commit to a repository, save a test python script like the one below as the file 'pre-commit' in the repository's hidden .git/hooks/ directory.  Assuming you're on Linux, this script file may look like:

```python
# fill in
```

Now, as you git commit to the repository, the test will automatically run.  In this case, the test succeeds, so the commit is allowed to occur.  If the test fails, the assert will prevent the commit from occuring at all.  Note that this hook must be set for each individual git repository you wanted tested.


# vkdash.tap githooks on Gitea
Gitea is an open-source self-hosted git service fork of gogs.  To setup vkdash to generate a dashboard using a githook with gitea, first **install vkdash on the server as shown above**.  TODO (start with vkdash.tap then go to dashboard...)

Then, download the latest gitea package from here : https://github.com/go-gitea/gitea/releases. 

Install it by running the following commands.

```bash
wget -O gitea URL_TO_YOUR_GITEA_DOWNLOAD
chmod +x gitea
```

Gitea listens on port 3000, so to access its web portal, go to http://YourDomainNameHere:3000.  As part of this crashcourse, accept the default configuration settings.  Register an account - the first account registered administers the whole site.  

Create a new repository by clicking on the '+' button on the upper right of the web page.  If you do not have a repository to use as an example, use this repository of vkdash (TODO Fill in with step by step instructions).  This article is assuming this repository is being used.

Click on the 'Settings' button on the upper right of the repository's menu. On the left, under 'Settings', find 'Git Hooks', and click the pencil button to the right of 'pre-recieve'.  Pre-recieve only triggers on the server when a commit has been pushed to the repository.  Its purpose is to vet the commit, to prevent it merging with the branch if it does not pass inspection.  

For simplities sake, remove the line that generates a HTML document. The next section shows how to use vkdash to generate a dashboard from all git repositories 

```python
# fill in
```

# vkdash board
This git hook below is a little more complicated.  But first, the example_tap.py file will need to be slightly modified to support vkdash's dashboard.  

Change the line in the example_tap.py from
```python
vkdash.ConsumeTAPtoHTML('results.html', test_results)
```

to

```python
vkdash._ConsumeTAPtoVKDashBoard(test_results)
```

Now change the git hook Read the comments for explaination.
```bash
#!/bin/bash

# make a safe space to test

if ! [ -d "/tmp/testing_dir" ]; then
   mkdir /tmp/testing_dir
fi

# git commits pass in 3 variables that we read

read oldrev newrev branch 

# turn the new revision from internal git data into actual files by archiving the repository then extract the files in the temporary testing directory.

git archive $newrev | tar -x -C /tmp/testing_dir &>/dev/null  #tar is noisy in this circumstance for some reason.

cd /tmp/testing_dir

# run the test!
# The program's output is piped to a html file that vkdash looks in to build the dashboard.
# The tiny change we made above causes the test results to be printed to stdio instead of being saved to a file.
python example_tap.py > ~/VKDashBoard/code/example_results.html #example_tap.py is this repository's test. Substute your own!

TODO cause this script to return non-zero if python raises an exception

# cleanup
rm -rf /tmp/testing_dir
```

If example_tap.py raises an exception, the script relays it to gitea to reject the commit. The user who pushed will be notified. 

*Note, not all git GUIs support reading back from server side githook messages.* If in doubt, use git's CLI!

# Optional
At this point, the dashboard has been generated and now viewable. You can configure 
scp ~/VKDashBoard/build/results.html USER@IP_ADD:/dir/to/html #TODO this doesn't seem to report to the calle any failures...
