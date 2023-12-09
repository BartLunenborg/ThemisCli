# Themis CLI

Use this cli tool to make the downloading and running of test cases easier. 

Made to work with Themis - Programming Judge of the RUG.


## Installation

To install themis cli globally using npm:

```bash
  npm install -g themis_cli
```
After installing, you should now be able to use themis everywhere. To check try:
```bash
  themis
```
Note, this program requires you to have ```python3``` and ```selenium``` on your pc. For selenium you can simply:
```bash
  pip install selenium
```
## Features

- Download test cases
- Run tests locally
- Save user name
- Save preferred year

## How to get started

Although not needed, if your are downloading test cases frequently it is nice to save your user name:
```bash
  themis user <s_number>
```
It can also save some time to set the current academic year:
```bash
  themis year
```
To check your saved username and year type:
```bash
  themis info
```
We can start the test case downloading flow by typing:
```bash
  themis get
```
This will run you through options until you are at the location where the tests you want are found. This will download all the files to the ```./tests/``` directory. If the tests directory is not present in your current directory it will create it. 

Note, if you want to run ```themis test a.out``` on these tests, you should call ```themis get``` from within the directory where your executable will be located.


We can also judge our program locally. To do this, compile your code to an executable and:
```bash
  themis test <a.out>
```
In this case ```a.out``` is just an example, any name for the executable would work. This will test your program against the downloaded tests in the ```./tests``` directory. It expects that the directory where you call ```themis test <a.out>``` from contains the ```a.out``` file and the ```tests``` directory. It will tell you how many test cases you passed and will store wrong output in the ```./testDiffs``` directory.
