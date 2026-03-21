from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='note_author')
        cls.reader = User.objects.create_user(username='note_reader')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Исходная заметка',
            text='Первый текст',
            slug='initial-slug',
            author=cls.author,
        )
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_authorized_user_can_create_note(self):
        notes_count = Note.objects.count()
        form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note-slug',
        }
        response = self.author_client.post(self.add_url, data=form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        note = Note.objects.get(slug=form_data['slug'])
        self.assertEqual(note.title, form_data['title'])
        self.assertEqual(note.text, form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        notes_count = Note.objects.count()
        form_data = {
            'title': 'Анонимная заметка',
            'text': 'Текст',
            'slug': 'anonymous-slug',
        }
        response = self.client.post(self.add_url, data=form_data)
        self.assertRedirects(
            response,
            f'{self.login_url}?next={self.add_url}',
        )
        self.assertEqual(Note.objects.count(), notes_count)

    def test_duplicate_slug_is_not_allowed(self):
        notes_count = Note.objects.count()
        form_data = {
            'title': 'Дубликат slug',
            'text': 'Текст',
            'slug': self.note.slug,
        }
        response = self.author_client.post(self.add_url, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), notes_count)
        form_errors = response.context['form'].errors['slug']
        self.assertIn(self.note.slug + WARNING, form_errors)

    def test_empty_slug_is_filled_automatically(self):
        title = 'Заметка без slug'
        notes_count = Note.objects.count()
        response = self.author_client.post(
            self.add_url,
            data={
                'title': title,
                'text': 'Текст без slug',
                'slug': '',
            },
        )
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        note = Note.objects.get(title=title)
        self.assertEqual(note.slug, slugify(title))

    def test_author_can_edit_own_note(self):
        response = self.author_client.post(
            self.edit_url,
            data={
                'title': 'Обновлённая заметка',
                'text': 'Новый текст',
                'slug': 'updated-slug',
            },
        )
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Обновлённая заметка')
        self.assertEqual(self.note.text, 'Новый текст')
        self.assertEqual(self.note.slug, 'updated-slug')

    def test_other_user_cannot_edit_foreign_note(self):
        response = self.reader_client.post(
            self.edit_url,
            data={
                'title': 'Чужое изменение',
                'text': 'Чужой текст',
                'slug': 'foreign-slug',
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Исходная заметка')
        self.assertEqual(self.note.text, 'Первый текст')
        self.assertEqual(self.note.slug, 'initial-slug')

    def test_author_can_delete_own_note(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_other_user_cannot_delete_foreign_note(self):
        notes_count = Note.objects.count()
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

