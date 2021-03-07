from abc import ABC, abstractmethod
from datetime import datetime
from schedulers.state_service import StateService, State


class Scheduler(ABC):
    def __init__(self, state_service: StateService):
        self.state_service = state_service

    def run(self, project: str, current_datetime: datetime):
        instances = self._get_schedulable_instances(project=project)

        for instance in instances:
            instance_state = self._get_instance_state(instance)
            schedule = instance.labels[
                self.state_service.get_config().schedule_tag_name
            ]
            desired_state = self.state_service.get_desired_state(
                schedule_name=schedule,
                current_datetime=current_datetime,
                last_start=self._get_last_start(instance),
                last_stop=self._get_last_stop(instance),
            )

            if (
                instance_state != State.UNKNOWN
                and desired_state != State.UNKNOWN
                and instance_state != desired_state
            ):
                if desired_state == State.RUNNING:
                    self._start_instance(project=project, instance=instance)
                elif desired_state == State.STOPPED:
                    self._stop_instance(project=project, instance=instance)

    @abstractmethod
    def _get_instance_state(self, instance) -> State:
        pass

    @abstractmethod
    def _get_last_start(self, instance) -> datetime:
        pass

    @abstractmethod
    def _get_last_stop(self, instance) -> datetime:
        pass

    @abstractmethod
    def _get_schedulable_instances(self, project: str) -> list:
        pass

    @abstractmethod
    def _start_instance(self, project: str, instance):
        pass

    @abstractmethod
    def _stop_instance(self, project: str, instance):
        pass
