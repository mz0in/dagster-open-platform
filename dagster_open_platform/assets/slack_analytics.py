import os

import pandas as pd
from dagster import (
    AssetCheckResult,
    AssetCheckSpec,
    MaterializeResult,
    ScheduleDefinition,
    asset,
    define_asset_job,
)
from dagster_open_platform.utils.environment_helpers import get_environment
from dagster_slack import SlackResource
from dagster_snowflake import SnowflakeResource
from snowflake.connector.pandas_tools import write_pandas


@asset(
    group_name="devrel",
    check_specs=[AssetCheckSpec("slack_successful_write", asset="slack_members")],
    description="Slack Stats, which includes number of members by day",
)
def slack_members(slack: SlackResource, snowflake: SnowflakeResource):
    client = slack.get_client()
    # The Dagster Slack resource doesn't support setting headers
    client.headers = {"cookie": os.getenv("SLACK_ANALYTICS_COOKIE")}
    data = {
        "date_range": "all",
        "set_active": "true",
    }
    response = client.api_call("team.stats.timeSeries", data=data).data
    assert isinstance(response, dict)
    response = response.get("stats", [])
    slack_stats = pd.DataFrame(response)
    slack_stats["ds"] = pd.to_datetime(slack_stats["ds"])

    database = None
    schema = None
    if get_environment() == "PROD":
        database = "TELEMETRY"
        schema = "SLACK_MEMBERS"

    with snowflake.get_connection() as conn:
        # write_pandas returns a tuple of (success, num_chunks, num_rows, output)
        res = write_pandas(
            conn=conn,
            df=slack_stats,
            table_name="SLACK_MEMBERS",
            database=database,
            schema=schema,
            overwrite=True,
            auto_create_table=True,
            quote_identifiers=False,
        )
        yield MaterializeResult(
            metadata={"num_rows": res[2]}, check_results=[AssetCheckResult(passed=res[0])]
        )


slack_asset_job = define_asset_job(
    "slack_members_refresh", selection=[slack_members], tags={"team": "devrel"}
)
slack_daily_schedule = ScheduleDefinition(
    job=slack_asset_job,
    cron_schedule="0 1 * * *",
)
