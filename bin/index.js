#! /usr/bin/env node
const yargs = require("yargs");
const chalk = require('chalk');
const boxen = require("boxen");
const { spawn } = require('child_process');
const path = require('path')
const fs = require('fs').promises;

const usage = chalk.keyword('violet')("\nUsage: themis command\n" + boxen(chalk.green("\n" + "Themis workflow cli.\n" + "Can be used for downloading tests or running tests.\n"), {padding: 1, borderColor: 'green', dimBorder: true}));
const options = yargs
  .usage(usage)
  .command({
    command: "user <username>",
    describe: "Set the username used for logging in.",
    handler: async (argv) => {
      const userFilePath = path.join(__dirname, 'user.txt');
      await fs.writeFile(userFilePath, argv.username);
      console.log(`Username: ${argv.username} stored`);
    }
  })
  .command({
    command: "year",
    describe: "Set the year used for Themis.",
    handler: (argv) => {
      const setYearPath = path.join(__dirname, 'setYear.py');
      const pythonProcess = spawn('python3', [setYearPath], { stdio: 'inherit'});
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.log(`set year exited with code ${code}`);
        }
      });
    },
  })
  .command({
    command: "get",
    describe: "Start flow for getting tests. Tests will be saved to ./tests (tests directory will be created if non-existent).",
    handler: (argv) => {
      const getTestsPath = path.join(__dirname, 'getTests.py');
      const pythonProcess = spawn('python3', [getTestsPath], { stdio: 'inherit'});
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
        console.log(`Get flow exited with code ${code}`);
        }
      });
    },
  })
  .command({
    command: "test [program]",
    describe: "Test you program against your downloaded test cases.\nIf no program is passed it looks for 'a.out' or 'main' (in that order).",
    builder: (yargs) => {
      return yargs.positional('program', {
        describe: 'Your executable program (e.g. a.out, main)',
        type: 'string',
      });
    },
    handler: (argv) => {
      let programPath = argv.program;
      const runTestsPath = path.join(__dirname, 'runTests.sh');
      let commandToRun = ``;
      if (!programPath) {
        commandToRun = `${runTestsPath}`;
      } else {
        commandToRun = `${runTestsPath} ${programPath}`;
      }
      const childProcess = spawn(commandToRun, { stdio: 'inherit', shell: true });
      childProcess.on('close', (code) => {
        if (code !== 0) {
          console.error(`Error: Test execution exited with code ${code}`);
        }
      });
    },
  })
  .command({
    command: "info",
    describe: "Show the stored username and standard year.",
    handler: async () => {
      const userFilePath = path.join(__dirname, 'user.txt');
      const yearFilePath = path.join(__dirname, 'year.txt');
      try {
        const [user, year] = await Promise.all([
          fs.readFile(userFilePath, 'utf-8').catch(() => null),
          fs.readFile(yearFilePath, 'utf-8').catch(() => null),
        ]);
        if (user) {
          console.log(`Username: ${user}`);
        } else {
          console.log("No username stored.");
        }
        if (year) {
          console.log(`Year: ${year}`);
        } else {
          console.log("No year stored.");
        }
      } catch (error) {
        console.error("Error reading files:", error.message);
      }
    }
  })
  .command({
    command: "$0",
    describe: "Show help message.",
    handler: () => {
      yargs.showHelp();
    },
  }) 
  .help(true)
  .argv;
