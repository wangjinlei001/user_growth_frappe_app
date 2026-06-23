import subprocess
from pathlib import Path


APP_ROOT = Path(
	subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
)


def read_readme():
	return (APP_ROOT / "README.md").read_text(encoding="utf-8")


def test_repository_root_contains_frappe_app_metadata():
	assert (APP_ROOT / "pyproject.toml").is_file()
	assert (APP_ROOT / "README.md").is_file()
	assert (APP_ROOT / "user_growth" / "hooks.py").is_file()


def test_repository_excludes_tracked_bench_runtime_paths():
	tracked_files = subprocess.check_output(
		["git", "ls-files"], cwd=APP_ROOT, text=True
	).splitlines()

	for path in tracked_files:
		assert not path.startswith(("apps/", "sites/", "logs/", "config/", "env/"))
		assert path not in {"Procfile", "patches.txt"}


def test_readme_install_command_uses_this_repository_url():
	readme = read_readme()

	assert "bench get-app https://github.com/wangjinlei001/user_growth_frappe_app --branch main" in readme
	assert "$URL_OF_THIS_REPO" not in readme


def test_readme_paths_match_standalone_app_layout():
	readme = read_readme()

	assert "../../" not in readme
	assert "apps/user_growth" not in readme
