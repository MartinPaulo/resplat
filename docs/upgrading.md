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


Prepare the database for porting:

```sql
-- Table ordering matters
DROP TABLE public.corsheaders_corsmodel;

DROP TABLE public.django_admin_log;
DROP TABLE public.django_migrations;
DROP TABLE public.django_session;

DROP TABLE public.auth_group_permissions;
DROP TABLE public.auth_user_groups;
DROP TABLE public.auth_user_user_permissions;

DROP TABLE public.auth_group;
DROP TABLE public.auth_permission;

DROP TABLE public.django_content_type;

-- Most of the existing tables reference this one, so use cascade to remove
-- all the foreign key constraints
DROP TABLE public.auth_user CASCADE;
```

Drop the CRAMS tables

```sql
DROP TABLE public.crams_allocationhome CASCADE;
DROP TABLE public.crams_computeproduct CASCADE;
DROP TABLE public.crams_computerequest CASCADE;
DROP TABLE public.crams_computerequestquestionresponse CASCADE;
DROP TABLE public.crams_contact CASCADE;
DROP TABLE public.crams_contactrole CASCADE;
DROP TABLE public.crams_domain CASCADE;
DROP TABLE public.crams_duration CASCADE;
DROP TABLE public.crams_forcode CASCADE;
DROP TABLE public.crams_fundingbody CASCADE;
DROP TABLE public.crams_fundingscheme CASCADE;
DROP TABLE public.crams_grant CASCADE;
DROP TABLE public.crams_granttype CASCADE;
DROP TABLE public.crams_project CASCADE;
DROP TABLE public.crams_projectcontact CASCADE;
DROP TABLE public.crams_projectid CASCADE;
DROP TABLE public.crams_projectidsystem CASCADE;
DROP TABLE public.crams_projectquestionresponse CASCADE;
DROP TABLE public.crams_provider CASCADE;
DROP TABLE public.crams_publication CASCADE;
DROP TABLE public.crams_question CASCADE;
DROP TABLE public.crams_request CASCADE;
DROP TABLE public.crams_requestquestionresponse CASCADE;
DROP TABLE public.crams_requeststatus CASCADE;
DROP TABLE public.crams_storageproduct CASCADE;
DROP TABLE public.crams_storagerequest CASCADE;
DROP TABLE public.crams_storagerequestquestionresponse CASCADE;
DROP TABLE public.crams_storagetype CASCADE;
DROP TABLE public.crams_supportedinstitution CASCADE;
```

Drop the CHANGES tables

```sql
DROP TABLE public.changes_capability CASCADE;
DROP TABLE public.changes_dependency CASCADE;
DROP TABLE public.changes_state CASCADE;
DROP TABLE public.changes_task CASCADE;
```

Drop the COSTINGS tables

```sql
DROP TABLE public.costing_costitem CASCADE;
DROP TABLE public.costing_funding CASCADE;
DROP TABLE public.costing_hewrate CASCADE;
DROP TABLE public.costing_item CASCADE;
DROP TABLE public.costing_mediabought CASCADE;
DROP TABLE public.costing_mediacost CASCADE;
DROP TABLE public.costing_poolallocation CASCADE;
DROP TABLE public.costing_productconfiguration CASCADE;
DROP TABLE public.costing_rackcost CASCADE;
DROP TABLE public.costing_staffmember CASCADE;
```

Drop the API tables

```sql
DROP TABLE public.api_nectar CASCADE;
```

Drop the contacts tables we aren't going to use

```sql
DROP TABLE public.contacts_account CASCADE;
DROP TABLE public.contacts_address CASCADE;
DROP TABLE public.contacts_addresslist CASCADE;
DROP TABLE public.contacts_identity CASCADE;
DROP TABLE public.contacts_membership CASCADE;
```

This leaves 

* `public.contacts_organisation`
* `public.contacts_contact`

Drop the applications tables we aren't going to use 

```sql
DROP TABLE public.applications_accesslayer CASCADE;
DROP TABLE public.applications_action CASCADE;
DROP TABLE public.applications_applicationaction CASCADE;
DROP TABLE public.applications_categorisation CASCADE;
DROP TABLE public.applications_collectionprofile_data_formats CASCADE;
DROP TABLE public.applications_collectionuse CASCADE;
DROP TABLE public.applications_computeallocation CASCADE;
DROP TABLE public.applications_dataformat CASCADE;
DROP TABLE public.applications_fundinggrant CASCADE;
DROP TABLE public.applications_grant CASCADE;
DROP TABLE public.applications_interface CASCADE;
DROP TABLE public.applications_milestone CASCADE;
DROP TABLE public.applications_pattern CASCADE;
DROP TABLE public.applications_publication CASCADE;
DROP TABLE public.applications_reference CASCADE;
DROP TABLE public.applications_storageaccount CASCADE;
DROP TABLE public.applications_storageaccount_applications CASCADE;
DROP TABLE public.applications_storageaccount_collections CASCADE;
DROP TABLE public.applications_supportedinstitution CASCADE;
```

This leaves:

* `public.applications_allocation`
* `public.applications_collectionprofile`
* `public.applications_custodian`
* `public.applications_domain`
* `public.applications_fieldofresearch`
* `public.applications_ingest`
* `public.applications_project`
* `public.applications_request`
* `public.applications_storageproduct`
* `public.applications_suborganization`


Drop the INGEST tables...

```sql
DROP TABLE public.ingest_ingestcollectionerror CASCADE;
DROP TABLE public.ingest_ingestfiledata CASCADE;
DROP TABLE public.ingest_ingestfilerun CASCADE;
```

Leaves us with: 

* `public.ingest_ingestfile`

We leave the labels tables for the time being:

* `public.labels_alias`
* `public.labels_label`

Now down to 15 remaining tables.

The ingest table breaks the django rules about its indexes...
So run

```sql
DELETE FROM applications_ingest
WHERE id IN (
  SELECT MIN(id)
  FROM applications_ingest
  GROUP BY extraction_date, collection_id, storage_product_id
  HAVING count(*) > 1
);

-- until following returns the empty set...
SELECT MIN(id)
  FROM applications_ingest
  GROUP BY extraction_date, collection_id, storage_product_id
  HAVING count(*) > 1;
```

The labels table breaks the django rules about its indexes...
So run

```sql
DELETE FROM labels_label
WHERE id IN (
  SELECT MIN(id)
  FROM labels_label
  GROUP BY VALUE, group_id
  HAVING COUNT(*) > 1
);

-- until following returns the empty set...
SELECT MIN(id)
  FROM labels_label
  GROUP BY VALUE, group_id
  HAVING COUNT(*) > 1;
```

Then need to make sure that the file types and file sources on the ingest
table are consistent with the code...

```sql
UPDATE ingest_ingestfile
SET file_source = upper(file_source);

UPDATE ingest_ingestfile
SET file_type = upper(file_type);
```


How the migrations were created:

```bash
# Get a set of django models for the first ingest
python manage.py inspectdb > models.py
```
Then ensured each model has an id field:

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

Then updated the model to remove the fields we don't want and ran the migration
again

```bash
python manage.py makemigrations
python manage.py migrate
```

Then create the django superuser

```bash
python manage.py createsuperuser
```






