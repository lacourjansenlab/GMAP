"""
A basis for all tests. Things here are available to all tests!
"""

# 3rd party imports
import pytest

# local imports
import GMAP.src.tools.CodingTools as GM_CT


# To report to the user that this file is present and active
@pytest.fixture(scope="session", autouse=True)
def my_fixture(request):
    capmanager = request.config.pluginmanager.getplugin("capturemanager")
    with capmanager.global_and_fixture_disabled():
        print(
            "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            "\n!!!!! Running tests using tests/conftest.py !!!!!"
            "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        )


# To prevent any created singletons leaking between tests.
# https://github.com/pytest-dev/pytest-mock/issues/100
@pytest.fixture(autouse=True)
def reset_singletons():
    GM_CT.Singleton._instances = {}


# If this name can be used as an input name to a test, this file is found
@pytest.fixture(autouse=True)
def fixt_test_presence():
    pass
