from types import SimpleNamespace

from vocareum_plugin import plugin


def test_pytest_configure_sets_results():
    config = SimpleNamespace()
    plugin.pytest_configure(config)
    assert hasattr(config, "vocareum_results")
    assert config.vocareum_results == []


def test_get_marker_arg_with_marker():
    marker = SimpleNamespace(args=["custom"])
    assert plugin._get_marker_arg(marker) == "custom"


def test_get_marker_arg_without_marker():
    assert plugin._get_marker_arg(None, default="fallback") == "fallback"


def test_get_user_property_found():
    report = SimpleNamespace(
        user_properties=[("key1", 42), ("vocareum_test_name", "hello")]
    )
    assert plugin._get_user_property(report, "vocareum_test_name") == "hello"


def test_get_user_property_not_found():
    report = SimpleNamespace(user_properties=[("other", 99)])
    assert plugin._get_user_property(report, "missing") is None
