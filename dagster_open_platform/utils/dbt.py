import os
from typing import Any, Mapping

from dagster import AssetKey, MetadataValue
from dagster_dbt import DagsterDbtTranslator

SNOWFLAKE_ACCOUNT_BASE = os.getenv("SNOWFLAKE_ACCOUNT", ".").split(".")[0]
PURINA_DATABASE_NAME = (
    f"PURINA_CLONE_{os.environ['DAGSTER_CLOUD_PULL_REQUEST_ID']}"
    if os.getenv("DAGSTER_CLOUD_IS_BRANCH_DEPLOYMENT") == "1"
    else "PURINA"
)
SNOWFLAKE_URL = f"https://app.snowflake.com/ax61354/{SNOWFLAKE_ACCOUNT_BASE}/#/data/databases/{PURINA_DATABASE_NAME}/schemas"


class PurinaDagsterDbtTranslator(DagsterDbtTranslator):
    @classmethod
    def get_asset_key(cls, dbt_resource_props: Mapping[str, Any]) -> AssetKey:
        resource_type = dbt_resource_props["resource_type"]
        resource_name = dbt_resource_props["name"]

        if resource_type in ("model", "seed"):
            schema = (
                dbt_resource_props["schema"] if dbt_resource_props["schema"] else "unknown_schema"
            )
            return AssetKey([dbt_resource_props["database"], schema, resource_name])

        elif resource_type == "source":
            sources = {
                "postgres_etl_high_freq": [
                    "stitch",
                    "dagster_cloud",
                    resource_name,
                ],
                "postgres_etl_low_freq": [
                    "stitch",
                    "dagster_cloud",
                    resource_name,
                ],
            }

            source_name = dbt_resource_props["source_name"]
            return AssetKey(sources[source_name])

        else:
            raise ValueError(f"Unknown dbt resource_type: {resource_type}")

    @classmethod
    def get_metadata(cls, dbt_node_info: Mapping[str, Any]) -> Mapping[str, Any]:
        if dbt_node_info["resource_type"] != "model":
            return {}

        return {
            "url": MetadataValue.url(
                f"{SNOWFLAKE_URL}/{dbt_node_info['schema'].upper()}/table/{dbt_node_info['name'].upper()}"
            )
        }
