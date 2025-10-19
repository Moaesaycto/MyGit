# ============================================================
#                   TESTING General Stuff
# ============================================================

making_a_project='
rm -rf ./* ./.*
mygit-init
touch a b c d
echo "first" > a
echo "second" >> a
echo "third" > b
mygit-add a b c
mygit-status
echo "forgot to add" > c
mygit-add c
mygit-commit -m "Uploading some files"
mygit-status
mygit-commit -m "Making sure..."
mygit-status
mygit-branch new_branch
mygit-branch new_branch_to_delete
mygit-branch new_branch_to_delete -d
mygit-branch new_branch
echo "tracking trunk" > d
mygit-add d
mygit-commit -m "just before checkout"
mygit-status
mygit-branch
mygit-checkout new_branch
mygit-rm a
mygit-commit -m "Committing removal"
mygit-add e
echo "something important" > e
mygit-checkout trunk
mygit-status
mygit-branch staging_branch
mygit-checkout staging_branch
mygit-branch
touch f1 f2 f3 f4 f5
seq 1 10 > f1
seq 10 100 > f2
mygit-commit -m "updating"
mygit-commit -m "updating" -a
mygit-status
mygit-show :a
mygit-show :f1
mygit-show :f2
'

# By this point, we have populated some branches with differing files.
# Let's try some merging
cleaning_project='
mygit-checkout trunk
mygit-merge new_branch -m "Trying to merge with trunk"
mygit-log
mygit-merge new_branch -m "Trying to merge with trunk"
'

test_block="$making_a_project
$cleaning_project
"

./_tester.sh 9 "$test_block"
