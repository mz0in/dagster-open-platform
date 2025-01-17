import os

from dagster import EnvVar, file_relative_path
from dagster_dbt import DbtCliResource
from dagster_gcp import BigQueryResource
from dagster_slack import SlackResource
from dagster_snowflake import SnowflakeResource

from ..utils.environment_helpers import get_dbt_target
from .stitch_resource import StitchResource

DBT_MANIFEST_PATH = file_relative_path(__file__, "../../dbt/target/manifest.json")

bigquery_resource = BigQueryResource(
    gcp_credentials=EnvVar("GCP_CREDENTIALS"),
)

snowflake_resource = SnowflakeResource(
    user=EnvVar("SNOWFLAKE_USER"),
    account=EnvVar("SNOWFLAKE_ACCOUNT"),
    password=EnvVar("SNOWFLAKE_PASSWORD"),
    role=os.getenv("SNOWFLAKE_ROLE", "PURINA"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "PURINA"),
)

dbt_resource = DbtCliResource(
    project_dir=file_relative_path(__file__, "../../dbt"),
    profiles_dir=file_relative_path(__file__, "../../dbt"),
    target=get_dbt_target(),
)

stitch_resource = StitchResource(
    stitch_client_id=EnvVar("STITCH_CLIENT_ID"),
    access_token=EnvVar("STITCH_ACCESS_TOKEN"),
)

slack_resource = SlackResource(token=EnvVar("SLACK_ANALYTICS_TOKEN"))
