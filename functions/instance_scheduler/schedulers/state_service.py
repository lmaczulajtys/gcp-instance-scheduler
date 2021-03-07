from datetime import datetime
from enum import Enum
import pytz
from config.scheduler_config import SchedulerConfig


class State(Enum):
    UNKNOWN = 0
    RUNNING = 1
    STOPPED = 2


class StateService:
    def __init__(self, config: SchedulerConfig):
        self.config = config
        self.timezone = pytz.timezone(config.timezone)

    def get_config(self):
        return self.config

    def get_desired_state(
        self,
        schedule_name: str,
        current_datetime: datetime,
        last_stop: datetime,
        last_start: datetime,
    ) -> State:
        if schedule_name not in self.config.schedules:
            return State.UNKNOWN

        schedule = self.config.schedules[schedule_name]
        state = State.UNKNOWN
        current_time = current_datetime.time()
        for period_name in schedule.periods_names:
            period = self.config.periods[period_name]
            begin_time = (
                datetime.strptime(period.begin_time, "%H:%M").time()
                if period.begin_time
                else None
            )
            end_time = (
                datetime.strptime(period.end_time, "%H:%M").time()
                if period.end_time
                else None
            )
            last_start_time = last_start.astimezone(self.timezone).time()
            last_stop_time = last_stop.astimezone(self.timezone).time()

            if current_datetime.weekday() in period.weekdays:
                # Instance state changed manually
                # or according to another period in schedule
                if last_start_time > last_stop_time and last_start_time > end_time:
                    state = State.UNKNOWN if state == State.UNKNOWN else state
                # Period only with stopping action
                elif begin_time is None and current_time >= end_time:
                    state = State.STOPPED
                elif begin_time is None:
                    state = State.UNKNOWN if state == State.UNKNOWN else state
                # Period only with starting action
                elif end_time is None and current_time >= begin_time:
                    state = State.RUNNING
                # Instance state changed manually
                elif (
                    last_start_time < last_stop_time
                    and last_start_time < begin_time
                    and last_stop_time > begin_time
                ):
                    state = State.UNKNOWN if state == State.UNKNOWN else state
                # In working hours
                elif begin_time <= current_time and current_time < end_time:
                    if begin_time < last_stop_time and last_stop_time < end_time:
                        return State.UNKNOWN
                    else:
                        return State.RUNNING
                # Outside of working hours
                else:
                    state = State.STOPPED

        return state
