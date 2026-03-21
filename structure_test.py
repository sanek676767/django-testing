from pathlib import Path


REQUIRED_PATHS = (
    'ya-news',
    'ya-news/news',
    'ya-news/news/fixtures',
    'ya-news/news/migrations',
    'ya-news/news/pytest_tests',
    'ya-news/news/__init__.py',
    'ya-news/news/admin.py',
    'ya-news/news/apps.py',
    'ya-news/news/forms.py',
    'ya-news/news/models.py',
    'ya-news/news/urls.py',
    'ya-news/news/views.py',
    'ya-news/templates',
    'ya-news/yanews',
    'ya-news/manage.py',
    'ya-news/pytest.ini',
    'ya-news/README.md',
    'ya-note',
    'ya-note/notes',
    'ya-note/notes/migrations',
    'ya-note/notes/tests',
    'ya-note/notes/admin.py',
    'ya-note/notes/apps.py',
    'ya-note/notes/forms.py',
    'ya-note/notes/__init__.py',
    'ya-note/notes/models.py',
    'ya-note/notes/urls.py',
    'ya-note/notes/views.py',
    'ya-note/templates',
    'ya-note/yanote',
    'ya-note/manage.py',
    'ya-note/pytest.ini',
    '.gitignore',
    'requirements.txt',
    'structure_test.py',
)


def get_missing_paths():
    root = Path(__file__).resolve().parent
    return [path for path in REQUIRED_PATHS if not (root / path).exists()]


def test_required_structure():
    missing_paths = get_missing_paths()
    assert not missing_paths, f'Missing paths: {missing_paths}'


if __name__ == '__main__':
    missing_paths = get_missing_paths()
    if missing_paths:
        raise SystemExit(f'Missing paths: {missing_paths}')
    print('Required structure is in place.')

