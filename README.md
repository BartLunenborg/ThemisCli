# Themis CLI

Made to work with Themis - Programming Judge of the RUG.

Use this cli tool to easily batch download test cases (and only test cases) and test your program against these downloaded test cases.


## Installation

To install themis cli globally using npm:

```bash
  npm install -g themis_cli
```
After installing, you should now be able to use themis everywhere. To check try:
```bash
  themis
```
**This tool requires** you to have ```python3``` and ```selenium``` on your pc. For selenium you can simply:
```bash
  pip install selenium
```
## Features

- Batch download test cases
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

Note, if you want to run ```themis test [a.out]``` on these tests, you should call ```themis get``` from within the directory where your executable will be located.

We can also judge our program locally. To do this, compile your code to an executable and:
```bash
  themis test [a.out]
```
In this case ```a.out``` is just an example, any name for the executable would work. This will test your program against the downloaded tests in the ```./tests``` directory. It expects that the directory where you call ```themis test [a.out]``` from contains the ```a.out``` executable and the ```tests``` directory. It will tell you how many test cases you passed and will store wrong output in the ```./testsDiffs``` directory. If no executable is provided in the command (```themis test```) then the program will look for ```a.out``` or ```main``` (in that order). So if your executable is called ```a.out``` or ```main``` you can just run ```themis test```

In the end we get a project directory that looks something like:
```bash
assignmentDir
│
├── main.c
├── main (executable)
│
├── tests
│   ├── 1.in
│   ├── 1.out
│   ├── 2.in
│   └── 2.out
│
└── testsDiffs
    └── 2.diff
```

Where calling ```themis get``` from assignmentDir would have yielded the ```tests``` directory and ```themis test``` would have yielded the ```testsDiffs``` directory if our program passed test case 1 but not test case 2. Note that we can use ```themis test``` in this case because our program executable is called ```main```.
