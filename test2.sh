#!/bin/dash

# ============================================================
#                     TESTING mygit-log
# ============================================================

# TO MARKER:
#   These are just the raw commands that are passed in. Please
#   refer to the _tester.sh file to see how it works.

setup='
mygit-init
touch a b c
echo one > a
echo two > b
echo three > c
'

bad_args='
mygit-log --
mygit-log -a
mygit-log lolno
'

basic_log_testing='
mygit-log
mygit-add a
mygit-commit -m "commit-0"
mygit-log
mygit-add b c
mygit-commit -m "commit-1"
mygit-log
echo updated > b
mygit-commit -a -m "commit-2"
mygit-log
echo new >> a
mygit-add a
mygit-commit -m "commit-3"
mygit-log
mygit-commit -m "noop"
mygit-log
'

log_edge_cases='
echo x > x
mygit-add x
mygit-commit -m "repeat"

echo y > y
mygit-add y
mygit-commit -m "repeat"

mygit-log
'

test_block="mygit-log
$bad_args
$setup
$bad_args
$basic_log_testing
$log_edge_cases
"

./_tester.sh 2 "$test_block"
