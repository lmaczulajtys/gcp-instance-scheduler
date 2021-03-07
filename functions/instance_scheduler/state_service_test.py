from datetime import datetime
from config.period import Period
from config.schedule import Schedule
from config.scheduler_config import SchedulerConfig
from schedulers.state_service import StateService, State

config = SchedulerConfig(
    periods={
        "period1": Period(
            name="period1",
            begin_time="9:00",
            end_time="13:00",
            weekdays=[0, 1, 2, 3, 4],
        ),
        "period2": Period(
            name="period2",
            begin_time="15:00",
            end_time="16:00",
            weekdays=[0, 1, 2, 3, 4],
        ),
        "period3": Period(
            name="period3", end_time="21:00", weekdays=[0, 1, 2, 3, 4, 5, 6]
        ),
    },
    schedules={
        "schedule1": Schedule(
            name="schedule1", periods_names=["period1", "period2", "period3"]
        )
    },
    schedule_tag_name="schedule",
    timezone="Europe/Warsaw",
)

service = StateService(config=config)


def test_automatic_schedules_businessday():
    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 08:00"),
            last_start=datetime.fromisoformat("2021-03-02 09:00"),
            last_stop=datetime.fromisoformat("2021-03-01 21:00"),
        )
        == State.STOPPED
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 09:00"),
            last_start=datetime.fromisoformat("2021-03-02 09:00"),
            last_stop=datetime.fromisoformat("2021-03-01 21:00"),
        )
        == State.RUNNING
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 10:00"),
            last_start=datetime.fromisoformat("2021-03-02 09:00"),
            last_stop=datetime.fromisoformat("2021-03-01 21:00"),
        )
        == State.RUNNING
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 13:00"),
            last_start=datetime.fromisoformat("2021-03-02 09:00"),
            last_stop=datetime.fromisoformat("2021-03-01 21:00"),
        )
        == State.STOPPED
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 13:30"),
            last_start=datetime.fromisoformat("2021-03-02 09:00"),
            last_stop=datetime.fromisoformat("2021-03-02 18:00"),
        )
        == State.STOPPED
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 15:00"),
            last_start=datetime.fromisoformat("2021-03-02 09:00"),
            last_stop=datetime.fromisoformat("2021-03-02 13:00"),
        )
        == State.RUNNING
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 15:30"),
            last_start=datetime.fromisoformat("2021-03-02 15:00"),
            last_stop=datetime.fromisoformat("2021-03-02 13:00"),
        )
        == State.RUNNING
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 16:00"),
            last_start=datetime.fromisoformat("2021-03-02 15:00"),
            last_stop=datetime.fromisoformat("2021-03-02 13:00"),
        )
        == State.STOPPED
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 16:30"),
            last_start=datetime.fromisoformat("2021-03-02 15:00"),
            last_stop=datetime.fromisoformat("2021-03-02 16:00"),
        )
        == State.STOPPED
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 21:00"),
            last_start=datetime.fromisoformat("2021-03-02 09:00"),
            last_stop=datetime.fromisoformat("2021-03-02 18:00"),
        )
        == State.STOPPED
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 22:00"),
            last_start=datetime.fromisoformat("2021-03-02 09:00"),
            last_stop=datetime.fromisoformat("2021-03-02 21:00"),
        )
        == State.STOPPED
    )


def test_automatic_schedules_manual_start():
    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 08:00"),
            last_start=datetime.fromisoformat("2021-03-02 07:00"),
            last_stop=datetime.fromisoformat("2021-03-01 21:00"),
        )
        == State.UNKNOWN
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 09:00"),
            last_start=datetime.fromisoformat("2021-03-02 07:00"),
            last_stop=datetime.fromisoformat("2021-03-01 21:00"),
        )
        == State.UNKNOWN
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 09:00"),
            last_start=datetime.fromisoformat("2021-03-02 07:00"),
            last_stop=datetime.fromisoformat("2021-03-02 08:00"),
        )
        == State.RUNNING
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 19:00"),
            last_start=datetime.fromisoformat("2021-03-02 20:00"),
            last_stop=datetime.fromisoformat("2021-03-02 18:00"),
        )
        == State.UNKNOWN
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 23:00"),
            last_start=datetime.fromisoformat("2021-03-02 22:00"),
            last_stop=datetime.fromisoformat("2021-03-02 21:00"),
        )
        == State.UNKNOWN
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-07 22:00"),
            last_start=datetime.fromisoformat("2021-03-07 17:00"),
            last_stop=datetime.fromisoformat("2021-03-07 23:10"),
        )
        == State.STOPPED
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-07 22:00"),
            last_start=datetime.fromisoformat("2021-03-07 17:00"),
            last_stop=datetime.fromisoformat("2021-03-07 01:10"),
        )
        == State.STOPPED
    )


def test_automatic_schedules_manual_stop():
    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-02 11:00"),
            last_start=datetime.fromisoformat("2021-03-02 09:00"),
            last_stop=datetime.fromisoformat("2021-03-02 10:00"),
        )
        == State.UNKNOWN
    )


def test_automatic_schedules_weekend():
    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-06 08:00"),
            last_start=datetime.fromisoformat("2021-03-06 09:00"),
            last_stop=datetime.fromisoformat("2021-03-05 21:00"),
        )
        == State.UNKNOWN
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-06 09:00"),
            last_start=datetime.fromisoformat("2021-03-06 09:00"),
            last_stop=datetime.fromisoformat("2021-03-05 21:00"),
        )
        == State.UNKNOWN
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-06 10:00"),
            last_start=datetime.fromisoformat("2021-03-06 09:00"),
            last_stop=datetime.fromisoformat("2021-03-05 21:00"),
        )
        == State.UNKNOWN
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-06 13:00"),
            last_start=datetime.fromisoformat("2021-03-06 09:00"),
            last_stop=datetime.fromisoformat("2021-03-05 21:00"),
        )
        == State.UNKNOWN
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-06 13:30"),
            last_start=datetime.fromisoformat("2021-03-06 09:00"),
            last_stop=datetime.fromisoformat("2021-03-05 21:00"),
        )
        == State.UNKNOWN
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-06 21:00"),
            last_start=datetime.fromisoformat("2021-03-06 09:00"),
            last_stop=datetime.fromisoformat("2021-03-05 21:00"),
        )
        == State.STOPPED
    )

    assert (
        service.get_desired_state(
            schedule_name="schedule1",
            current_datetime=datetime.fromisoformat("2021-03-06 22:00"),
            last_start=datetime.fromisoformat("2021-03-06 09:00"),
            last_stop=datetime.fromisoformat("2021-03-06 21:00"),
        )
        == State.STOPPED
    )
