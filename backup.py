from settings import IGNORE_DIRS, IGNORE_FILES
from DBoxConnection import DBoxConnection
from datetime import datetime, time
from crontab import CronTab
from pathlib import Path
import logging
import dropbox
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
@click.option(
    "--upload-zip",
    help="If the backup will be uploaded as a zipped file",
    type=click.BOOL,
    required=True
)
def main(from_dir, to_dir, backup_start, frequency_interval, automatic_backup, upload_zip):
    """
        A command line backup tool to keep your files stored at dropbox by using its API. 
        It runs at given time intervals specified by the user and can perform automatic
        backups using cronjobs
    """

    FROM_DIR = Path(from_dir)
    TO_DIR = Path(to_dir)
    BACKUP_START_TIME = backup_start
    FREQUENCY_INTERVAL = frequency_interval
    AUTOMATIC_BACKUP = automatic_backup

    logging.basicConfig(
        filename="./backup.log",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )


    # Dropbox connection object
    # Handling the backup folder creation skip if already exist 
    dbox = DBoxConnection()
    
    if dbox.validate_token():
        logging.info("The dropbox auth token is valid")
    else:
        logging.error("The dropbox token is not valid, get a new one")

    if TO_DIR.name not in dbox.get_dirs("", only_names=True, recursive=False):
        dbox.create_folder(TO_DIR)
        logging.info("The backup directory %s was created in dropbox")
    else:
        logging.warning("The backup directory %s already exists in dropbox", TO_DIR)


    # Setting up the cron jobs 
    # cron = CronTab(user=True)
    # job = cron.new(command="")
    # job.setall(datetime(year, month, day, hour, minute))
    # datetime.strptime(date_string=)

    click.secho(f"Backing up {str(FROM_DIR)} into {str(TO_DIR)} at {str(BACKUP_START_TIME)} every {str(FREQUENCY_INTERVAL)}", fg="green")

    # Traverse the directory to backup, skip the files and dirs that must be ignored
    VISITED = []
    TMP_DIR = Path.cwd()/"tmp"
    try:
        os.mkdir(TMP_DIR)
    except:
        pass

    if upload_zip:
        BUILD_PATH = list(TMP_DIR.parts)
    else:
        BUILD_PATH = list(TO_DIR.parts)

    print("Starting build path = ", BUILD_PATH)

    for root, dirs, files in os.walk(FROM_DIR):
        CURRENT_DIR = os.path.basename(root)
        logging.info("Visiting %s", root)
        print("Build path -> ", BUILD_PATH)
        if CURRENT_DIR in VISITED:
            VISITED.remove(CURRENT_DIR)
            PARENT_DIR = ("/".join(BUILD_PATH))[1:]
            print(PARENT_DIR)
            if upload_zip:
                if CURRENT_DIR not in os.listdir(PARENT_DIR):
                    _ = BUILD_PATH.pop()
            else:
                if CURRENT_DIR not in dbox.get_dirs(PARENT_DIR, only_names=True, recursive=False):
                    _ = BUILD_PATH.pop()
            BUILD_PATH.append(CURRENT_DIR)
        
        if files:
            os.chdir(root)
            logging.info("%s has %s files", CURRENT_DIR, len(files))
            for FILE in files:
                print("File = ", FILE)
                if FILE not in IGNORE_FILES:
                    if upload_zip:
                        shutil.copy(FILE, "/".join(BUILD_PATH)[1:]+"/")
                    else:            
                        with open(FILE, 'rb') as f:
                            try:
                                dbox.upload_content(file=f.read(), path="/".join(BUILD_PATH)[1:]+"/"+f.name)
                                print("File uploaded")
                            except dropbox.exceptions.ApiError as error:
                                if error.error.is_path():
                                    logging.error("Path error")
                else:
                    logging.warning("Ignoring the file %s", FILE)

        if dirs:
            logging.info("%s has %s files", CURRENT_DIR, len(dirs))
            for DIR in dirs:
                if DIR not in IGNORE_DIRS:
                    VISITED.append(DIR)
                    try:
                        if upload_zip:
                            os.mkdir("/".join(BUILD_PATH)[1:]+"/"+DIR)
                        else:
                            dbox.create_folder("/".join(BUILD_PATH)[1:]+"/"+DIR)    
                        logging.info("Creating folder %s at %s", DIR, "/".join(BUILD_PATH)[1:])
                    except:
                        logging.warning("Folder %s already exist at %s", DIR, "/".join(BUILD_PATH)[1:])
                else:
                    logging.warning("Ignoring %s directory", DIR)
        else:
            logging.info("%s has no directories", CURRENT_DIR)
            if CURRENT_DIR not in IGNORE_DIRS:
                BUILD_PATH.remove(CURRENT_DIR)


if __name__ == "__main__":
    main()


# python backup.py --from-dir "/home/sjukdom/_Narasimha_/_forbackup_/" --to-dir "/Backup" --backup-start 60 --frequency-interval 120 --automatic-backup false