# ============================================================
#   COMP2041 ASSIGNMENT 2 SUBMISSION | UTILITIES FILE
#   Stephen Lerantges (z5319858)
#   Term 2, 2024
# ------------------------------------------------------------
# This file contains all needed functions to access the actual
# .mygit system so that none of it bloats up the actual
# commands. I've put all typing and docstrings to help explain
# everything.
# ============================================================

from typing import Any
import os
import re
import hashlib
import zlib
import sys

from tree import (
    add_node,
)

ROOT = ".mygit"
COMMITS_DIR = os.path.join(ROOT, "commits")
LOG_FILE = os.path.join(ROOT, "log")
INDEX_FILE = os.path.join(ROOT, "index")
HEAD_FILE = os.path.join(ROOT, "HEAD")
OBJECTS_DIR = os.path.join(ROOT, "objects")
BRANCHES_DIR = os.path.join(ROOT, "branch")


# Before each part (except init)
def preflight_checks(prefix: str) -> None:
    """
    Necessary checks for each of the separate commands. Specifically:
    - mygit repository is properly set up;
    - if .gitingore file is present, throw a fit.

    Args:
        prefix (str): The command name prefix used in the error message.
    """

    if os.path.exists(".gitignore"):
        error(
            f"mygit-{prefix}: error: can not run mygit because .gitignore present in current directory")

    if not os.path.isdir(ROOT):
        error(
            f"mygit-{prefix}: error: mygit repository directory .mygit not found")


def clean_args(usage: str, *args: list[str], params: list[str] = []) -> list[str]:
    """
    Filters and validates command-line arguments against expected parameters.

    Args:
        usage (str): Usage string to display on error.
        *args: Tuple containing argument list (usually sys.argv[1:]).
        params (list): List of accepted optional flags.

    Returns:
        list[str]: A cleaned list of valid arguments.
    """
    cleaned = []
    for arg in args[0]:
        if arg == "--":
            continue
        if arg[0] == "-" and arg != "-":
            if arg in params:
                cleaned.append(arg)
            else:
                error(usage)
        else:
            cleaned.append(arg)

    return cleaned


def error(message: str) -> None:
    """
    Custom error thrower, to avoid repetition (DRY)

    Args:
        message (str): The error message to display.
    """
    print(message, file=sys.stderr)
    exit(1)


def filename_check(filename: str, exists: bool = False, prefix="add", strict=True) -> None | bool:
    """
    Validates a filename from what the spec wants, and optional existence checks.

    Args:
        filename (str): The filename to check.
        exists (bool): If True, ensures the file physically exists.
        prefix (str): Command name prefix used in error messages.
        strict (bool): If True, raises error on failure; otherwise returns False.

    Returns:
        bool or None: True if valid, False if invalid and not strict, otherwise raises error.
    """
    if filename == '' or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]*', filename):
        strict and error(
            f"mygit-{prefix}: error: invalid filename '{filename}'")
        return False

    if exists and not os.path.isfile(filename):
        strict and error(f"mygit-{prefix}: error: can not open '{filename}'")
        return False

    return True


def is_valid_branch_name(name: str) -> bool:
    """
    Checks if the name of a branch is valid (regex pattern)

    Args:
        name (str): Desired name for the branch

    Returns:
        bool: Whether it is valid or not
    """
    return bool(re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]*', name))


def load_index() -> dict:
    """
    Loads the index file into a dictionary mapping filenames to SHA1 hashes.

    Returns:
        dict: The parsed index as {filename: sha1}.
    """
    index = {}
    with open(INDEX_FILE) as f:
        for line in f:
            if line.strip():
                fname, sha1 = line.strip().split()
                index[fname] = sha1
    return index


def save_index(index: dict) -> None:
    """
    Writes the given index dictionary to the index file.

    Args:
        index (dict): The index mapping {filename: sha1} to save.
    """
    with open(INDEX_FILE, "w") as f:
        for fname, sha1 in index.items():
            f.write(f"{fname} {sha1}\n")


def autostage_index() -> None:
    """
    Updates the index with the latest contents of all files currently tracked.
    """
    index = load_index()
    for fname in list(index.keys()):
        if os.path.isfile(fname):  # Only if file still exists. TEST THIS!
            with open(fname, "rb") as f:
                index[fname] = add_file(f.read())
    save_index(index)


def is_index_changed(commit_number: int, index: dict) -> bool:
    """
    Determines whether the current index differs from the specified commit.

    Args:
        commit_number (int): The number of the last commit.
        index (dict): The current index to compare.

    Returns:
        bool: True if there are any differences; False otherwise.
    """
    commit_path = os.path.join(COMMITS_DIR, str(commit_number))
    if not os.path.exists(commit_path):
        return True  # No previous commit: always a change

    last_commit = {}
    with open(commit_path) as f:
        for line in f:
            if line.strip():
                fname, sha1 = line.strip().split()
                last_commit[fname] = sha1

    # Compare all keys from both index and last commit
    all_files = set(index) | set(last_commit)
    for fname in all_files:
        if index.get(fname) != last_commit.get(fname):
            return True

    return False


def get_prev_file_sha1(filename: str) -> str | None:
    """
    Gets the SHA1 hash of the given file from the most recent commit.

    Args:
        filename (str): The file to look up.
        branch (optional): Placeholder for future branch support.

    Returns:
        str or None: The SHA1 hash if found, otherwise None.
    """
    if get_next_commit_num() == 0:
        return None

    branch = read_head()

    commit_number = get_commit_number_for_branch(branch)
    commit_path = os.path.join(COMMITS_DIR, str(commit_number))

    if not os.path.exists(commit_path):
        return None

    with open(commit_path) as f:
        for line in f:
            if line.strip():
                fname, sha1 = line.strip().split()
                if fname == filename:
                    return sha1

    return None


def get_last_commit_sha1(filename: str, branch: Any = None) -> str | None:
    """
    Searches commit history for the most recent SHA1 of the specified file.

    Not used (I think?), but thought to keep it juuuust in case.

    Args:
        filename (str): File to search for in previous commits.
        branch (optional): Placeholder for branch support.

    Returns:
        str or None: SHA1 of the most recent version of the file, or None if not found.
    """
    commit_number = get_next_commit_num()
    if commit_number == 0:
        return None  # No commits yet

    for i in reversed(range(commit_number)):
        path = os.path.join(COMMITS_DIR, str(i))
        if not os.path.exists(path):
            continue
        with open(path) as f:
            for line in f:
                if line.strip():
                    fname, sha1 = line.strip().split()
                    if fname == filename:
                        return sha1
    return None


def add_file(data: str) -> str:
    """
    Stores a file's blob into the object store and returns its SHA1.

    Args:
        data (str): Raw file data to compress and store.

    Returns:
        str: SHA1 hash of the blob (like a fingerprint for the file).
    """
    sha1, content = sha1_hash_blob(data), compressed_blob(data)
    folder, obj_name = sha1[:2], sha1[2:]
    obj_dir = os.path.join(ROOT, "objects", folder)
    obj_path = os.path.join(obj_dir, obj_name)

    if not os.path.exists(obj_path):
        os.makedirs(obj_dir, exist_ok=True)
        with open(obj_path, "wb") as out:
            out.write(content)

    return sha1


def sha1_hash_blob(data: bytes) -> str:
    """
    Computes the SHA1 hash of the given data.
    This is very similar to what the implementation did. It is not
    necessary, but I thought it would be a good challenge.

    Args:
        data (bytes): File content in bytes.

    Returns:
        str: SHA1 hex digest.
    """
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def compressed_blob(data: str) -> bytes:
    """
    Compresses data in blob format using zlib.

    Args:
        data (str): Raw file content.

    Returns:
        bytes: Compressed blob content.
    """
    blob = f"blob {len(data)}\0".encode() + data
    return zlib.compress(blob)


def decompress_blob(data: bytes) -> str:
    """
    Decompresses a blob object and extracts its file content.

    The input is expected to be in the Git blob format: 
    b'blob <size>\\0<content>'.
    This function removes the header  and returns only the file content as
    a string.

    Args:
        data (bytes): The compressed blob data.

    Returns:
        str: The decompressed file content.
    """
    return zlib.decompress(data).split(b'\0', 1)[1]


def get_next_commit_num() -> int:
    """
    Determines the next available commit number.

    Returns:
        int: The next sequential commit number.
    """
    commit_number = 0
    while os.path.exists(os.path.join(COMMITS_DIR, str(commit_number))):
        commit_number += 1
    return commit_number


def is_valid_commit(commit: int | str) -> bool:
    """
    Checks whether the given commit number or name corresponds to a valid commit.

    Args:
        commit (int or str): Commit number or name.

    Returns:
        bool: True if the commit exists; False otherwise.
    """
    return os.path.exists(os.path.join(COMMITS_DIR, str(commit)))


def is_valid_branch(branch: str) -> bool:
    """
    Checks whether the given branch corresponds to a valid branch.

    Args:
        commit (int or str): Target branch name.

    Returns:
        bool: True if the branch exists; False otherwise.
    """
    return os.path.exists(os.path.join(BRANCHES_DIR, branch))


def unpack_commit(commit_number: int | str) -> dict:
    """
    Unpacks a `.pack` file associated with a commit and returns its file contents.
    The file still needs to be decompressed using .decompress(blob)

    Args:
        commit_number (int): The commit number to unpack.

    Returns:
        dict: A mapping of {filename: blob_data} for that commit.
    """
    pack_path = os.path.join(COMMITS_DIR, f"{commit_number}.pack")
    if not os.path.exists(pack_path):
        error(f"Pack file for commit {commit_number} not found")

    files = {}
    with open(pack_path, "rb") as pack:
        while True:
            fname_len_bytes = pack.read(2)
            if not fname_len_bytes:
                break  # EOF

            fname_len = int.from_bytes(fname_len_bytes, 'big')
            fname = pack.read(fname_len).decode()

            blob_len = int.from_bytes(pack.read(4), 'big')
            blob = pack.read(blob_len)

            files[fname] = blob

    return files


def read_head() -> str:
    """
    Reads the current branch name from .mygit/HEAD.

    Returns:
        str: The current branch name.
    """
    with open(HEAD_FILE, "r") as f:
        return f.read().strip()


def write_head(branch: str) -> None:
    """
    Writes the current branch name to .mygit/HEAD.

    Args:
        branch (str): Branch name to write.
    """
    with open(HEAD_FILE, "w") as f:
        f.write(branch)


def get_commit_number_for_branch(branch: str, prefix: str = "checkout") -> str:
    """
    Retrieves the commit number that the given branch points to.

    Args:
        branch (str): The branch name.

    Returns:
        str: The commit number (as string).
    """
    branch_path = os.path.join(BRANCHES_DIR, branch)

    if not os.path.isfile(branch_path):
        error(f"mygit-checkout: error: unknown branch '{branch}'")

    with open(branch_path) as f:
        return int(f.read().strip())


def get_commit_files(commit_num: str) -> dict[str, str]:
    """
    Reads the .mygit/commits/<commit_num> file to get the file -> sha1 mapping.

    Args:
        commit_num (str): The commit number to read.

    Returns:
        dict[str, str]: Mapping of filenames to their blob sha1 hashes.
    """
    commit_path = os.path.join(COMMITS_DIR, str(commit_num))
    files = {}
    if not os.path.exists(commit_path):
        return files  # No files yet for this commit
    with open(commit_path) as f:
        for line in f:
            if line.strip():
                fname, sha1 = line.strip().split()
                files[fname] = sha1
    return files


def create_pack(commit_number: int, index: dict) -> None:
    """
    Create a compressed .pack file for the given commit number using the current index.

    Each entry in the index is written to the pack file in the following binary format:
    - 2 bytes: length of the filename
    - N bytes: UTF-8 encoded filename
    - 4 bytes: length of the file's blob data
    - M bytes: compressed blob data (from the objects store)

    This whole system is an artifact of me trying to copy the reference
    implementation... Decided to keep it because I felt like it would be a nice
    challenge to try out.

    Args:
        commit_number (int): The numeric ID for the commit
        index (dict): A mapping of filenames to their SHA1 blob hashes

    Returns:
        None
    """
    with open(os.path.join(COMMITS_DIR, f"{commit_number}.pack"), "wb") as pack_file:
        for fname, sha1 in index.items():
            folder, name = sha1[:2], sha1[2:]
            with open(os.path.join(OBJECTS_DIR, folder, name), "rb") as f:
                data = f.read()

            fname_bytes = fname.encode()
            pack_file.write(len(fname_bytes).to_bytes(2, 'big'))
            pack_file.write(fname_bytes)
            pack_file.write(len(data).to_bytes(4, 'big'))
            pack_file.write(data)


def get_all_tracked_files() -> set[str]:
    """
    Collect all filenames that are relevant to repository tracking.

    This includes:
    - Files in the current working directory that pass filename checks;
    - Files currently staged in the index;
    - Files previously committed in the latest commit.

    Returns:
        set[str]: Sorted list of all tracked or trackable filenames
    """
    branch = read_head()
    branch_path = os.path.join(BRANCHES_DIR, branch)

    index = load_index()
    working = [f for f in os.listdir(".") if os.path.isfile(f)]

    # If no commits exist
    if not os.path.isfile(branch_path):
        return sorted(set(index.keys()) | set(working))

    commit_num = get_commit_number_for_branch(branch)
    commit_files = unpack_commit(commit_num)

    return sorted(set(commit_files) | set(index.keys()) | set(working))


def create_commit(index: dict[str, str], message: str, extra_parents: list[int] | None = None) -> int | None:
    """
    Create a new commit object, write all repository metadata and return
    the new commit number.

    Args:
        index: Current staging index mapping filename -> sha1.
        message: The *single-line* commit message to record in .mygit/log.
        extra_parents: Any additional parent commits (e.g. the *other* side of
                        a merge).  mygit-commit should pass None (or
                        an empty list). mygit-merge should pass a *list*
                        containing the commit number it merged *from*.

    Returns:
        int: the freshly allocated commit number (zero-based).
    """
    if extra_parents is None:
        extra_parents = []

    commit_no = get_next_commit_num()

    if commit_no == 0:
        os.makedirs(BRANCHES_DIR, exist_ok=True)
        with open(os.path.join(BRANCHES_DIR, "trunk"), "w") as f:
            f.write("0")
        with open(HEAD_FILE, "w") as f:
            f.write("trunk")

    if (commit_no == 0 and not index) or (
            commit_no > 0 and not is_index_changed(commit_no - 1, index)):
        return None

    # Write commit mapping
    commit_list_path = os.path.join(COMMITS_DIR, str(commit_no))
    with open(commit_list_path, "w", encoding="utf-8") as out:
        for fname, sha in sorted(index.items()):
            out.write(f"{fname} {sha}\n")

    # Write pack file
    create_pack(commit_no, index)

    # Update log
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{commit_no} {message}\n")

    # Update DAG
    if commit_no == 0:
        add_node(commit_no, [])
    else:
        current_branch = read_head()
        primary_parent = int(get_commit_number_for_branch(current_branch))
        all_parents = [primary_parent] + extra_parents

        for parent in all_parents:
            try:
                add_node(parent, [])
            except ValueError:
                pass  # Parent already exists

        add_node(commit_no, all_parents)

    # Move branch pointer
    with open(os.path.join(BRANCHES_DIR, read_head()), "w", encoding="utf-8") as ref:
        ref.write(str(commit_no))

    return commit_no


def restore_commit(commit_num: str, prev_commit_files: dict[str, str]) -> None:
    """
    Switches the working directory and index to the state of the given commit.
    NOTE: This implementation does NOT seem like actual git. Specifically,
    test subset2_25 implies that unstaged changes carry over. I don't believe
    that is correct, but I don't really have a choice.

    This:
    - Deletes any files tracked in the previous commit;
    - Restores files from the target commit to the working directory;
    - Updates the index accordingly;
    - Preserves any uncommitted changes in tracked files.

    Args:
        commit_num (str): The target commit number to restore.
        prev_commit_files (dict[str, str]): Mapping of filenames to SHA1s in the current commit.
    """
    files_in_target = unpack_commit(commit_num)
    index_before = load_index()
    tracked_files = get_all_tracked_files()

    # We need to backup uncommitted changes (index != repo)
    backup = {}
    for fname in tracked_files:
        if not os.path.isfile(fname):
            continue
        with open(fname, "rb") as f:
            content = f.read()
        working_sha = sha1_hash_blob(content)
        index_sha = index_before.get(fname)
        commit_sha = prev_commit_files.get(fname)
        if index_sha != commit_sha or working_sha != index_sha:
            backup[fname] = content

    # Flushing out all the files from the previous commit
    for fname in tracked_files:
        if fname in prev_commit_files and os.path.exists(fname):
            os.remove(fname)

    # Restoring to former glory!
    target_sha = {}
    for fname, blob in files_in_target.items():
        data = decompress_blob(blob)
        with open(fname, "wb") as f:
            f.write(data)
        target_sha[fname] = sha1_hash_blob(data)

    # Updating the index (shallow copy is fine, but may need to change if index
    # structure changes)
    new_index = index_before.copy()
    for fname, prev_sha in prev_commit_files.items():
        if fname in index_before and index_before[fname] == prev_sha:
            if fname in target_sha:
                new_index[fname] = target_sha[fname]
            else:
                new_index.pop(fname, None)

    for fname, sha in target_sha.items():
        if fname not in new_index:
            new_index[fname] = sha

    # Restoring backups from before
    for fname, data in backup.items():
        with open(fname, "wb") as f:
            f.write(data)

    save_index(new_index)


def get_conflicts(index: dict[str, str], target_commit: str) -> list[str]:
    """
    Determines which files would be overwritten by checking out the given commit.

    A conflict is detected if all of the following conditions are met:
    - Exists in both the working directory and the target commit;
    - Has uncommitted changes not reflected in the index;
    - Those index changes don't match the target commit.

    Args:
        index (dict[str, str]): Current index mapping of filenames to SHA1 hashes.
        target_commit (str): The commit number (as string) of the branch to check out.

    Returns:
        list[str]: List of conflicting filenames that would be overwritten.
    """
    conflicts = []
    target_blobs = unpack_commit(target_commit)
    for fname, blob in target_blobs.items():
        if not os.path.exists(fname):
            continue
        with open(fname, "rb") as f:
            working_sha = sha1_hash_blob(f.read())

        index_sha = index.get(fname)
        target_sha = sha1_hash_blob(decompress_blob(blob))

        # Conflict only if working != index and index != target
        if index_sha is None or (working_sha != index_sha and index_sha != target_sha):
            conflicts.append(fname)

    return conflicts


def working_directory_would_be_overwritten(target_commit: str) -> bool:
    """
    Checks if the working directory would be overwritten in the case of changing
    branches or merging.

    Args:
        target_commit (str): Which commit number do you want to check

    Returns:
        bool: True of unsafe to change
    """
    tracked_files = get_all_tracked_files()
    index = load_index()
    commit_files = get_commit_files(target_commit)

    for fname in tracked_files:
        if not os.path.isfile(fname):
            continue  # deleted locally — not a problem

        with open(fname, "rb") as f:
            working_sha = sha1_hash_blob(f.read())

        index_sha = index.get(fname)
        commit_sha = commit_files.get(fname)

        # If working copy doesn't match either index or commit, it's unstaged
        if working_sha != index_sha and working_sha != commit_sha:
            return True

    return False


def get_merge_conflicts(
    base: dict[str, str],
    ours: dict[str, str],
    theirs: dict[str, str]
) -> list[str]:
    """
    Returns filenames that have conflicting changes between ours and theirs
    relative to the base.

    A true conflict occurs when:
    - base != ours
    - base != theirs
    - ours != theirs

    Args:
        base (dict[str, str]): base commit file -> sha1
        ours (dict[str, str]): current commit file -> sha1
        theirs (dict[str, str]): target commit file -> sha1

    Returns:
        list[str]: list of filenames with 3-way conflicts
    """
    all_files = set(base) | set(ours) | set(theirs)
    conflicts = []

    for fname in sorted(all_files):
        base_sha = base.get(fname)
        our_sha = ours.get(fname)
        their_sha = theirs.get(fname)

        if (base_sha != our_sha and
            base_sha != their_sha and
                our_sha != their_sha):
            conflicts.append(fname)

    return conflicts


def get_commit_message(commit_number: int) -> str:
    """
    Returns the commit message associated with the given commit number.

    Args:
        commit_number (int): The commit number.

    Returns:
        str: The commit message, or "unknown" if not found.
    """
    if not os.path.exists(LOG_FILE):
        return None

    with open(LOG_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                num, msg = line.split(" ", 1)
                if int(num) == commit_number:
                    return msg
            except ValueError:
                continue

    return None
