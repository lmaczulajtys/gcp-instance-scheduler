from datetime import datetime
from google.cloud.compute_v1.services.instances import InstancesClient
from google.cloud.compute_v1.types import AggregatedListInstancesRequest, Instance
from schedulers.scheduler import Scheduler
from schedulers.state_service import StateService, State


class ComputeScheduler(Scheduler):
    def __init__(
        self,
        state_service: StateService,
        client: InstancesClient,
    ):
        super(ComputeScheduler, self).__init__(state_service=state_service)
        self.client = client

    def _get_instance_state(self, instance):
        if instance.status == Instance.Status.RUNNING:
            return State.RUNNING
        elif instance.status in [
            Instance.Status.STOPPED,
            Instance.Status.STOPPING,
            Instance.Status.TERMINATED,
        ]:
            return State.STOPPED
        else:
            return State.UNKNOWN

    def _get_last_start(self, instance) -> datetime:
        return datetime.fromisoformat(instance.last_start_timestamp)

    def _get_last_stop(self, instance) -> datetime:
        return datetime.fromisoformat(instance.last_stop_timestamp)

    def _get_schedulable_instances(self, project: str):
        request = AggregatedListInstancesRequest()
        request.project = project
        request.filter = "labels.{}!=''".format(
            self.state_service.get_config().schedule_tag_name
        )

        pager = self.client.aggregated_list(request=request)
        instances = []
        for page in pager:
            if page[1].instances:
                instances.append(page[1].instances)

        return [instance for sublist in instances for instance in sublist]

    def _start_instance(self, project: str, instance):
        zone = self._get_zone(instance)
        print("STARTING {}/{}/{}".format(project, zone, instance.name))
        self.client.start(project=project, zone=zone, instance=instance.name)

    def _stop_instance(self, project: str, instance):
        zone = self._get_zone(instance)
        print("STOPPING {}/{}/{}".format(project, zone, instance.name))
        self.client.stop(project=project, zone=zone, instance=instance.name)

    def _get_zone(self, instance):
        return instance.zone.rsplit("/", 1)[1]
