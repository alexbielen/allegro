from allegro.cache import Cache, SerializableError
import os
import pytest


def test_get_cache_dir(mocker):
    expected_cache_dir = "/Users/alexbielen/.cache/allegro"
    mocker.patch.dict(
        "allegro.cache.os.environ", {"XDG_CACHE_HOME": "/Users/alexbielen/.cache"}
    )
    c = Cache()
    assert c.cache_dir == expected_cache_dir


def test_get_cache_dir_fallback(mocker):
    expected_cache_dir = "/Users/alexbielen/.cache/allegro"
    mocker.patch.dict(
        "allegro.cache.os.environ", {"XDG_CACHE_HOME": "", "HOME": "/Users/alexbielen/"}
    )
    c = Cache()
    assert c.cache_dir == expected_cache_dir


def test_create_file(tmpdir, mocker):
    mocker.patch("allegro.cache._get_cache_dir", return_value=tmpdir)
    c = Cache()
    l = [1, 2, 3]
    c.save(l, "cached_list")
    loaded_list = c.load("cached_list")
    assert l == loaded_list


def test_create_file_with_dirname(tmpdir, mocker):
    mocker.patch("allegro.cache._get_cache_dir", return_value=tmpdir)
    c = Cache(cache_dir=tmpdir)
    l = [1, 2, 3]
    c.save(l, "cached_list")
    loaded_list = c.load("cached_list")
    assert l == loaded_list


def test_lookup_file_that_does_not_exist(tmpdir, mocker):
    mocker.patch("allegro.cache._get_cache_dir", return_value=tmpdir)
    c = Cache(cache_dir=tmpdir)

    with pytest.raises(IOError) as e_info:
        filename = "dne.txt"
        c.load(filename)

    expected_message = f"File {os.path.join(tmpdir, filename)} does not exist."
    assert e_info.value.args[0] == expected_message


def test_that_serializable_exception_is_thrown(tmpdir, mocker):
    mocker.patch("allegro.cache._get_cache_dir", return_value=tmpdir)
    c = Cache(cache_dir=tmpdir)

    with pytest.raises(SerializableError) as exc_info:
        c.save(lambda i: i, "function")

    assert exc_info.value.args[0] == "Cannot serialize this object."

