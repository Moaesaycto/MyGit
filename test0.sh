#!/bin/dash

# ============================================================
#                TESTING mygit-init & mygit-add
# ============================================================

# TO MARKER:
#   These are just the raw commands that are passed in. Please
#   refer to the _tester.sh file to see how it works.
#
#   When trying to add a file that has no permissions, it will
#   throw an error with the checking. Do this one manually!
#

basic_init_testing='
mygit-init testing is fun
mygit-init --
mygit-init -z
mygit-init
mygit-init
'

weird_init_testing='
rm -rf ./* ./.*
touch .gitignore
mygit-init
'

# Run twice (once before init, once after)
basic_add_testing='
touch a b c d e
mygit-add
mygit-add --
mygit-add -b
mygit-add help
mygit-add :awawa
mygit-add a
mygit-add a b c d e
'

edge_case_add_testing='
mkdir mydir
mygit-add mydir
mygit-add /dev/null
touch secret
chmod 000 secret
mygit-add secret
chmod 644 secret
touch f
mygit-add f mydir /dev/null secret
echo spaced content > "file with space.txt"
mygit-add "file with space.txt"
'

test_block="$basic_init_testing
$weird_init_testing
rm -rf ./* ./.*
$basic_add_testing
mygit-init
$basic_add_testing
$edge_case_add_testing
"

./_tester.sh 0 "$test_block"
