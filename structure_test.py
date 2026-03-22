from pathlib import Path


REQUIRED_PATHS = (
    'ya_news',
    'ya_news/news',
    'ya_news/news/fixtures',
    'ya_news/news/migrations',
    'ya_news/news/pytest_tests',
    'ya_news/news/__init__.py',
    'ya_news/news/admin.py',
    'ya_news/news/apps.py',
    'ya_news/news/forms.py',
    'ya_news/news/models.py',
    'ya_news/news/urls.py',
    'ya_news/news/views.py',
    'ya_news/templates',
    'ya_news/yanews',
    'ya_news/manage.py',
    'ya_news/pytest.ini',
    'ya_news/README.md',
    'ya_note',
    'ya_note/notes',
    'ya_note/notes/migrations',
    'ya_note/notes/tests',
    'ya_note/notes/admin.py',
    'ya_note/notes/apps.py',
    'ya_note/notes/forms.py',
    'ya_note/notes/__init__.py',
    'ya_note/notes/models.py',
    'ya_note/notes/urls.py',
    'ya_note/notes/views.py',
    'ya_note/templates',
    'ya_note/yanote',
    'ya_note/manage.py',
    'ya_note/pytest.ini',
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
