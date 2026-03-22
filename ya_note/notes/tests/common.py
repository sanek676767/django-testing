from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


NOTE_SLUG = 'note-slug'
OTHER_NOTE_SLUG = 'other-note-slug'
NOTE_TITLE = 'Author note'
NOTE_TEXT = 'Author text'
OTHER_NOTE_TITLE = 'Reader note'
OTHER_NOTE_TEXT = 'Reader text'

HOME_URL = reverse('notes:home')
ADD_URL = reverse('notes:add')
LIST_URL = reverse('notes:list')
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
SIGNUP_URL = reverse('users:signup')
LOGOUT_URL = reverse('users:logout')

User = get_user_model()


def get_detail_url(slug):
    return reverse('notes:detail', args=(slug,))


def get_edit_url(slug):
    return reverse('notes:edit', args=(slug,))


def get_delete_url(slug):
    return reverse('notes:delete', args=(slug,))


class BaseNoteTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='note_author')
        cls.reader = User.objects.create_user(username='note_reader')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author,
        )
        cls.other_note = Note.objects.create(
            title=OTHER_NOTE_TITLE,
            text=OTHER_NOTE_TEXT,
            slug=OTHER_NOTE_SLUG,
            author=cls.reader,
        )
        cls.detail_url = get_detail_url(NOTE_SLUG)
        cls.edit_url = get_edit_url(NOTE_SLUG)
        cls.delete_url = get_delete_url(NOTE_SLUG)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
