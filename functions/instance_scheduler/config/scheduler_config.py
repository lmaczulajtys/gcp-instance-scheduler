class SchedulerConfig:
    def __init__(
        self,
        periods: dict,
        schedules: dict,
        schedule_tag_name: str,
        timezone: str,
    ):
        self.periods = periods
        self.schedules = schedules
        self.schedule_tag_name = schedule_tag_name
        self.timezone = timezone
