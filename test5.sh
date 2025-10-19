#!/bin/dash

# ============================================================
#                     TESTING mygit-status
# ============================================================

# All cases (that I found):
#   same as repo
#   added to index
#   added to index, file changed
#   file changed, changes not staged for commit
#   file changed, changes staged for commit
#   file changed, different changes staged for commit
#   file deleted
#   added to index, file deleted
#   file deleted, deleted from index
#   deleted from index
#   untracked
#   (plus argument-error cases)

arg_tests='
mygit-status foo
mygit-status --
mygit-status -h
'

no_commit_repo='
rm -rf .mygit
mygit-init
echo first > lone
mygit-add lone
mygit-status
'

baseline='
rm -rf ./
mygit-init
echo one > a
echo two > b
echo three > c
mygit-add a b
mygit-commit -m "base"
'

untracked_and_same='
echo four > d
mygit-status
'

add_then_modify='
echo new > e
mygit-add e
echo newer >> e
mygit-status
'

changed_not_staged='
echo mod >> a
mygit-status
'

changed_and_staged='
mygit-add a
mygit-status
'

divergent='
echo another >> a
mygit-status
'

file_deletes='
rm b
mygit-status
mygit-rm --cached b
mygit-status
rm a
mygit-rm --cached a
mygit-status
'

recreate='
echo resurrected > a
mygit-status
'

extra_edges='
touch empty.txt
mygit-add empty.txt
mygit-status
'

reset_with_commit='
mygit-add .
mygit-commit -m "sync"
mygit-status
'

test_block="$arg_tests
$no_commit_repo
$baseline
$untracked_and_same
$add_then_modify
$changed_not_staged
$changed_and_staged
$divergent
$file_deletes
$recreate
$extra_edges
$reset_with_commit
"

./_tester.sh 5 "$test_block"
