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

-- drop the ingest tables we aren't going to use
DROP TABLE public.ingest_ingestcollectionerror CASCADE;
DROP TABLE public.ingest_ingestfiledata CASCADE;
DROP TABLE public.ingest_ingestfilerun CASCADE;

-- now clean the data

-- following should be function, rather than a repeated call
DELETE FROM applications_ingest
WHERE id IN (
  SELECT MIN(id)
  FROM applications_ingest
  GROUP BY extraction_date, collection_id, storage_product_id
  HAVING count(*) > 1
);

DELETE FROM applications_ingest
WHERE id IN (
  SELECT MIN(id)
  FROM applications_ingest
  GROUP BY extraction_date, collection_id, storage_product_id
  HAVING count(*) > 1
);

DELETE FROM applications_ingest
WHERE id IN (
  SELECT MIN(id)
  FROM applications_ingest
  GROUP BY extraction_date, collection_id, storage_product_id
  HAVING count(*) > 1
);

-- following should be function, rather than a repeated call
DELETE FROM labels_label
WHERE id IN (
  SELECT MIN(id)
  FROM labels_label
  GROUP BY VALUE, group_id
  HAVING COUNT(*) > 1
);

DELETE FROM labels_label
WHERE id IN (
  SELECT MIN(id)
  FROM labels_label
  GROUP BY VALUE, group_id
  HAVING COUNT(*) > 1
);

UPDATE ingest_ingestfile
SET file_source = upper(file_source);

UPDATE ingest_ingestfile
SET file_type = upper(file_type);

DELETE FROM applications_storageproduct
WHERE product_name_id IN (77, 78, 79, 80, 100, 101, 411);

DELETE FROM labels_label
WHERE id IN (77, 78, 79, 80, 100, 101, 411);