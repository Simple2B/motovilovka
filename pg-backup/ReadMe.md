# pg-backup

Backup Postgres db and data files to mounted volume /backup

## Usage

Docker Compose:

```yaml
database:
  image: postgres:12
  environment:
    POSTGRES_USER: user
    POSTGRES_PASSWORD: password

backup:
  build: istacat/pg-backup
  links:
    - database
  environment:
    SCHEDULE: "@daily"
    POSTGRES_DATABASE: dbname
    POSTGRES_USER: user
    POSTGRES_PASSWORD: password
    POSTGRES_EXTRA_OPTS: "--schema=public --blobs"
```

### Automatic Periodic Backups

You can additionally set the `SCHEDULE` environment variable like `-e SCHEDULE="@daily"` to run the backup automatically.

More information about the scheduling can be found [here](http://godoc.org/github.com/robfig/cron#hdr-Predefined_schedules).

### Manually create backup

For manually run database backup you need goto project folder and execute the following line.

```bash
docker-compose exec backup sh backup.sh
```

### Manually restore latest stored backup

For restore the latest backup you need goto project folder and execute the following line.

```bash
docker-compose exec backup sh restore.sh
```

**Warning!**
This will potentially put your database in a very bad state or complete destroy your data, be very careful.
