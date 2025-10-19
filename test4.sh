#!/bin/dash

# ============================================================
#                     TESTING mygit-rm
# ============================================================

# TO MARKER:
#   This test covers removal from index and/or working dir,
#   force/cached options, staged file protection, and edge cases.

setup='
mygit-init
echo 1 > a
echo 2 > b
echo 3 > c
echo 4 > d
echo 5 > e
mygit-add a b c d e
mygit-commit -m "initial commit"
'

invalid_usage='
mygit-rm
mygit-rm --
mygit-rm -z
mygit-rm --unknown
mygit-rm --force --cached --oops
mygit-rm :notafile
'

basic_removal='
cp a a_copy
mygit-rm a
mygit-add a_copy
mv a_copy a
'

cached_removal='
mygit-rm --cached b
mygit-add b
'

unstaged_removal='
echo new > f
mygit-rm f
'

unmodified_safety_check='
echo changed > c
mygit-rm c
mygit-rm --cached c
mygit-rm --force c
'

force_and_cached='
echo x > d
mygit-rm --force --cached d
'

nonexistent_removal='
mygit-rm not_in_index
'

multiple_files='
echo one > g
echo two > h
mygit-add g h
mygit-commit -m "extra files"
mygit-rm g h
'

filename_edge_cases='
echo spaced > "space file.txt"
mygit-add "space file.txt"
mygit-commit -m "strange names"
mygit-rm "space file.txt"
'

cached_file_removed_on_disk='
echo gone > gone.txt
mygit-add gone.txt
rm gone.txt
mygit-rm --cached gone.txt
'

readded_with_different_content='
echo v1 > temp
mygit-add temp
mygit-commit -m "v1"
echo v2 > temp
mygit-add temp
echo v3 > temp
mygit-rm temp
'

batch_conflicts='
echo x > x
echo y > y
echo z > z
mygit-add x y z
mygit-commit -m "trio"
echo y-changed > y
mygit-add y
echo z-changed > z
mygit-rm x y z
'

staged_deleted_and_cached='
echo killme > victim
mygit-add victim
mygit-commit -m "victim added"
rm victim
mygit-rm --cached victim
'

# Manually test this one, the tester doesn't like it
unreadable_file_test='
echo secret > private
mygit-add private
chmod 000 private
mygit-rm private
chmod +r private
'

pre_commit_protection='
mygit-init
echo a > pre_a
mygit-add pre_a
mygit-rm pre_a
'

force_redundant='
echo f > f
mygit-add f
mygit-commit -m "add f"
mygit-rm --force f
'

test_block="$setup
$invalid_usage
$basic_removal
$cached_removal
$unstaged_removal
$unmodified_safety_check
$force_and_cached
$nonexistent_removal
$multiple_files
$filename_edge_cases
$cached_file_removed_on_disk
$readded_with_different_content
$batch_conflicts
$staged_deleted_and_cached
$pre_commit_protection
$force_redundant
"

./_tester.sh 4 "$test_block"
