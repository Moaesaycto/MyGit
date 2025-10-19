#!/bin/dash

# ============================================================
#                TESTING mygit-show
# ============================================================

# TO MARKER:
#   This test covers index-mode, commit-mode, bad inputs,
#   missing commits/files, and weird file naming.

setup='
mygit-init
echo apple > a
echo banana > b
echo cherry > c
mygit-add a b
mygit-commit -m "commit-0"
echo apricot > a
mygit-add a
mygit-commit -m "commit-1"
echo blueberry > b
mygit-add b
mygit-commit -m "commit-2"
echo coconut > c
mygit-add c
'

bad_usage_tests='
mygit-show
mygit-show :
mygit-show 1::a
mygit-show --
mygit-show -z
mygit-show 1:
mygit-show :foo
'

bad_target_tests='
mygit-show 0:z
mygit-show 2:z
mygit-show 999:a
mygit-show -1:a
'

index_mode_tests='
mygit-show a
mygit-show b
mygit-show c
'

commit_mode_tests='
mygit-show 0:a
mygit-show 1:a
mygit-show 2:b
mygit-show 0:b
'

filename_edge_cases='
mygit-show 0:=b
mygit-show :=|
'

empty_file_test='
touch empty.txt
mygit-add empty.txt
mygit-commit -m "empty file"
mygit-show empty.txt
mygit-show 6:empty.txt
'

exist_but_changes='
echo different > d
mygit-add d
mygit-show d
mygit-show 0:d
'

test_block="$setup
$bad_usage_tests
$bad_target_tests
$index_mode_tests
$commit_mode_tests
$filename_edge_cases
$empty_file_test
$exist_but_changes
"

./_tester.sh 3 "$test_block"
