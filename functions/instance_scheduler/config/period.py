class Period:
    def __init__(
        self,
        name: str,
        begin_time: str = None,
        end_time: str = None,
        weekdays=[],
        description: str = None,
    ):
        self.name = name
        self.description = description
        self.begin_time = begin_time
        self.end_time = end_time
        self.weekdays = weekdays
