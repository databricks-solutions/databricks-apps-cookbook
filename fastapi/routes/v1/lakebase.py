import logging
import os

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

from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)
w = WorkspaceClient()
router = APIRouter(tags=["lakebase"])
# lakebase_instance_name = "agrants-sdk-create"
# lakebase_database_name = "grants-database"
# catalog_name = "grants-testing-catalog"
# synced_table_storage_catalog = "mfg_mid_central_sa"
# synced_table_storage_schema = "gdoyle"

current_user_id = w.current_user.me().id


@router.post(
    "/resources/create-lakebase-resources",
    summary="Create Lakebase Resources",
)
async def create_lakebase_resources(
    create_resources: bool = Query(
        description="""🚨 This endpoint creates resources in your Databricks environment that will incur a cost. 
        By setting this value to true you understand the costs associated with this action. 🚨""",
    ),
    capacity: str = Query("CU_1", description="Capacity of the Lakebase instance"),
    node_count: int = Query(1, description="Number of nodes in the Lakebase instance"),
    enable_readable_secondaries: bool = Query(
        False, description="Enable readable secondaries"
    ),
    retention_window_in_days: int = Query(
        7, description="Retention window in days for the Lakebase instance"
    ),
):
    if create_resources:
        instance_name = os.getenv("INSTANCE_NAME", f"{current_user_id}-lakebase-demo")
        lakebase_database_name = os.getenv("LAKEBASE_DATABASE_NAME", "demo_database")
        catalog_name = os.getenv(
            "LAKEBASE_CATALOG_NAME", f"{current_user_id}-pg-catalog"
        )
        synced_table_storage_catalog = os.getenv(
            "SYNCHED_TABLE_STORAGE_CATALOG", "default_storage_catalog"
        )
        synced_table_storage_schema = os.getenv(
            "SYNCHED_TABLE_STORAGE_SCHEMA", "default_storage_schema"
        )

        instance = DatabaseInstance(
            name=instance_name,
            capacity=capacity,
            node_count=node_count,
            enable_readable_secondaries=enable_readable_secondaries,
            retention_window_in_days=retention_window_in_days,
        )
        logger.info(f"Creating database instance: {instance_name}")
        instance_create = w.database.create_database_instance_and_wait(instance)
        logger.info(f"Database instance created: {instance_create}")

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
        logger.info(f"Creating catalog: {catalog_name}")
        database_create = w.database.create_database_catalog(catalog)
        logger.info(f"Created catalog {database_create.name}")

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
            logical_database_name=database_create.name,
            spec=spec,
        )

        logger.info(f"Creating synced table: {synced_table.name}")
        synced_table_create = w.database.create_synced_database_table(synced_table)
        logger.info(f"Created sync pipeline: {synced_table_create.id}")
    else:
        logger.info("create_resources is set to False. No resources were created.")
