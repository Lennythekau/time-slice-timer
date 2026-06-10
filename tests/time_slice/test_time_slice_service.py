import datetime

from tests.conftest import MockTimer
from time_slice.model import RunningTimeSlice
from time_slice.repo import TimeSliceRepo
from time_slice.service import TimeSliceService
from user_session import UserSession


def test_start_slice_is_idempotent(
    time_slice_service: TimeSliceService, running_slice: RunningTimeSlice
):
    time_slice_started_fired_counter = 0

    def on_time_slice_started(_):
        nonlocal time_slice_started_fired_counter
        time_slice_started_fired_counter += 1

    time_slice_service.slice_started += on_time_slice_started
    time_slice_service.start_slice(running_slice)
    time_slice_service.start_slice(running_slice)
    time_slice_service.slice_started -= on_time_slice_started

    assert time_slice_started_fired_counter == 1


def test_start_slice_starts_stopwatch_with_correct_time(
    user_session: UserSession,
    time_slice_service: TimeSliceService,
    running_slice: RunningTimeSlice,
):
    stopwatch_time = -1

    def on_stopwatch_started(start_time: int):
        nonlocal stopwatch_time
        stopwatch_time = start_time

    user_session.stopwatch.started += on_stopwatch_started
    time_slice_service.start_slice(running_slice)

    assert stopwatch_time == running_slice.duration * 60


def test_pause_slice_is_idempotent(
    time_slice_service: TimeSliceService, running_slice: RunningTimeSlice
):
    time_slice_paused_fired_counter = 0

    def on_time_slice_paused():
        nonlocal time_slice_paused_fired_counter
        time_slice_paused_fired_counter += 1

    time_slice_service.slice_paused += on_time_slice_paused
    time_slice_service.start_slice(running_slice)

    time_slice_service.pause_slice()

    assert time_slice_paused_fired_counter == 1


def test_pause_slice_is_noop_when_there_is_no_time_slice_running(
    time_slice_service: TimeSliceService,
):
    time_slice_paused_fired_counter = 0

    def on_time_slice_paused():
        nonlocal time_slice_paused_fired_counter
        time_slice_paused_fired_counter += 1

    time_slice_service.slice_paused += on_time_slice_paused
    time_slice_service.pause_slice()

    assert time_slice_paused_fired_counter == 0


def test_stopwatch_paused_triggers_time_slice_paused(
    user_session: UserSession,
    time_slice_service: TimeSliceService,
    running_slice: RunningTimeSlice,
):
    time_slice_paused_fired = False

    def on_time_slice_paused():
        nonlocal time_slice_paused_fired
        time_slice_paused_fired = True

    time_slice_service.slice_paused += on_time_slice_paused
    time_slice_service.start_slice(running_slice)
    user_session.stopwatch.pause()

    assert time_slice_paused_fired


def test_stopwatch_finished_triggers_time_slice_finished(
    user_session: UserSession,
    time_slice_service: TimeSliceService,
    timer: MockTimer,
    running_slice: RunningTimeSlice,
):
    time_slice_finished_fired = False

    def on_time_slice_finished():
        nonlocal time_slice_finished_fired
        time_slice_finished_fired = True

    time_slice_service.slice_finished += on_time_slice_finished
    time_slice_service.start_slice(running_slice)

    timer.tick(running_slice.duration * 60 + 2)
    user_session.stopwatch.update_time()

    assert time_slice_finished_fired


def test_finish_time_slice_commits_to_db(
    user_session: UserSession,
    time_slice_service: TimeSliceService,
    timer: MockTimer,
    running_slice: RunningTimeSlice,
    time_slice_repo: TimeSliceRepo,
    today: datetime.datetime,
):

    def on_time_slice_finished():
        slices = time_slice_repo.get_slices_by_date(today)
        assert len(slices) == 1

        time_slice = slices[0]
        assert time_slice.duration == running_slice.duration
        assert time_slice.tag == running_slice.tag
        assert time_slice.description == running_slice.description
        assert time_slice.date.date() == today.date()

    time_slice_service.start_slice(running_slice)

    timer.tick(running_slice.duration * 60 + 2)
    user_session.stopwatch.update_time()


def test_cancel_time_slice_triggers_time_slice_cancelled(
    user_session: UserSession,
    time_slice_service: TimeSliceService,
    running_slice: RunningTimeSlice,
):

    time_slice_cancelled_fired = False

    def on_time_slice_cancelled():
        nonlocal time_slice_cancelled_fired
        time_slice_cancelled_fired = True
        assert user_session.current_time_slice is None

    time_slice_service.slice_cancelled += on_time_slice_cancelled
    time_slice_service.start_slice(running_slice)
    time_slice_service.cancel_slice()

    assert time_slice_cancelled_fired
