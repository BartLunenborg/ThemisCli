#! /usr/bin/env node
const yargs = require("yargs");
const chalk = require('chalk');
const boxen = require("boxen");
const { spawn } = require('child_process');
const path = require('path')
const fs = require('fs-extra')
const os = require('os');

const usage = chalk.keyword('violet')("\nUsage: themis command\n" + boxen(chalk.green("\n" + "Themis workflow cli.\n" + "Can be used for downloading tests or running tests.\n"), {padding: 1, borderColor: 'green', dimBorder: true}));
const options = yargs
  .usage(usage)
  .command({
    command: "user <username>",
    describe: "Set the username used for logging in.",
    handler: async (argv) => {
      const configDir = path.join(os.homedir(), '.config', 'themis_cli');
      const configPath = path.join(configDir, 'config.json');
      try {
        await fs.ensureDir(configDir);

        const configExists = await fs.pathExists(configPath);
        if (!configExists) {
          console.error(`Error: config file not found at ${configPath}, use 'themis setup' to create it.`);
          process.exit(1);
        }

        const config = await fs.readJson(configPath);
        config.user = argv.username;

        await fs.writeJson(configPath, config, { spaces: 2 });
        console.log(`Username: ${argv.username} stored in configuration file.`);
      } catch (err) {
        console.error(`Error: ${err.message}`);
        process.exit(1);
      }
    }
  })
  .command({
    command: "year",
    describe: "Set the year used for Themis (defaults to 2024-2025).",
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
      })
      .option('n', {
        alias: 'no-redirect',
        describe: 'Pass the test file as an argument to the executable\n e.g ./a.out < 1.in becomes ./a.out 1.in',
        type: 'boolean',
        default: false
      })
      .option('v', {
        alias: 'verbose',
        describe: 'If a test fails the diff will be printed',
        type: 'boolean',
        default: false
      });
    },
    handler: (argv) => {
      let programPath = argv.program;
      const runTestsPath = path.join(__dirname, 'runTests.sh');
      let commandToRun = `${runTestsPath}`;
      if (programPath) {
        commandToRun += ` ${programPath}`;
      }
      if (argv.noRedirect) {
        commandToRun += ` -n`;
      }
      if (argv.verbose) {
        commandToRun += ` -v`;
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
    describe: "Show the stored username and year.",
    handler: async () => {
      const configDir = path.join(os.homedir(), '.config', 'themis_cli');
      const configPath = path.join(configDir, 'config.json');
      try {
        await fs.ensureDir(configDir);

        const configExists = await fs.pathExists(configPath);
        if (!configExists) {
          console.error(`Error: config file not found at ${configPath}, use 'themis setup' to create it.`);
          process.exit(1);
        }

        const config = await fs.readJson(configPath);
        console.log('Stored information:');
        if (config.user) {
          console.log(`Username: ${config.user}`);
        } else {
          console.log(`Username: nothing stored`);
        }
        if (config.year) {
          console.log(`Year: ${config.year}`);
        } else {
          console.log(`Year: nothing stored`);
        }
      } catch (err) {
        console.error(`Error: ${err.message}`);
        process.exit(1);
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
