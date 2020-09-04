from settings import IGNORE_DIRS, IGNORE_FILES
from datetime import datetime, time
from pathlib import Path
import logging
import shutil
import click
import os



@click.command()
@click.option(
    "--from-dir",
    help="Directory to backup/watch if --automatic-sync is enabled",
    type=click.Path(exists=True),
    required=True   
)
@click.option(
    "--to-dir",
    help="Root directory to store the backup",
    type=click.Path(exists=False),
    required=True
)
@click.option(
    "--backup-start",
    help="Perform the backup in the given time interval (in minutes)",
    type=click.INT,
    required=True
)
@click.option(
    "--frequency-interval",
    help="Interval of time (in minutes) to perform the backups",
    type=click.INT,
    required=True
)
@click.option(
    "--automatic-backup",
    help="Whether to perform or not automatic back ups by using cron jobs",
    type=click.BOOL,
    required=True
)
def main(from_dir, to_dir, backup_start, frequency_interval, automatic_backup):
    """
        A command line backup tool to keep your files stored at dropbox by using its API. 
        It runs at given time intervals specified by the user and can perform automatic
        backups using cronjobs
    """

    logging.basicConfig(
        filename="./backup.log",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    FROM_DIR = Path(from_dir)
    TO_DIR = Path(to_dir)
    BACKUP_START_TIME = backup_start
    FREQUENCY_INTERVAL = frequency_interval
    AUTOMATIC_BACKUP = automatic_backup

    click.secho(f"Backing up {str(FROM_DIR)} into {str(TO_DIR)} at {str(BACKUP_START_TIME)} every {str(FREQUENCY_INTERVAL)}", fg="green")

    VISITED = []
    TMP_DIR = Path.cwd()/"tmp"
    try:
        os.mkdir(TMP_DIR)
    except:
        pass
    BUILD_PATH = list(TMP_DIR.parts)
    print("Starting build path = ", BUILD_PATH)

    # Start from the root directory
    for root, dirs, files in os.walk(FROM_DIR):
        CURRENT_DIR = os.path.basename(root)
        logging.info("Visiting %s", root)
        if CURRENT_DIR in VISITED:
            VISITED.remove(CURRENT_DIR)
            PARENT_DIR = "/".join(BUILD_PATH)+"/"
            if CURRENT_DIR not in os.listdir(PARENT_DIR):
                _ = BUILD_PATH.pop()
            BUILD_PATH.append(CURRENT_DIR)
            # logging.info("Visiting %s", "/".join(BUILD_PATH)[1:])

        
        if files:
            os.chdir(root)
            logging.info("%s has %s files", CURRENT_DIR, len(files))
            for FILE in files:
                if FILE not in IGNORE_FILES:
                    shutil.copy(FILE, "/".join(BUILD_PATH)[1:]+"/")   # This the same [1]
                else:
                    logging.warning("Ignoring the file %s", FILE)

        if dirs:
            logging.info("%s has %s files", CURRENT_DIR, len(dirs))
            for DIR in dirs:
                if DIR not in IGNORE_DIRS:
                    VISITED.append(DIR)
                    try:
                        os.mkdir("/".join(BUILD_PATH)[1:]+"/"+DIR)    # This the same [1]
                    except:
                        pass
                else:
                    logging.warning("Ignoring %s directory", DIR)
        else:
            logging.info("%s has no directories", CURRENT_DIR)
            if CURRENT_DIR not in IGNORE_DIRS:
                BUILD_PATH.remove(CURRENT_DIR)


if __name__ == "__main__":
    main()