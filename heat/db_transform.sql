-- Set up our access layer mapping table
CREATE TABLE public.access_layer_member (
  id             SERIAL PRIMARY KEY NOT NULL,
  collection_id  INT                NOT NULL REFERENCES applications_project (id),
  accesslayer_id INT                NOT NULL REFERENCES applications_accesslayer (id),
  UNIQUE (collection_id, accesslayer_id)
);

CREATE UNIQUE INDEX access_layer_member_ix_collection_access_layer
  ON access_layer_member (collection_id, accesslayer_id);

-- will have to pass the owner in?
ALTER TABLE public.access_layer_member
  OWNER TO vicnode_prd;

INSERT INTO access_layer_member (collection_id, accesslayer_id)
  SELECT DISTINCT
    applications_collectionuse.collection_id,
    access_layer_id
  FROM public.applications_interface AS ai
    LEFT JOIN public.applications_collectionuse
      ON ai.collection_id = applications_collectionuse.id
    LEFT JOIN public.applications_accesslayer
      ON ai.access_layer_id = applications_accesslayer.id;

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

-- get rid of CRAMS
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

-- get rid of changes
DROP TABLE public.changes_capability CASCADE;
DROP TABLE public.changes_dependency CASCADE;
DROP TABLE public.changes_state CASCADE;
DROP TABLE public.changes_task CASCADE;

-- get rid of costings
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

-- and the api table
DROP TABLE public.api_nectar CASCADE;

--Drop the contacts tables we aren't going to use
DROP TABLE public.contacts_account CASCADE;
DROP TABLE public.contacts_address CASCADE;
DROP TABLE public.contacts_addresslist CASCADE;
DROP TABLE public.contacts_identity CASCADE;
DROP TABLE public.contacts_membership CASCADE;

-- drop the applications tables we aren't going to use
-- DROP TABLE public.applications_accesslayer CASCADE;
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

-- drop the ingest tables we aren't going to use
DROP TABLE public.ingest_ingestcollectionerror CASCADE;
DROP TABLE public.ingest_ingestfiledata CASCADE;
DROP TABLE public.ingest_ingestfilerun CASCADE;

-- now clean the data

-- The ingest table breaks the django rules about its indexes...

CREATE OR REPLACE FUNCTION clean_ingests()
  RETURNS VOID AS '

DECLARE id_found INTEGER;
BEGIN
  -- has more than one set of identical id
  LOOP
    SELECT MIN(id)
    INTO id_found
    FROM applications_ingest
    GROUP BY extraction_date, collection_id, storage_product_id
    HAVING count(*) > 1;
    IF id_found IS NULL
    THEN
      EXIT;
    END IF;
    DELETE FROM applications_ingest
    WHERE id IN (
      SELECT MIN(id)
      FROM applications_ingest
      GROUP BY extraction_date, collection_id, storage_product_id
      HAVING count(*) > 1
    );
  END LOOP;
END;'
LANGUAGE plpgsql;

SELECT clean_ingests();

-- The labels table breaks the django rules about its indexes...

CREATE OR REPLACE FUNCTION clean_labels()
  RETURNS VOID AS '

DECLARE id_found INTEGER;
BEGIN
  LOOP
    SELECT MIN(id)
    INTO id_found
    FROM labels_label
    GROUP BY VALUE, group_id
    HAVING count(*) > 1;
    IF id_found IS NULL
    THEN
      EXIT;
    END IF;
    DELETE FROM labels_label
    WHERE id IN (
      SELECT MIN(id)
      FROM labels_label
      GROUP BY VALUE, group_id
      HAVING count(*) > 1
    );
  END LOOP;
END;'
LANGUAGE plpgsql;

-- the production data has an issue with this id in the labels alias table
-- this is a hacky and brute force approach to solving the issue...
DELETE FROM labels_alias
WHERE label_id = 673;

SELECT clean_labels();

-- file type and file source aren't upper case for a lot of records in the
-- ingest table

UPDATE ingest_ingestfile
SET file_source = upper(file_source);

UPDATE ingest_ingestfile
SET file_type = upper(file_type);

-- we have a set of junk storage products, so remove them

DELETE FROM applications_storageproduct
WHERE product_name_id IN (77, 78, 79, 80, 100, 101, 411);

DELETE FROM labels_label
WHERE id IN (77, 78, 79, 80, 100, 101, 411);

-- move the Ballarat requests to Federation University

UPDATE applications_request
SET institution_id = 8
WHERE institution_id = 17;

UPDATE applications_request
SET operational_funding_source_id = 8
WHERE operational_funding_source_id = 17;

-- move the Ballarat contacts to Federation University
UPDATE contacts_contact
SET organisation_id = 8
WHERE organisation_id = 17;

-- Delete Ballarat from the list of institutions
DELETE FROM contacts_organisation
WHERE short_name = 'Ballarat';

-- clean up non UoM projects...
-- As promised, any collection with the following nomenclature in its ID can be removed
--
-- RDS – RITP-XXX (I believe there are 35) – this is all of the LARDS archive migrated collective
-- MURDA-XXX  (there are around 233) – this is all of the MURDA collective
-- 2016MONXXXX (I think there are only 3)
-- Anything under Monash Internal Tenancy (RDSM)

-- Anything else can stay for the time being in case we have incorrectly labelled things

DELETE FROM applications_ingest
WHERE collection_id IN (
  SELECT DISTINCT collection_id
  FROM applications_request
    LEFT JOIN applications_allocation
      ON applications_request.id = applications_allocation.application_id
  WHERE code LIKE 'RDS-RITP%' OR code LIKE '2016MON%' OR code LIKE 'MURDA-%' OR
        code LIKE 'RDSM%'
) AND collection_id != 81;

DELETE FROM applications_custodian
WHERE collection_id IN (
  SELECT DISTINCT collection_id
  FROM applications_request
    LEFT JOIN applications_allocation
      ON applications_request.id = applications_allocation.application_id
  WHERE code LIKE 'RDS-RITP%' OR code LIKE '2016MON%' OR code LIKE 'MURDA-%' OR
        code LIKE 'RDSM%'
) AND collection_id != 81;

DELETE FROM applications_collectionprofile
WHERE collection_id IN (
  SELECT DISTINCT collection_id
  FROM applications_request
    LEFT JOIN applications_allocation
      ON applications_request.id = applications_allocation.application_id
  WHERE code LIKE 'RDS-RITP%' OR code LIKE '2016MON%' OR code LIKE 'MURDA-%' OR
        code LIKE 'RDSM%'
) AND collection_id != 81;


DELETE FROM applications_domain
WHERE collection_id IN (
  SELECT DISTINCT collection_id
  FROM applications_request
    LEFT JOIN applications_allocation
      ON applications_request.id = applications_allocation.application_id
  WHERE code LIKE 'RDS-RITP%' OR code LIKE '2016MON%' OR code LIKE 'MURDA-%' OR
        code LIKE 'RDSM%'
) AND collection_id != 81;

DELETE FROM access_layer_member
WHERE collection_id IN (
  SELECT DISTINCT collection_id
  FROM applications_request
    LEFT JOIN applications_allocation
      ON applications_request.id = applications_allocation.application_id
  WHERE code LIKE 'RDS-RITP%' OR code LIKE '2016MON%' OR code LIKE 'MURDA-%' OR
        code LIKE 'RDSM%'
) AND collection_id != 81;

ALTER TABLE public.applications_allocation
  DROP CONSTRAINT applications_allocat_collection_id_35d4d1f8_fk_applicati,
  ADD CONSTRAINT applications_allocat_collection_id_35d4d1f8_fk_applicati
FOREIGN KEY (collection_id)
REFERENCES applications_project
ON DELETE CASCADE;

DELETE FROM applications_project
WHERE id IN (
  SELECT DISTINCT collection_id
  FROM applications_request
    LEFT JOIN applications_allocation
      ON applications_request.id = applications_allocation.application_id
  WHERE code LIKE 'RDS-RITP%' OR code LIKE '2016MON%' OR code LIKE 'MURDA-%' OR
        code LIKE 'RDSM%'
) AND id != 81;

DELETE FROM applications_request
WHERE (code LIKE 'RDS-RITP%' OR code LIKE '2016MON%' OR code LIKE 'MURDA-%' OR
       code LIKE 'RDSM%') AND id != 922;

-- Reveal our problem child...
-- SELECT *
-- FROM applications_request
-- WHERE id = 922;


-- can now delete labels no longer used...


