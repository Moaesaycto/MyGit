# ============================================================
#                   TESTING mygit-merge
# ============================================================

before_first_commit='
rm -rf ./* ./.*
mygit-merge trunk -m "no repo yet"
'

setup_repo='
rm -rf ./* ./.*
mygit-init
echo 1 > a
mygit-add a
mygit-commit -m "c0"
mygit-branch dev
mygit-branch feature
mygit-branch ff
'

divergence_commits='
mygit-checkout dev
echo dev >> a
mygit-add a
mygit-commit -m "dev1"
echo dev2 >> a
mygit-add a
mygit-commit -m "dev2"

mygit-checkout trunk
echo trunk >> a
mygit-add a
mygit-commit -m "trunk1"

mygit-checkout feature
echo feature > b
mygit-add b
mygit-commit -m "feature1"

mygit-checkout ff
echo ff > ff.txt
mygit-add ff.txt
mygit-commit -m "ff1"
mygit-checkout trunk
'

fast_forward_merge='
mygit-merge ff -m "fast-forward into trunk"
'

three_way_merge='
mygit-merge dev -m "merge dev into trunk"
mygit-branch
'

already_up_to_date='
mygit-merge trunk -m "noop"
mygit-checkout dev
mygit-merge trunk -m "ff dev from trunk"
mygit-checkout trunk
'

dirty_workdir_cases='
echo dirty > dirty.txt
mygit-merge feature -m "should block on dirty"
rm dirty.txt
echo staged >> a
mygit-add a
mygit-merge feature -m "merge with staged OK"
'

self_and_message_checks='
mygit-merge trunk -m ""
mygit-merge $(cat .mygit/HEAD) -m "self"
'

conflict_merge='
mygit-branch conflict
mygit-checkout conflict
echo conflict > a
mygit-add a
mygit-commit -m "conflict change"
mygit-checkout dev
echo other > a
mygit-add a
mygit-commit -m "dev conflict change"
mygit-merge conflict -m "attempt conflicting merge"
mygit-merge -m "msg" dev
'

invalid_usage_merge='
mygit-merge
mygit-merge dev
mygit-merge unknown -m "oops"
mygit-merge 9999 -m "bad id"
mygit-merge dev feature -m "too many"
mygit-merge dev -m
'

merge_test_block="$before_first_commit
$setup_repo
$divergence_commits
$fast_forward_merge
$three_way_merge
$already_up_to_date
$dirty_workdir_cases
$self_and_message_checks
$conflict_merge
$invalid_usage_merge
"

./_tester.sh 8 "$merge_test_block"
