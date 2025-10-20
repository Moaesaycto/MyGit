# MyGit

MyGit was a COMP2041 project that involved implementing Git from scratch using Python (and Shell for testing). When a project was added, it was stored in the head until it was commited. The version of the file was stored using a a content-addressable storage (CAS) scheme, where the file’s name or path is derived from its hash. A hash-prefix partitioning was used to manually hash the location of the file for extremely quick look-ups even with many files.

The project also included manual version control, as well as branches and merging (which was an absolute nightmare). Most of it is functional except for one small bug when checking out from a branch.

Just like the other assignment from this course, there is a manual testing script that compares the outputs of my implementation to the outputs of the reference implementation. Unlike the previous assignment, this one creates a mini virtual environment to initialise the mygit repositories, so that they do not affect each other when files are moved and items are changed. It also compares to make sure that the exact same files (with the exact same contents) are present in both directories each step of the way. If there was a single thing wrong in any aspect, this testing script would alert me.

- `mygit-init` creates a new repository; initialises metadata and object storage.
- `mygit-add` stages file changes for the next commit (hashes and stores them).
- `mygit-rm` removes files from the working tree and staging area.
- `mygit-show` displays the contents or details of a specific object or commit.
- `mygit-branch` lists, creates, or deletes branches.
- `mygit-log` shows the commit history.
- `mygit-status` displays current branch, staged and unstaged changes.
- `mygit-checkout` switches branches or restores files from a commit.
- `mygit-merge` merges changes from one branch into another.
- `mygit-commit` records staged changes as a new commit with a message and metadata.

**If you want me to make this project private, please let me know and I will do so immediately.**
