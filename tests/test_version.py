from config import settings
from config.version import get_version_info


def test_version_info_contains_runtime_metadata():
    info = get_version_info()

    assert info["application_version"] == settings.APP_VERSION
    assert info["build_type"] == settings.BUILD_TYPE
    assert info["environment"] == settings.ENVIRONMENT
    assert info["python_version"]
    assert info["operating_system"]

