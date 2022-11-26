# Vaultwarden backup

I needed to make a backup of my vaultwarden installation, and I hate Shellscripts.
So I wrote a Python script, using only stdlib functions to perform the job.

```
root@server:/export/vaultwarden# tree -d
.
├── backups
├── bin
└── vaultwarden
    ├── attachments
    ├── icon_cache
    ├── sends
    └── tmp

7 directories
```

The script will backup all files from `/export/vaultwarden/vaultwarden` 
to a staging directory below `/export/vaultwarden/backups`.
The staging directory will then be collected into a `.tar.bz2` archive,
which is left in `/export/vaultwarden/backups`, and the stage is removed.

A Python class `Backup` accepts the `datadir` and `backupdir` parameters.
`datadir` is in my case `/export/vaultwarden/vaultwarden`, and backupdir
is `/export/vaultwarden/backups`.
A parameter `debug` can be set to `True` for some output, it is `False` by default.