#!/bin/bash

EXECUTABLE="./$1"
TEST_DIR="./tests"
DIFFS_DIR="./testDiffs"

totalTests=0
passedTests=0

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[01;34m'
NC='\033[0m'  # No Colour

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

if [ -n "$(find "$TEST_DIR" -maxdepth 1 -type f -name '*.in')" ]; then
    for infile in "$TEST_DIR"/*.in; do
        totalTests=$((totalTests + 1))

        expected="${infile%.in}.out"
        filename=$(basename "$infile")
        index="${filename%.*}"
        diff_file="$DIFFS_DIR/$index.diff"

        if [ ! -e "$expected" ]; then
            echo -e "${RED}Error: Missing corresponding .out file for $infile${NC}"
            continue
        fi

        start_time=$(date +%s.%N)
        actual=$($EXECUTABLE < "$infile")
        end_time=$(date +%s.%N)

        if [ "$actual" = "$(cat "$expected")" ]; then
            passedTests=$((passedTests + 1))
            echo -e "Test $index: ${GREEN}Passed${NC} (time taken: $(bc <<<"scale=3; $end_time - $start_time") seconds)"
        else
            echo -e "Test $index: ${RED}Failed${NC} (time taken: $(bc <<<"scale=3; $end_time - $start_time") seconds)"
            echo -e "Expected:\n$(cat "$expected")\nActual:\n$actual" > "$diff_file"
        fi
    done
fi

if [ "$totalTests" -eq 0 ]; then
    echo -e "No tests found in ./tests"
elif [ "$totalTests" -eq "$passedTests" ]; then
    echo -e "${GREEN}Passed all $totalTests/$totalTests tests!${NC}"
    rm -r "$DIFFS_DIR"
else
    echo -e "There were ${RED}test failures${NC}, passed $passedTests/$totalTests tests."
    echo -e "See the ${BLUE}testDiffs${NC} directory for the differences in output."
fi
