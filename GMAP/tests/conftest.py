"""
A basis for all tests. Things here are available to all tests!
"""

# 3rd party imports
import pytest

import matplotlib
matplotlib.use("Agg")  # need to set this before further mpl imports
# Agg should be faster, and less error prone. Disable this if you encounter
# weird mpl errors.

# local imports
import GMAP.src.tools.coding_tools as GM_ct
import GMAP.src.tools.file_handler as GM_fh


# To report to the user that this file is present and active
# def pytest_sessionstart(session):  # runs immediately after cmd
def pytest_collection_finish(session):  # runs just before executing tests
    capmanager = session.config.pluginmanager.getplugin("capturemanager")

    with capmanager.global_and_fixture_disabled():
        print(
            "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            "\n!!!!! Running tests using tests/conftest.py !!!!!"
            "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        )

# @pytest.fixture(scope="session", autouse=True)
# def my_fixture(request):
#     capmanager = request.config.pluginmanager.getplugin("capturemanager")
#     with capmanager.global_and_fixture_disabled():
#         print(
#             "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
#             "\n!!!!! Running tests using tests/conftest.py !!!!!"
#             "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
#         )


# To prevent any created singletons leaking between tests.
# https://github.com/pytest-dev/pytest-mock/issues/100
# @pytest.fixture()
# def reset_singletons():
#     GM_CT.Singleton._instances = {}


# @pytest.fixture()
# def init_files():
#     GM_FH.FileLocations()


@pytest.fixture(autouse=True)
def pre_test(request):
    GM_ct.Singleton._instances = {}
    if "nofiles" in request.keywords:
        return
    GM_fh.FileLocations()


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "nofiles: mark test to not auto-load files"
    )
