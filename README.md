# BackupMySys

A command line backup tool to keep your files stored at dropbox by using its API. It runs at given time intervals specified by the user and can perform automatic backups using cronjobs.

To run the backup use the following syntax:

```sh
$ python backup.py --from-dir <path_to_dir> --to-dir <folder_to_upload> --backup-start <time_in_minutes> --frequency-interval <time in minutes> --automatic-backup <true|false>
```

The "--form-dir" argument must be a valid path, otherwise it will raise an error.


### Todo 

- [X] Parse command line arguments
- [X] Traverse the target directory with os.walk
- [X] Set up a logger object
- [ ] Set up Dropbox API
- [ ] Upload the directory to dropbox
- [ ] Run crontab jobs as specified in the arguments