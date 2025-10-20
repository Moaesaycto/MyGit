# **MyGit**

**Type:** Version Control System · **Tech Stack:** Python, Shell (for testing) · **Status:** Completed

## **Overview**

**MyGit** was a **COMP2041** project recreating the essential features of Git from scratch. It implements content-addressable storage, branching, merging, and metadata management entirely in Python, with Bash scripts used for extensive regression testing.

## **Features**

* `mygit-init`: Initialise a new repository with metadata and object storage.
* `mygit-add`: Stage file changes; compute hashes for CAS storage.
* `mygit-rm`: Remove files from working tree and staging area.
* `mygit-show`: Display contents or metadata of commits/objects.
* `mygit-branch`: Create, list, or delete branches.
* `mygit-log`: Show commit history.
* `mygit-status`: Display current branch and file change states.
* `mygit-checkout`: Switch branches or restore files from commits.
* `mygit-merge`: Merge branches (mostly functional, with one minor checkout bug).
* `mygit-commit`: Record staged changes with message and timestamp.

## **Testing and Validation**

Includes a **virtualised test harness** that:

* Spins up isolated environments for each repository test.
* Compares MyGit’s output and file states against the **reference Git implementation**.
* Flags any discrepancy between expected and actual results; even a single byte difference.

## **Purpose**

Built to deeply understand the internal mechanisms of Git: particularly **content-addressable storage**, **branching logic**, and **merge conflicts**: while gaining experience in robust testing and debugging of large script-based systems.

*(Note: Can be made private upon request.)*
