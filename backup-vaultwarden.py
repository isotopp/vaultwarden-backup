#! /usr/bin/env python3

from shutil import copytree, ignore_patterns, make_archive, rmtree
from pathlib import Path
from datetime import datetime
import time
import sys
import subprocess


class Backup:
    """
    Make a backup of a vaultwarden installation.

    We create a backups directory, in which we create a staging subdirectory.
    Files are copied into the stage, according to the instructions in
    https://github.com/dani-garcia/vaultwarden/wiki/Backing-up-your-vault.
    The stage is then archives into a .tar.bz2, and removed.
    """

    # Path to sqlite3 binary
    sqlite3 = "/usr/bin/sqlite3"

    def __init__(self,
                 datadir="/export/vaultwarden/vaultwarden",
                 backupdir="/export/vaultwarden/backups",
                 debug=False):
        """ Constructor.
        datadir: Location of the vaultwarden installation. Must be readable to the program.
        backupdir: Location where the staging subdirectory will be created. Later the .tar.bz2 will be left here.
            The staging directory will be {backupdir}/backup-{now}.
        debug: prints some messages when set to True (Default: False).
        """
        self.now = datetime.now().strftime("%Y%m%d-%H%M%S")

        self.debug = debug
        self.datadir = Path(datadir)
        self.backupdir = Path(backupdir)
        self.stagedir = self.backupdir / f"backup-{self.now}"

    def make_staging(self):
        """ Create the staging directory. """
        if self.debug:
            print(f"Making staging {self.stagedir}")
        Path(self.stagedir).mkdir(parents=True, exist_ok=False)

    def cleanup_staging(self):
        """ Remove the staging directory. """
        if self.debug:
            print(f"Remove staging {self.stagedir}.")
        rmtree(self.stagedir, ignore_errors=False)

    def backup_db(self):
        """ Make a backup of the sqlite3 database separately, using the .backup command for database backups. """

        data_dbfile = self.datadir / "db.sqlite3"
        backup_dbfile = self.stagedir / "db.sqlite3"
        cmd = [self.sqlite3, data_dbfile, f".backup {backup_dbfile}"]
        if self.debug:
            print(f"backup_db: {cmd=}")

        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.SubprocessError as e:
            print(f"Failed: {e}")
            sys.exit(1)

    def backup_everything_else(self):
        """ Using copytree(), we make a copy of all things except the database. """
        if self.debug:
            print(f"Copy files from {self.datadir} to {self.stagedir}.")
        copytree(self.datadir, self.stagedir, dirs_exist_ok=True, ignore=ignore_patterns('db.sqlite3*'))

    def backup_bztar(self):
        """ Compress the staging directory into a .tar.bz2. """
        if self.debug:
            print(f"Archive {self.stagedir} into {self.stagedir}.tar.bz2.")

        make_archive(str(self.stagedir), "bztar", self.stagedir)

    def backup(self):
        self.make_staging()

        self.backup_everything_else()
        self.backup_db()

        self.backup_bztar()
        self.cleanup_staging()

    def expire(self, days=365.0):
        """ Expire Backups older than days (default: 365). """
        now = time.time()
        cutoff = now - days * 86400

        for p in self.backupdir.glob("*.tar.bz2"):
            ctime = p.stat().st_ctime
            if ctime < cutoff:
                if self.debug:
                    print(f"Expire file {p} ({ctime=} {cutoff=}).")
                p.unlink()
            else:
                if self.debug:
                    print(f"File {p} still good ({ctime=} {cutoff=}).")


b = Backup()
b.backup()
b.expire()
