#!/bin/dash

# ============================================================
#                    TESTING mygit-commit
# ============================================================

# TO MARKER:
#   These are just the raw commands that are passed in. Please
#   refer to the _tester.sh file to see how it works.

setup='
mygit-init
touch a b c
echo 1 > a
echo 2 > b
echo 3 > c
'

# Run twice (once before setup, once after)
bad_args='
mygit-commit
mygit-commit -m
mygit-commit -a
mygit-commit --
mygit-commit "hello" -m
mygit-commit oop -m "hello"
mygit-commit -m "hello" ""
mygit-commit -m
mygit-commit -z -m "oops"
'

basic_commit_testing='
mygit-add a
mygit-commit -m "commit-0"
mygit-commit -m "no changes"
mygit-add b c
mygit-commit -m "commit-1"
mygit-add d
echo 222 > b
mygit-commit -a -m "commit-2"
mygit-commit -m "noop"
echo 11 >> a
mygit-add a
mygit-commit -m "commit-3"
echo changed > c
mygit-commit -m "commit-4 (should not happen)"
mygit-add c
mygit-commit -m "commit-4 (actual)"
'

test_block="$bad_args
$setup
$bad_args
$basic_commit_testing
"

./_tester.sh 1 "$test_block"
