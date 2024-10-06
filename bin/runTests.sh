#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[01;34m'
NC='\033[0m'
TEST_DIR="./tests"
DIFFS_DIR="./tests-diffs"

no_redirect_flag=false
verbose=false
program=""

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    -n|--no-redirect)
      no_redirect_flag=true
      shift
      ;;
    -v|--verbose)
      verbose=true
      shift
      ;;
    *)
      # If not a flag, treat as the program name
      program="$1"
      shift
      ;;
  esac
done

# Find the executable to use
if [ -z "$program" ]; then  # If not provided, look for a.out or main
  if [ -e "a.out" ]; then
    EXECUTABLE="./a.out"
    echo -e "${GREEN}a.out${NC} will be used for running tests."
  elif [ -e "main" ]; then
    EXECUTABLE="./main"
    echo -e "${GREEN}main${NC} will be used for running tests."
  else
    echo -e "${RED}Error: No executable provided, and 'a.out' or 'main' not found.${NC}"
    exit 1
  fi
else  # Check if the provided executable exists.
  if [ ! -e "$program" ]; then
    echo -e "${RED}Error: The specified program '$program' does not exist.${NC}"
    exit 1
  fi
  if [[ "$program" == *.py ]]; then  # Prepend the executable with the required string
    EXECUTABLE="python3 $program"
  else
    EXECUTABLE="./$program"
  fi
fi

# Ensure tests directory exists
if [ ! -d "$TEST_DIR" ]; then
  echo -e "${RED}Error: The tests directory '$TEST_DIR' does not exist.${NC}"
  exit 1
fi

# Make a directory for the .diff files
if [ ! -d "$DIFFS_DIR" ]; then
  mkdir -p "$DIFFS_DIR"
else
  rm -rf "$DIFFS_DIR"/*
fi

# Run the tests
tests=($(find "$TEST_DIR" -maxdepth 1 -type f -name '*.in' | sort -V))
for test in "${tests[@]}"; do
  totalTests=$((totalTests + 1))

  expected="${test%.in}.out"
  filename=$(basename "$test")
  index="${filename%.*}"
  diff_file="$DIFFS_DIR/$index.diff"

  if [ ! -e "$expected" ]; then
    echo -e "${RED}Error: Missing corresponding .out file for $test${NC}"
    continue
  fi

  start_time=$(date +%s.%N)
  if $no_redirect_flag; then
    actual=$($EXECUTABLE "$test")
  else
    actual=$($EXECUTABLE < "$test")
  fi
  end_time=$(date +%s.%N)

  if [[ "$index" =~ ^-?[0-9]+$ ]]; then
    printf -v index_formatted "%2d" "$index"
  else
    printf -v index_formatted "%s"  "$index"
  fi
  if [ "$actual" = "$(cat "$expected")" ]; then
    passedTests=$((passedTests + 1))
    echo -e "Test $index_formatted: ${GREEN}Passed${NC} (time taken: $(bc <<<"scale=3; $end_time - $start_time") seconds)"
  else
    echo -e "Test $index_formatted: ${RED}Failed${NC} (time taken: $(bc <<<"scale=3; $end_time - $start_time") seconds)"
    echo -e "INPUT:\n$(cat "$test")\n<<<<<=============>>>>>\nEXPECTED:\n$(cat "$expected")\n<<<<<=============>>>>>\nACTUAL:\n$actual" > "$diff_file"
  fi
done

if [ "$totalTests" -eq 0 ]; then
  echo -e "No tests found in ./tests"
elif [ "$totalTests" -eq "$passedTests" ]; then
  echo -e "${GREEN}Passed all $totalTests/$totalTests tests!${NC}"
  rm -r "$DIFFS_DIR"
else
  echo -e "There were ${RED}test failures${NC}, passed $passedTests/$totalTests tests."
  if $verbose; then
    for diff_file in ./tests-diffs/*.diff; do
      echo -e "${RED}$diff_file:${NC}"
      cat "$diff_file"
    done
  else
    echo -e "See the ${BLUE}tests-diffs${NC} directory for the differences in output."
  fi
fi
