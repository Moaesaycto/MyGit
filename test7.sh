#!/bin/dash

# ============================================================
#                   TESTING mygit-checkout
# ============================================================

before_init='
rm -rf ./* ./.*
mygit-checkout
mygit-checkout trunk
mygit-checkout dev
mygit-checkout -d trunk
mygit-checkout unknown
'

checkout_setup='
rm -rf ./* ./.*
mygit-init
echo base > file.txt
mygit-add file.txt
mygit-commit -m "initial commit"
mygit-branch dev
mygit-branch feature
'

basic_switching='
mygit-checkout dev
echo dev > dev.txt
mygit-add dev.txt
mygit-commit -m "dev commit"
mygit-checkout trunk
echo trunk > file.txt
mygit-add file.txt
mygit-commit -m "trunk edit"
mygit-checkout feature
echo feature > feat.txt
mygit-add feat.txt
mygit-commit -m "feature commit"
mygit-checkout trunk
mygit-checkout dev
mygit-checkout feature
mygit-checkout trunk
'

invalid_usage='
mygit-checkout
mygit-checkout trunk dev
mygit-checkout -d trunk
mygit-checkout non_existent_branch
touch dev
mygit-checkout dev
mygit-checkout 123
mygit-checkout ;_;
'

dirty_working_directory='
echo dirtychange > file.txt
mygit-checkout feature
echo featureupdate > feat.txt
mygit-add feat.txt
mygit-commit -m "mod feat"
echo dirtychangeagain > feat.txt
mygit-checkout dev
mygit-branch
'

state_verification='
cat file.txt
cat dev.txt
cat feat.txt
mygit-checkout trunk
cat file.txt
mygit-checkout feature
cat feat.txt
mygit-branch
'

complex_branch_ops='
mygit-checkout dev
mygit-branch -d dev
mygit-branch dev2
mygit-checkout dev2
echo change > dev2.txt
mygit-add dev2.txt
mygit-commit -m "dev2 commit"
mygit-checkout trunk
mygit-branch hotfix
mygit-checkout hotfix
echo hotfix > hot.txt
mygit-add hot.txt
mygit-commit -m "hotfix commit"
mygit-checkout trunk
mygit-branch -d hotfix
mygit-branch dev3
mygit-checkout dev3
echo dev3 > d3.txt
mygit-add d3.txt
mygit-commit -m "dev3 commit"
mygit-checkout feature
mygit-branch -d dev3
mygit-checkout trunk
mygit-checkout dev2
mygit-checkout hotfix
mygit-branch
'

checkout_test_block="$before_init
$checkout_setup
$basic_switching
$invalid_usage
$dirty_working_directory
$state_verification
$complex_branch_ops
"

./_tester.sh 7 "$checkout_test_block"
