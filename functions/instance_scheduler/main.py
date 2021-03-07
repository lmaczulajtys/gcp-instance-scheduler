import os
import pytz
from datetime import datetime
from google.cloud.compute_v1.services.instances import InstancesClient
from google.cloud import datastore
from config.period import Period
from config.schedule import Schedule
from config.scheduler_config import SchedulerConfig
from schedulers.compute_scheduler import ComputeScheduler
from schedulers.state_service import StateService

DEFAULT_PROJECT = os.getenv("GCP_PROJECT")
DEFAULT_TIMEZONE = "GMT"

DS_NAMESPACE = "gcp-instance-scheduler"
DS_ENTITY_PERIOD = "Period"
DS_ENTITY_SCHEDULE = "Schedule"

ENV_PROJECTS_LIST = "PROJECTS_LIST"
ENV_TIMEZONE = "TIMEZONE"

SCHEDULE_TAG_NAME = "schedule"


def get_config():
    client = datastore.Client(namespace=DS_NAMESPACE)

    periods_query = client.query(kind=DS_ENTITY_PERIOD)
    periods_iter = periods_query.fetch()
    periods = {}
    for period in periods_iter:
        periods[period.key.name] = Period(
            name=period.key.name,
            begin_time=period["beginTime"],
            end_time=period["endTime"],
            weekdays=period["weekdays"],
            description=period["description"],
        )

    schedules_query = client.query(kind=DS_ENTITY_SCHEDULE)
    schedules_iter = schedules_query.fetch()
    schedules = {}
    for schedule in schedules_iter:
        schedules[schedule.key.name] = Schedule(
            name=schedule.key.name,
            periods_names=schedule["periods"],
            description=schedule["description"],
        )

    return SchedulerConfig(
        periods=periods,
        schedules=schedules,
        schedule_tag_name=SCHEDULE_TAG_NAME,
        timezone=os.getenv(ENV_TIMEZONE, DEFAULT_TIMEZONE),
    )


def main(event, context):
    config = get_config()
    timezone = pytz.timezone(config.timezone)
    current_datetime = datetime.now(timezone)

    schedulers = [
        ComputeScheduler(
            state_service=StateService(config=config), client=InstancesClient()
        )
    ]

    env_projects = os.getenv(ENV_PROJECTS_LIST, DEFAULT_PROJECT)
    projects = env_projects.split(",")
    for project in projects:
        for scheduler in schedulers:
            scheduler.run(project=project, current_datetime=current_datetime)


def webhook(cloudevent):
    main(cloudevent, None)
