import platform
import sys

from config import settings


def get_version_info():
    return {
        "application_version": settings.APP_VERSION,
        "build_type": settings.BUILD_TYPE,
        "environment": settings.ENVIRONMENT,
        "python_version": sys.version.split()[0],
        "operating_system": platform.platform(),
    }

