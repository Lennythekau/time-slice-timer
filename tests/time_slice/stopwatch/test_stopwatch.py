from pytest import approx

from tests.conftest import MockTimer
from time_slice.stopwatch.model import Stopwatch

START_TIME = 10


def test_initial_time(stopwatch: Stopwatch):
    stopwatch_time_limit = -1

    def on_stopwatch_started(time_limit: int):
        nonlocal stopwatch_time_limit
        stopwatch_time_limit = time_limit

    stopwatch.started += on_stopwatch_started
    stopwatch.start(START_TIME)

    assert stopwatch.update_time() == START_TIME
    assert stopwatch_time_limit == START_TIME


def test_get_time_after_ticking(stopwatch: Stopwatch, timer: MockTimer):
    target_time = START_TIME

    ticks = 3.7, 0.8, 1.9

    stopwatch.start(START_TIME)

    for tick in ticks:
        timer.tick(tick)
        target_time -= tick

        assert stopwatch.update_time() == approx(target_time)
        assert not stopwatch.is_finished
        assert not stopwatch.is_paused


def test_pause_gives_correct_state(stopwatch: Stopwatch, timer: MockTimer):
    paused_triggered = False

    def on_stopwatch_paused():
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


def test_pause_ignores_time_ticking(stopwatch: Stopwatch, timer: MockTimer):
    stopwatch.start(START_TIME)

    tick = 1.9
    timer.tick(tick)
    target_time = START_TIME - tick

    stopwatch.pause()

    timer.tick(19203293)

    assert stopwatch.update_time() == approx(target_time)


def test_cancel(stopwatch: Stopwatch, timer: MockTimer):
    cancelled_triggered = False

    def on_stopwatch_cancel():
        nonlocal cancelled_triggered
        cancelled_triggered = True

    stopwatch.cancelled += on_stopwatch_cancel

    stopwatch.start(START_TIME)
    timer.tick(3)
    stopwatch.cancel()

    assert stopwatch.update_time() == Stopwatch.UNSET
    assert stopwatch.is_paused
    assert not stopwatch.is_finished
    assert cancelled_triggered


def test_finish(stopwatch: Stopwatch, timer: MockTimer):
    finished_triggered = False

    def on_stopwatch_finish():
        nonlocal finished_triggered
        finished_triggered = True

    stopwatch.finished += on_stopwatch_finish

    stopwatch.start(START_TIME)

    timer.tick(START_TIME / 2)
    stopwatch.update_time()
    assert not finished_triggered

    timer.tick(START_TIME / 2)
    stopwatch.update_time()

    timer.tick(0.3)
    stopwatch.update_time()

    assert finished_triggered
