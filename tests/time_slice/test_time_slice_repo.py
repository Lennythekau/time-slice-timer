from datetime import datetime

from tag.repo import TagRepo
from time_slice.model import RunningTimeSlice
from time_slice.repo import TimeSliceRepo


def test_add_slice(time_slice_repo: TimeSliceRepo, tag_repo: TagRepo, today: datetime):
    tag = tag_repo.add_tag("test_tag")
    running_slice = RunningTimeSlice("test", tag, 5)
    time_slice = time_slice_repo.add_slice(running_slice, today)

    assert time_slice.tag == tag
    assert time_slice.description == running_slice.description
    assert time_slice.date == today


def test_get_times_by_tag(
    time_slice_repo: TimeSliceRepo, tag_repo: TagRepo, today: datetime
):

    tag1 = tag_repo.add_tag("tag1")
    tag2 = tag_repo.add_tag("tag2")

    slice1 = time_slice_repo.add_slice(RunningTimeSlice("1", tag1, 5), today)
    slice2 = time_slice_repo.add_slice(RunningTimeSlice("2", tag1, 20), today)
    slice3 = time_slice_repo.add_slice(RunningTimeSlice("3", tag2, 10), today)

    predicted_times_by_tag = {
        tag1: slice1.duration + slice2.duration,
        tag2: slice3.duration,
    }

    actual_times_by_tag = time_slice_repo.get_times_by_tag(today)

    for tag, time in actual_times_by_tag:
        assert predicted_times_by_tag[tag] == time
