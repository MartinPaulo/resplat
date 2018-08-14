# resplat

A simple reporting project

https://www.digitalocean.com/community/tutorials/how-to-create-a-mcs-signed-ssl-certificate-for-apache-in-ubuntu-16-04

Todo:

* Rename collection profile to "description"
* Get rid of estimated collection size
* Don't hide collection profile


access layer <- interface -> collection use -> collection (project)

so build:

collection <- new table -> access layer

For the new table:

columns: id, collection_id, acces_layer_id

```sql

CREATE TABLE access_layer_member (
  id             SERIAL PRIMARY KEY NOT NULL,
  collection_id  INT                NOT NULL REFERENCES applications_project (id),
  accesslayer_id INT                NOT NULL REFERENCES applications_accesslayer (id),
  UNIQUE (collection_id, accesslayer_id)
);

CREATE UNIQUE INDEX access_layer_member_ix_collection_access_layer
  ON access_layer_member (collection_id, accesslayer_id);

```


```sql
INSERT INTO access_layer_member (collection_id, access_layer_id)
SELECT DISTINCT
  applications_collectionuse.collection_id,
  access_layer_id
FROM applications_interface AS ai
  LEFT JOIN applications_collectionuse
    ON ai.collection_id = applications_collectionuse.id
  LEFT JOIN applications_accesslayer
    ON ai.access_layer_id = applications_accesslayer.id
ORDER BY
  collection_id,
  access_layer_id;
```