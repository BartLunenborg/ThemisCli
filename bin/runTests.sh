#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[01;34m'
NC='\033[0m'

if [ -z "$1" ]; then
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
else
  EXECUTABLE="./$1"
fi

TEST_DIR="./tests"
DIFFS_DIR="./testsDiffs"

totalTests=0
passedTests=0

if [ ! -e "$EXECUTABLE" ]; then
  echo -e "${RED}Error: The specified program '$EXECUTABLE' does not exist.${NC}"
  exit 1
fi

if [ ! -d "$TEST_DIR" ]; then
  echo -e "${RED}Error: The tests directory '$TEST_DIR' does not exist.${NC}"
  exit 1
fi

if [ ! -d "$DIFFS_DIR" ]; then
  mkdir -p "$DIFFS_DIR"
else
  rm -rf "$DIFFS_DIR"/*
fi

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
  actual=$($EXECUTABLE < "$test")
  end_time=$(date +%s.%N)

  if [ "$actual" = "$(cat "$expected")" ]; then
    passedTests=$((passedTests + 1))
    printf -v index_formatted "%2d" "$index"
    echo -e "Test $index_formatted: ${GREEN}Passed${NC} (time taken: $(bc <<<"scale=3; $end_time - $start_time") seconds)"
  else
    printf -v index_formatted "%2d" "$index"
    echo -e "Test $index_formatted: ${RED}Failed${NC} (time taken: $(bc <<<"scale=3; $end_time - $start_time") seconds)"
    echo -e "Input:\n$(cat "$test")\n\nExpected:\n$(cat "$expected")\n\nActual:\n$actual" > "$diff_file"
  fi
done

if [ "$totalTests" -eq 0 ]; then
  echo -e "No tests found in ./tests"
elif [ "$totalTests" -eq "$passedTests" ]; then
  echo -e "${GREEN}Passed all $totalTests/$totalTests tests!${NC}"
  rm -r "$DIFFS_DIR"
else
  echo -e "There were ${RED}test failures${NC}, passed $passedTests/$totalTests tests."
  echo -e "See the ${BLUE}testsDiffs${NC} directory for the differences in output."
fi
