# %pip install --upgrade databricks-sdk

# dbutils.library.restartPython()

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.database import (
    DatabaseCatalog,
    DatabaseInstance,
    DatabaseInstanceRole,
    DatabaseInstanceRoleAttributes,
    DatabaseInstanceRoleIdentityType,
    DatabaseInstanceRoleMembershipRole,
    NewPipelineSpec,
    SyncedDatabaseTable,
    SyncedTableSchedulingPolicy,
    SyncedTableSpec,
)

w = WorkspaceClient()

lakebase_instance_name = (
    "agrants-sdk-create"  # What your lakebase instance will be named
)
lakebase_database_name = "grants-database"  # Lakebase database name
catalog_name = "grants-testing-catalog"  # Initial Lakebase catalog name
synced_table_storage_catalog = "mfg_mid_central_sa"  # Catalog storage name for synced table, chose a catalog you have permissions to.
synced_table_storage_schema = (
    "gdoyle"  # Schema for synced table, chose a schema you have permissions to.
)

instance = DatabaseInstance(
    name=lakebase_instance_name,
    capacity="CU_1",
    node_count=1,
    enable_readable_secondaries=False,
    retention_window_in_days=7,
)

instance_create = w.database.create_database_instance_and_wait(instance)
print(f"Database instance created: {instance_create}")

superuser_role = DatabaseInstanceRole(
    name=w.current_user.me().user_name,
    identity_type=DatabaseInstanceRoleIdentityType.USER,
    membership_role=DatabaseInstanceRoleMembershipRole.DATABRICKS_SUPERUSER,
    attributes=DatabaseInstanceRoleAttributes(
        bypassrls=True, createdb=True, createrole=True
    ),
)

catalog = DatabaseCatalog(
    name=catalog_name,
    database_instance_name=instance_create.name,
    database_name=lakebase_database_name,
    create_database_if_not_exists=True,
)
database_create = w.database.create_database_catalog(catalog)
print(f"Created catalog {database_create.name}")

new_pipeline = NewPipelineSpec(
    storage_catalog=synced_table_storage_catalog,
    storage_schema=synced_table_storage_schema,
)

spec = SyncedTableSpec(
    source_table_full_name="samples.tpch.orders",
    primary_key_columns=["o_orderkey"],
    timeseries_key="o_orderdate",
    create_database_objects_if_missing=True,
    new_pipeline_spec=new_pipeline,
    scheduling_policy=SyncedTableSchedulingPolicy.SNAPSHOT,  # Add this
)

synced_table = SyncedDatabaseTable(
    name=f"{catalog_name}.public.orders_synced",
    database_instance_name=instance_create.name,
    logical_database_name=lakebase_database_name,
    spec=spec,
)

synced_table_create = w.database.create_synced_database_table(synced_table)
print(f"Create Sync Pipeline: {synced_table_create}")
