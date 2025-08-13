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
from models.lakebase import LakebaseResourcesDeleteResponse, LakebaseResourcesResponse

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)
w = WorkspaceClient()
router = APIRouter(tags=["lakebase"])
current_user_id = w.current_user.me().id


@router.post(
    "/resources/create-lakebase-resources",
    response_model=LakebaseResourcesResponse,
    summary="Create Lakebase Resources",
)
async def create_lakebase_resources(
    create_resources: bool = Query(
        description="""🚨 This endpoint creates resources in your Databricks environment that will incur a cost. 
        By setting this value to true you understand the costs associated with this action. 🚨
        ⌛️ This endpoint may take a few minutes to complete.⌛️""",
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
        instance_name = os.getenv(
            "LAKEBASE_INSTANCE_NAME", f"{current_user_id}-lakebase-demo"
        )

        # Check if instance already exists
        try:
            instance_exists = w.database.get_database_instance(name=instance_name)
            logger.info(f"Instance {instance_name} already exists. Skipping creation.")
            return LakebaseResourcesResponse(
                instance=instance_name,
                catalog="",
                synced_table="",
                message="Instance already exists, skipping creation.",
            )
        except Exception as e:
            if "not found" in str(e).lower() or "resource not found" in str(e).lower():
                logger.info(
                    f"Instance {instance_name} does not exist. Proceeding with creation."
                )
            else:
                logger.error(f"Error checking instance existence: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error checking instance existence: {str(e)}",
                )

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

        logger.info(f"Creating superuser role for: {superuser_role.name}")
        try:
            created_role = w.database.create_database_instance_role(
                instance_name=instance_create.name,
                database_instance_role=superuser_role,
            )
            logger.info(f"Successfully created superuser role: {created_role.name}")
        except Exception as e:
            logger.error(f"Failed to create superuser role (continuing anyway): {e}")
            logger.info(
                "Database instance is still functional - role can be created manually if needed"
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
            logical_database_name=lakebase_database_name,
            spec=spec,
        )

        logger.info(f"Creating synced table: {synced_table.name}")
        try:
            synced_table_create = w.database.create_synced_database_table(synced_table)
            logger.info(f"Initiated sync pipeline creation: {synced_table_create.id}")
            pipeline_id = synced_table_create.id
        except Exception as e:
            logger.error(
                f"API error during synced table creation (pipeline likely created anyway): {e}"
            )
            pipeline_id = "check-workspace-ui"

        workspace_url = w.config.host
        if pipeline_id != "check-workspace-ui":
            pipeline_url = f"{workspace_url}/pipelines/{pipeline_id}"
            message = f"Resources created successfully. Synced table pipeline {pipeline_id} is provisioning asynchronously. Monitor progress at: {pipeline_url}"
        else:
            message = f"Resources created successfully. Synced table pipeline initiated (API response error). Check pipelines in workspace: {workspace_url}/pipelines"

        return LakebaseResourcesResponse(
            instance=instance_create.name,
            catalog=database_create.name,
            synced_table=pipeline_id,
            message=message,
        )
    else:
        logger.info("create_resources is set to False. No resources were created.")
        return LakebaseResourcesResponse(
            instance="",
            catalog="",
            synced_table="",
            message="No resources were created (create_resources=False)",
        )


@router.delete(
    "/resources/delete-lakebase-resources",
    response_model=LakebaseResourcesDeleteResponse,
    summary="Delete Lakebase Resources",
)
async def delete_lakebase_resources(
    confirm_deletion: bool = Query(
        description="""🚨 This endpoint will permanently delete Lakebase resources. 
        Set to true to confirm you want to delete these resources. 🚨
        ⌛️ This endpoint may take a few minutes to complete.⌛️""",
    ),
):
    if not confirm_deletion:
        logger.info("confirm_deletion is set to False. No resources were deleted.")
        return LakebaseResourcesDeleteResponse(
            deleted_resources=[],
            failed_deletions=[],
            message="No resources were deleted (confirm_deletion=False)",
        )

    instance_name = os.getenv(
        "LAKEBASE_INSTANCE_NAME", f"{current_user_id}-lakebase-demo"
    )
    catalog_name = os.getenv("LAKEBASE_CATALOG_NAME", f"{current_user_id}-pg-catalog")
    synced_table_name = f"{catalog_name}.public.orders_synced"

    deleted_resources = []
    failed_deletions = []

    logger.info(f"Attempting to delete synced table: {synced_table_name}")
    try:
        w.database.delete_synced_database_table(name=synced_table_name)
        deleted_resources.append(f"Synced table: {synced_table_name}")
        logger.info(f"Successfully deleted synced table: {synced_table_name}")
    except Exception as e:
        failed_deletions.append(f"Synced table: {synced_table_name} - {str(e)}")
        logger.error(f"Failed to delete synced table {synced_table_name}: {e}")

    logger.info(f"Attempting to delete catalog: {catalog_name}")
    try:
        w.database.delete_database_catalog(name=catalog_name)
        deleted_resources.append(f"Catalog: {catalog_name}")
        logger.info(f"Successfully deleted catalog: {catalog_name}")
    except Exception as e:
        failed_deletions.append(f"Catalog: {catalog_name} - {str(e)}")
        logger.error(f"Failed to delete catalog {catalog_name}: {e}")

    logger.info(f"Attempting to delete database instance: {instance_name}")
    try:
        w.database.delete_database_instance(name=instance_name, purge=True)
        deleted_resources.append(f"Database instance: {instance_name}")
        logger.info(f"Successfully deleted database instance: {instance_name}")
    except Exception as e:
        failed_deletions.append(f"Database instance: {instance_name} - {str(e)}")
        logger.error(f"Failed to delete database instance {instance_name}: {e}")

    if failed_deletions:
        message = f"Deletion completed with errors. {len(deleted_resources)} resources deleted, {len(failed_deletions)} failed."
    else:
        message = f"All {len(deleted_resources)} resources deleted successfully."

    return LakebaseResourcesDeleteResponse(
        deleted_resources=deleted_resources,
        failed_deletions=failed_deletions,
        message=message,
    )
