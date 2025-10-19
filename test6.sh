#!/bin/dash

# ============================================================
#                   TESTING mygit-branch
# ============================================================

before_first_commit='
mygit-branch
mygit-branch new
mygit-branch -d new
mygit-branch .badname
mygit-branch -d .badname
mygit-init
mygit-branch
mygit-branch new
mygit-branch -d new
'

baseline='
rm -rf ./* ./.*
mygit-init
echo base > a
mygit-add a
mygit-commit -m "c0"
mygit-branch
'

create_and_duplicate='
mygit-branch dev
mygit-branch
mygit-branch dev
mygit-branch -z wrong
mygit-branch -d
mygit-branch extra arg
mygit-branch
'

delete_errors='
mygit-branch -d trunk
mygit-branch -d ghost
mygit-branch -d dev
mygit-branch
'

names_matching='
mygit-branch -bad
mygit-branch --double
mygit-branch -a
mygit-branch _bad
mygit-branch .hidden
mygit-branch /slashes
mygit-branch ""
mygit-branch ---
mygit-branch _
mygit-branch "bad name"
mygit-branch
'

branch_edge_cases='
mygit-branch test -d
mygit-branch -d test extra
mygit-branch foo/bar
mygit-branch " "
mygit-branch Dev
mygit-branch dev
mygit-branch version_2.0
mygit-branch -d ghost
mygit-branch
'

names_matching='
mygit-branch -bad
mygit-branch --double
mygit-branch -a
mygit-branch _bad
mygit-branch .hidden
mygit-branch /slashes
mygit-branch ""
mygit-branch ---
mygit-branch _
mygit-branch "bad name"
mygit-branch 123
mygit-branch dev-
mygit-branch dev_
mygit-branch --dev
mygit-branch a--b
mygit-branch "this-branch-name-is-way-too-long____________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________"
mygit-branch
'

test_block="$before_first_commit
$baseline
$create_and_duplicate
$delete_errors
$names_matching
$branch_edge_cases
$additional_cases
"

./_tester.sh 6 "$test_block"