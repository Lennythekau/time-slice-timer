from tag.model import Tag
import sqlite3

import pytest

from tag.model import EMPTY_TAG
from tag.repo import TagRepo


def test_add_tag_returns_valid_tag(tag_repo: TagRepo):
    TAG_NAME = "foo"
    tag = tag_repo.add_tag(TAG_NAME)
    assert tag.name == TAG_NAME
    assert tag.tag_id != EMPTY_TAG.tag_id


def test_add_tag_raises_error_for_duplicate_name(tag_repo: TagRepo):
    TAG_NAME = "foo"

    tag_repo.add_tag(TAG_NAME)
    with pytest.raises(sqlite3.IntegrityError):
        tag_repo.add_tag(TAG_NAME)


def test_get_tags_without_adding_new_tags_gives_only_empty_tag(tag_repo: TagRepo):
    tags = tag_repo.get_tags()

    assert len(tags) == 1
    assert tags[0] == EMPTY_TAG


def test_get_tags_with_new_tags_added_gives_new_tags_as_well(tag_repo: TagRepo):
    TAG_NAMES = "foo", "bar"

    for name in TAG_NAMES:
        tag_repo.add_tag(name)

    tags = tag_repo.get_tags()

    # the new tags, plus the empty tag
    assert len(tags) == len(TAG_NAMES) + 1

    assert tags[0] == EMPTY_TAG

    # start from 1, as tags[0] must be the empty tag
    for i, name in enumerate(TAG_NAMES, start=1):
        assert tags[i].name == name


def test_remove_tags_fails_silently(tag_repo: TagRepo):
    tag_repo.add_tag("foo")

    tags_before = tag_repo.get_tags()
    tag_repo.delete_tag("bar")
    tags_after = tag_repo.get_tags()

    assert tags_before == tags_after


def test_remove_tags_is_accurate(tag_repo: TagRepo):
    tag_repo.add_tag("foo")
    tag_repo.add_tag("bar")

    predicted_tags = [tag for tag in tag_repo.get_tags() if tag.name != "bar"]

    tag_repo.delete_tag("bar")
    actual_tags = tag_repo.get_tags()

    assert predicted_tags == actual_tags


def test_edit_tag(tag_repo: TagRepo):
    tag_repo.add_tag("foo")
    tag_repo.add_tag("bar")

    predicted_tags = tag_repo.get_tags()

    # foo is at index 1, after the empty tag
    predicted_tags[1] = Tag(predicted_tags[1].tag_id, "new_foo")

    tag_repo.edit_tag("foo", "new_foo")
    actual_tags = tag_repo.get_tags()

    assert predicted_tags == actual_tags
