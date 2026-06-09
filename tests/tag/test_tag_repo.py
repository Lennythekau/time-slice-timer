import sqlite3

import pytest

from tag.repo import TagRepo

# Most testing of TagRepo can be done in the tests for TagService, since it uses TagRepo substantially.


def test_tag_repo_add_tag_raises_error_for_duplicate_name(tag_repo: TagRepo):
    TAG_NAME = "foo"

    tag_repo.add_tag(TAG_NAME)
    with pytest.raises(sqlite3.IntegrityError):
        tag_repo.add_tag(TAG_NAME)


def test_tag_repo_get_tags_without_adding_new_tags_gives_nothing(tag_repo: TagRepo):
    tags = tag_repo.get_tags()
    assert tags == []
