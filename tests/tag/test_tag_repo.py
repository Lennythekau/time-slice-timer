import sqlite3

import pytest

from tag.model import EMPTY_TAG, Tag
from tag.repo import TagRepo
from tag.service import TagService


def test_add_tag_returns_valid_tag(tag_service: TagService):
    TAG_NAME = "foo"
    tag, err = tag_service.add_tag(TAG_NAME)

    assert tag is not None
    assert tag.name == TAG_NAME
    assert tag.tag_id != EMPTY_TAG.tag_id
    assert err == ""


def test_tag_repo_add_tag_raises_error_for_duplicate_name(tag_repo: TagRepo):
    TAG_NAME = "foo"

    tag_repo.add_tag(TAG_NAME)
    with pytest.raises(sqlite3.IntegrityError):
        tag_repo.add_tag(TAG_NAME)


def test_tag_repo_get_tags_without_adding_new_tags_gives_nothing(tag_repo: TagRepo):
    tags = tag_repo.get_tags()
    assert tags == []


def test_tag_repo_get_tags_with_new_tags_added_gives_new_tags_as_well(
    tag_repo: TagRepo,
):
    TAG_NAMES = "foo", "bar"

    for name in TAG_NAMES:
        tag_repo.add_tag(name)

    tags = tag_repo.get_tags()
    assert tuple(tag.name for tag in tags) == TAG_NAMES


# TODO: change to service
def test_remove_tags_fails_silently(tag_repo: TagRepo):
    tag = tag_repo.add_tag("foo")

    tags_before = tag_repo.get_tags()
    tag_repo.delete_tag(Tag(1000, "foo").tag_id)
    tags_after = tag_repo.get_tags()

    assert tags_before == tags_after


def test_remove_tags_is_accurate(tag_repo: TagRepo):
    tag_repo.add_tag("foo")
    tag = tag_repo.add_tag("bar")

    predicted_tags = [tag for tag in tag_repo.get_tags() if tag.name != "bar"]

    tag_repo.delete_tag(tag.tag_id)
    actual_tags = tag_repo.get_tags()

    assert predicted_tags == actual_tags


def test_edit_tag(tag_repo: TagRepo):
    tag_0 = tag_repo.add_tag("foo")
    tag_repo.add_tag("bar")

    predicted_tags = tag_repo.get_tags()

    # foo is at index 1, after the empty tag
    predicted_tags[0] = tag_0._replace(name="new_foo")

    tag_repo.edit_tag(tag_0.tag_id, "new_foo")
    actual_tags = tag_repo.get_tags()

    assert predicted_tags == actual_tags
