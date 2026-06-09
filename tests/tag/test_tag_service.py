from tag.model import EMPTY_TAG, Tag
from tag.service import TagService


def test_tag_service_add_tag_returns_valid_tag(tag_service: TagService):
    TAG_NAME = "foo"
    tag, err = tag_service.add_tag(TAG_NAME)

    assert tag is not None
    assert tag.name == TAG_NAME
    assert tag.tag_id != EMPTY_TAG.tag_id


def test_tag_service_add_tag_returns_error_for_duplicate_name(tag_service: TagService):
    TAG_NAME = "foo"

    tag_service.add_tag(TAG_NAME)
    tag, err = tag_service.add_tag(TAG_NAME)

    assert tag is None
    assert err != ""


def test_tag_service_add_tag_returns_error_for_empty_string_name(
    tag_service: TagService,
):
    tag, err = tag_service.add_tag("")

    assert tag is None
    assert err != ""


def test_tag_service_get_tags_without_adding_new_tags_gives_empty_tag(
    tag_service: TagService,
):
    tags = list(tag_service.get_tags().values())
    assert tags == [EMPTY_TAG]


def test_tag_service_get_tags_with_new_tags_added_gives_new_tags_as_well(
    tag_service: TagService,
):
    TAG_NAMES = "foo", "bar"

    for name in TAG_NAMES:
        tag_service.add_tag(name)

    # we do [1:] because the tag at index 0 is the empty tag
    tags = list(tag_service.get_tags().values())[1:]

    assert tuple(tag.name for tag in tags) == TAG_NAMES


def test_delete_tag_fails_silently(tag_service: TagService):
    tag, err = tag_service.add_tag("foo")

    tags_before = tag_service.get_tags()
    tag_service.delete_tag(Tag(1000, "foo").tag_id)
    tags_after = tag_service.get_tags()

    assert tags_before == tags_after


def test_delete_tag_is_accurate(tag_service: TagService):
    tag_service.add_tag("foo")
    tag, err = tag_service.add_tag("bar")

    predicted_tags = [
        tag for tag in tag_service.get_tags().values() if tag.name != "bar"
    ]

    assert tag is not None
    tag_service.delete_tag(tag.tag_id)
    actual_tags = list(tag_service.get_tags().values())

    assert predicted_tags == actual_tags


def test_edit_tag_gives_updated_tag(tag_service: TagService):
    tag_0, err = tag_service.add_tag("foo")
    tag_service.add_tag("bar")

    predicted_tags = tag_service.get_tags()

    assert tag_0 is not None
    # foo is at index 1, after the empty tag
    predicted_tags[1] = tag_0._replace(name="new_foo")

    tag_service.edit_tag(tag_0.tag_id, "new_foo")
    actual_tags = tag_service.get_tags()

    assert predicted_tags == actual_tags


def test_edit_tag_with_new_name_as_empty_string_returns_error(tag_service: TagService):
    tag, err = tag_service.add_tag("foo")
    assert tag is not None

    new_tag, err = tag_service.edit_tag(tag.tag_id, "")

    assert new_tag is None
    assert err != ""


def test_edit_tag_with_new_name_as_duplicate_returns_error(tag_service: TagService):
    TAG_NAME = "foo"
    tag_service.add_tag(TAG_NAME)
    tag, err = tag_service.add_tag(TAG_NAME + "d")
    assert tag is not None

    new_tag, err = tag_service.edit_tag(tag.tag_id, TAG_NAME)

    assert new_tag is None
    assert err != ""
