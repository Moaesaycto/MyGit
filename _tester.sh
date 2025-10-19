#!/bin/dash

# ============================================================
#                 ASSIGNMENT 2 CUSTOM CHECKER
# ============================================================
# READ ME
# This script runs every command once with the reference
# binary, then once with your binary, and only afterwards
# compares the two runs.  Directory state is therefore
# independent across the two passes.
#
# This one is slightly different to my assignment 1 checker as
# it creates two directories and runs the tests in them
# separately. It also compares to make sure that the files in
# both are identical are equal (testing the rm stuff).
#
# It stores failed cases in test_results/test<test_number>/.
# It ONLY stores failed cases, so no more annoying sifting.
# ------------------------------------------------------------

if [ $# -ne 2 ]; then
    echo "Usage: $0 <test_number> <tests_string> (received $# arguments)"
    exit 1
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
RESET='\033[0m'

test_num="$1"
tests="$2"
outdir="test_results/test$test_num"

ref_repo="ref_repo"
cap_repo="cap_repo"

rm -rf "$ref_repo" "$cap_repo" "$outdir"
mkdir -p "$ref_repo" "$cap_repo" "$outdir"

list_files() {
    dir="$1"
    for f in "$dir"/*; do
        [ -f "$f" ] && echo "${f##*/}"
    done | sort
}

status_log="$outdir/status_diff"
mkdir -p "$(dirname "$status_log")"
i=0

while IFS= read -r line; do
    [ -z "$line" ] && continue

    case "$line" in
        mygit-*)
            i=$((i + 1))

            stdout_ref=$(mktemp)
            stderr_ref=$(mktemp)
            stdout_stu=$(mktemp)
            stderr_stu=$(mktemp)
            files_ref=$(mktemp)
            files_stu=$(mktemp)

            (
                cd "$ref_repo" || exit 1
                2041 $line \
                    >"$stdout_ref" 2>"$stderr_ref"
                echo $? >"$stdout_ref.status"
            )

            (
                cd "$cap_repo" || exit 1
                ../$line \
                    >"$stdout_stu" 2>"$stderr_stu"
                echo $? >"$stdout_stu.status"
            )

            list_files "$ref_repo" >"$files_ref"
            list_files "$cap_repo" >"$files_stu"

            fail=0
            cmp -s "$stdout_ref" "$stdout_stu" || fail=1
            cmp -s "$stderr_ref" "$stderr_stu" || fail=1
            cmp -s "$stdout_ref.status" "$stdout_stu.status" || fail=1
            cmp -s "$files_ref" "$files_stu" || fail=1

            if cmp -s "$files_ref" "$files_stu"; then
                while read -r file; do
                    if ! cmp -s "$ref_repo/$file" "$cap_repo/$file"; then
                        fail=1
                        echo "  - contents of '$file' differ" >>"$status_log"
                    fi
                done <"$files_ref"
            fi

            if [ $fail -eq 0 ]; then
                printf "%b%d %b" "$GREEN" "$i" "$RESET"
            else
                printf "%b%d %b" "$RED" "$i" "$RESET"

                {
                    echo "Test $i failed"
                    cmp -s "$stdout_ref" "$stdout_stu" || echo "  - stdout differs"
                    cmp -s "$stderr_ref" "$stderr_stu" || echo "  - stderr differs"
                    cmp -s "$stdout_ref.status" "$stdout_stu.status" || echo "  - exit code differs"
                    cmp -s "$files_ref" "$files_stu" || echo "  - file list differs"
                } >>"$status_log"

                fail_file="$outdir/cmd$i.txt"
                {
                    echo "---===[ Test $i failed ]===---"
                    echo ""
                    echo "Failed command: $line"
                    echo "\n"
                    if ! cmp -s "$stdout_ref" "$stdout_stu"; then
                        echo "--- stdout differs ---"
                        echo -n "Expected: "
                        cat "$stdout_ref"
                        echo -n "Received: "
                        cat "$stdout_stu"
                        echo "\n"
                    fi
                    if ! cmp -s "$stderr_ref" "$stderr_stu"; then
                        echo "--- stderr differs ---"
                        echo -n "Expected: "
                        cat "$stderr_ref"
                        echo ""
                        echo -n "Received: "
                        cat "$stderr_stu"
                        echo "\n"
                    fi
                    if ! cmp -s "$stdout_ref.status" "$stdout_stu.status"; then
                        echo "--- exit status differs ---"
                        echo -n "Expected: "
                        cat "$stdout_ref.status"
                        echo -n "Received: "
                        cat "$stdout_stu.status"
                        echo "\n"
                    fi
                    if ! cmp -s "$files_ref" "$files_stu"; then
                        echo "--- surface file list differs ---"
                        echo "Expected:"
                        cat "$files_ref"
                        echo "Received:"
                        cat "$files_stu"
                        echo ""
                    fi

                    if cmp -s "$files_ref" "$files_stu"; then
                        while read -r file; do
                            if ! cmp -s "$ref_repo/$file" "$cap_repo/$file"; then
                                echo "--- file '$file' differs ---"
                                echo "Expected:"
                                cat "$ref_repo/$file"
                                echo "Received:"
                                cat "$cap_repo/$file"
                                echo ""
                            fi
                        done <"$files_ref"
                    fi
                } >"$fail_file"
            fi

            rm -f "$stdout_ref" "$stderr_ref" "$stdout_ref.status"
            rm -f "$stdout_stu" "$stderr_stu" "$stdout_stu.status"
            rm -f "$files_ref" "$files_stu"
            ;;
        *)
            (cd "$ref_repo" && eval "$line" >/dev/null 2>/dev/null)
            (cd "$cap_repo" && eval "$line" >/dev/null 2>/dev/null)
            ;;
    esac
done <<EOF
$tests
EOF

echo ""

if [ -s "$status_log" ]; then
    echo "--- Failures ---"
    printf "%b" "$RED"; cat "$status_log"; printf "%b" "$RESET"
else
    echo "${GREEN}All tests passed!${RESET}"
fi