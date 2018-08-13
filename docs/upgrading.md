# Steps to port the database

To backup and restore the database, named, say, 'vicnode':

```bash
# Dump a copy of the db into the file named 'dump.sql'
sudo -u postgres pg_dump vicnode > dump.sql
# Drop the db:
sudo -u postgres dropdb vicnode
# Create a new db
sudo -u postgres createdb -T template0 vicnode
# Restore the db from the file containing the copy
sudo -u postgres psql vicnode < dump.sql > log.txt
# Run the cleanup transform
# from https://stackoverflow.com/questions/9736085/run-a-postgresql-sql-file-using-command-line-arguments
sudo -u postgres psql -d vicnode -a -f heat/db_transform.sql 

# compress the sql dump into the current directory
tar -zcvf dump.sql.tgz ~/Vagrant/VicNode/data/dump.sql
# split the compressed sql dump into multiple 1 meg files:
split -b1m dump.sql.tgz "dump.sql.tgz.part"
# and recombine the files into one 
cat dump.sql.tgz.parta* >dump_rebuilt.sql.tgz
```

```bash
# some useful commands to prepare the database for heat...

# set up an ssh tunnel for pg_dump (where 118.138.240.252 is the IP address
# of the tunnel instance inside the monash data centers)
ssh -i ~/.ssh/tunnel -L 9000:pgsql.its.monash.edu.au:5432 ubuntu@118.138.240.252
# check the 9000 port is open
netstat -na | grep LISTEN
# do the dump to the local machine, skipping the authoken table
/usr/local/bin/pg_dump --if-exists --clean --file=/Users/mpaulo/temp/my_vicnode_dump.sql --dbname=vicnode_prd --username=vicnode_prd_ro --host=localhost --port=9000 -T public.authtoken_token
#/usr/local/bin/pg_dump --if-exists --clean --file=/Users/mpaulo/temp/next_vicnode_dump.sql -T=public.authtoken_token --dbname=vicnode_prd --username=vicnode_prd_ro --host=localhost --port=59621

# earlier versions of the psql client can report the following error messages
# ERROR:  unrecognized configuration parameter "idle_in_transaction_session_timeout"
# ERROR:  unrecognized configuration parameter "row_security"
# a crude fix is to remove the lines that set these flags
sed -i.bak '/idle_in_transaction_session_timeout/d' ./my_vicnode_dump.sql
sed -i.bak '/row_security/d' ./my_vicnode_dump.sql
# compress it
tar -zcvf dump.sql.tgz my_vicnode_dump.sql
# and then encrypt it (remember the password)...  
gpg -c --cipher-algo AES256 dump.sql.tgz


```


Following useful piece of sql gives the sql to drop all of the tables

```sql
SELECT 'DROP TABLE ' || n.nspname || '.' || c.relname || ';' AS "Name"
FROM pg_catalog.pg_class c
  LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r', 'v', 'S', '')
      AND n.nspname <> 'pg_catalog'
      AND n.nspname <> 'information_schema'
      AND n.nspname !~ '^pg_toast'
      AND pg_catalog.pg_table_is_visible(c.oid);
```

```

How the migrations were created:

```bash
# Get a set of django models for the first ingest
python manage.py inspectdb > models.py
```
Then ensured each model has an id field (this is probably not needed, but): 

```python

id = models.AutoField(primary_key=True)

```

and removed the line:

```python

managed = False

```

Then refactored the Model names and modified the field definitions.

Then a fake migration of the application model

```bash
python manage.py makemigrations
python manage.py migrate --fake-initial
```

Then updated the model to remove the fields we don't want and run the migration
again

```bash
python manage.py makemigrations
python manage.py migrate
```

Then create the django superuser

```bash
python manage.py createsuperuser
```



## Thoughts on merging tables...

Create new model (C) that represents the two merged old models (A & B).
Make a normal migration
If there is one, apply it
Create a custom migration `python manage.py makemigration --empty storage`
Edit the file to to do a data migration via code/sql (see below)
Run `python manage.py migrate` to apply the migration
Drop the two models A & B
Generate and run a new migration to get rid of the tables.

So if doing the merge via code, something along the lines of:

```python
from django.db import migrations


def merge_models(apps, schema_editor):
    A = apps.get_model('storage', 'A')
    B = apps.get_model('storage', 'B')
    C = apps.get_model('storage', 'C')
    # join A and B, iterate over and insert into C
    for a in A.objects.all():
        b = a.b
        c = C.objects.create()
        # set c with values from a (and b)
        c.save()


class Migrations(migrations.Migration):
    dependencies = [
        ('storage', 'the_last_migration'),
    ]
    operations = [
        migrations.RunPython(merge_models),
    ]

```

```text
If we could put everything in at the request stage it would be far better...
And less prone to error and replication

```

# Links of interest:

* https://medium.com/@half0wl/server-rendered-charts-in-django-2604f903389d 


## Notes on SOE

```bash
# get rid of unused kernels...
sudo apt autoremove 
# install pip and pyyaml then test the cloud-init config file:
python -c 'import yaml,sys;yaml.safe_load(sys.stdin)' < yamltest.txt

# 

```

```yaml
users:
  - default
  - name: myNewAdminUser
    groups: sudo
    shell: /bin/bash
```