# AzrueDevOpsSync

One way sync of git repositories between two AzureDevOps instances when one is on prems and does not have a public ip address.


## Security

Do not check in your config file.  The .gitignore file is set to ignore .cfg files.

Make sure the on prems version of AzureDevOps has https set up. Http will not work with git when passing credentials.

## Getting Started

### Make default.cfg

In the code folder, rename the default_cfg.txt file to default.cfg and change the values.

## Syncing code between two VSTS Projects

python SyncRepos.py

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
