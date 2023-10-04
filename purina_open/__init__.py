import warnings

from dagster import Definitions, ExperimentalWarning, load_assets_from_modules

warnings.filterwarnings("ignore", category=ExperimentalWarning)

from .assets import cloud_staging, health_check, oss_analytics
from .resources import bigquery_resource, dbt_resource, snowflake_resource
from .resources.stitch_resource import stitch_resource

health_check_assets = load_assets_from_modules(
    [health_check],
    group_name="health_check",
)

oss_analytics_assets = load_assets_from_modules([oss_analytics], group_name="oss_analytics")
cloud_staging = load_assets_from_modules([cloud_staging], group_name="cloud_staging")

all_assets = [*health_check_assets, *oss_analytics_assets, *cloud_staging]

defs = Definitions(
    assets=all_assets,
    resources={
        "stitch": stitch_resource,
        "bigquery": bigquery_resource,
        "snowflake": snowflake_resource,
        "dbt": dbt_resource,
    },
)
