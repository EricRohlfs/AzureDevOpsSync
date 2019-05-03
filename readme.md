# AzrueDevOpsSync

One way sync of git repositories between two AzureDevOps instances when one is on prems and does not have a public ip address.


## Security

Do not check in your config file.  The .gitignore file is set to ignore .cfg files.

Make sure the on prems version of AzureDevOps has https set up. Http will not work with git when passing credentials.

## Current Desing Strategy

Since cloning could take quite a while, the current plan is to have this script generate the various scripts.
They can then be executed manually or by being called form another 'master' script.


## Getting Started

### Make default.cfg

In the code folder, rename the default_cfg.txt file to default.cfg and change the values.

## Syncing code between two VSTS Projects

Run the SyncRepos.py script

    python SyncRepos.py

The look in the folder that was set for the GitRootFolderPath in the default.cfg file.

    git_clone_missing.bat
    git_set_remotes.bat
    git_fetch_push.bat

## Initial Flow

User logs onto AzureDevOps on Server1, does a repo import. Now Server1 will be the primary data source for what repos are updated.

The SyncRepos.py, runs on Server1 on a daily schedule and does it's thing.

(Note: since 

## Use case

In a world, where a team has two on prems versions of AzureDevOps, behind firewalls and only Server2 public IP Addresses ...

### Use Case

A repo on Server2 updates, when the script runs, the repo on Server1 should have all the updates.

### Use Case

When a new repo is created on Server2, Server1 needs to know about it. This will be a manual process see Initial Flow.
