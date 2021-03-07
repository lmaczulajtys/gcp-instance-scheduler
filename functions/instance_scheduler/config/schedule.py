class Schedule:
    def __init__(self, name: str, periods_names: list, description: str = None):
        self.name = name
        self.description = description
        self.periods_names = periods_names
