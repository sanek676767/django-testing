from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestNoteContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='note_author')
        cls.other_user = User.objects.create_user(username='another_user')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заметка автора',
            text='Текст автора',
            slug='author-slug',
            author=cls.author,
        )
        cls.other_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст другого автора',
            slug='other-slug',
            author=cls.other_user,
        )
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_author_note_is_in_object_list(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_other_user_note_is_not_in_object_list(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.other_note, object_list)

    def test_add_and_edit_pages_contain_note_form(self):
        for url in (self.add_url, self.edit_url):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
