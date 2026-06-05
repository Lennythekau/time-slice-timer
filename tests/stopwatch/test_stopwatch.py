import pytest
from pytest import approx
from stopwatch.model import StopwatchModel
from tests.stopwatch.mock_timer import MockTimer

START_TIME = 10


@pytest.fixture
def timer():
    return MockTimer()


@pytest.fixture
def stopwatch(timer: MockTimer):
    return StopwatchModel(timer.get_time)


def test_initial_time(stopwatch: StopwatchModel):
    stopwatch_time_limit = -1

    def on_stopwatch_started(time_limit: int):
        nonlocal stopwatch_time_limit
        stopwatch_time_limit = time_limit

    stopwatch.started += on_stopwatch_started
    stopwatch.start(START_TIME)

    assert stopwatch.update_time() == START_TIME
    assert stopwatch_time_limit == START_TIME


def test_get_time_after_ticking(stopwatch: StopwatchModel, timer: MockTimer):
    target_time = START_TIME

    ticks = 3.7, 0.8, 1.9

    stopwatch.start(START_TIME)

    for tick in ticks:
        timer.tick(tick)
        target_time -= tick

        assert stopwatch.update_time() == approx(target_time)
        assert not stopwatch.is_finished
        assert not stopwatch.is_paused


def test_pause_gives_correct_state(stopwatch: StopwatchModel, timer: MockTimer):
    paused_triggered = False

    def on_stopwatch_paused(_):
        nonlocal paused_triggered
        paused_triggered = True

    stopwatch.paused += on_stopwatch_paused

    stopwatch.start(START_TIME)

    tick = 1.9
    timer.tick(tick)
    target_time = START_TIME - tick

    stopwatch.pause()

    assert stopwatch.update_time() == approx(target_time)
    assert not stopwatch.is_finished
    assert stopwatch.is_paused
    assert paused_triggered


def test_pause_ignores_time_ticking(stopwatch: StopwatchModel, timer: MockTimer):
    stopwatch.start(START_TIME)

    tick = 1.9
    timer.tick(tick)
    target_time = START_TIME - tick

    stopwatch.pause()

    timer.tick(19203293)

    assert stopwatch.update_time() == approx(target_time)


def test_cancel(stopwatch: StopwatchModel, timer: MockTimer):
    cancelled_triggered = False

    def on_stopwatch_cancel(_):
        nonlocal cancelled_triggered
        cancelled_triggered = True

    stopwatch.cancelled += on_stopwatch_cancel

    stopwatch.start(START_TIME)
    timer.tick(3)
    stopwatch.cancel()

    assert stopwatch.update_time() == approx(StopwatchModel.UNSET)
    assert stopwatch.is_paused
    assert not stopwatch.is_finished
    assert cancelled_triggered
