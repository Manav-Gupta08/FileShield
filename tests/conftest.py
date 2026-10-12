import os
import tempfile
import sys


TEST_ROOT = tempfile.TemporaryDirectory(prefix="fileshield-tests-")
os.environ["FILESHIELD_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///" + TEST_ROOT.name.replace("\\", "/") + "/test.db"
os.environ["STORAGE_ROOT"] = TEST_ROOT.name + "/jobs"
os.environ["FILESHIELD_SECRET_KEY"] = "42" * 32
os.environ["REQUIRE_SCAN"] = "false"
os.environ["REDIS_URL"] = ""


def pytest_sessionfinish(session, exitstatus):
	if "backend.database" in sys.modules:
		sys.modules["backend.database"].engine.dispose()
	TEST_ROOT.cleanup()