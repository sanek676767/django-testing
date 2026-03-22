from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .common import (
    ADD_URL,
    LOGIN_URL,
    NOTE_TEXT,
    NOTE_TITLE,
    SUCCESS_URL,
    BaseNoteTestCase,
)


class TestNoteLogic(BaseNoteTestCase):

    def test_authorized_user_can_create_note(self):
        notes_count = Note.objects.count()
        form_data = {
            'title': 'New note',
            'text': 'New note text',
            'slug': 'new-note-slug',
        }
        response = self.author_client.post(ADD_URL, data=form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        note = Note.objects.get(slug=form_data['slug'])
        self.assertEqual(note.title, form_data['title'])
        self.assertEqual(note.text, form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        notes_count = Note.objects.count()
        form_data = {
            'title': 'Anonymous note',
            'text': 'Anonymous text',
            'slug': 'anonymous-slug',
        }
        response = self.client.post(ADD_URL, data=form_data)
        self.assertRedirects(response, f'{LOGIN_URL}?next={ADD_URL}')
        self.assertEqual(Note.objects.count(), notes_count)

    def test_duplicate_slug_is_not_allowed(self):
        notes_count = Note.objects.count()
        form_data = {
            'title': 'Duplicate slug',
            'text': 'Duplicate text',
            'slug': self.note.slug,
        }
        response = self.author_client.post(ADD_URL, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), notes_count)
        self.assertFormError(
            response.context['form'],
            'slug',
            [self.note.slug + WARNING],
        )

    def test_empty_slug_is_filled_automatically(self):
        form_data = {
            'title': 'Note without slug',
            'text': 'Text without slug',
            'slug': '',
        }
        notes_count = Note.objects.count()
        response = self.author_client.post(ADD_URL, data=form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        note = Note.objects.get(title=form_data['title'])
        self.assertEqual(note.slug, slugify(form_data['title']))

    def test_author_can_edit_own_note(self):
        form_data = {
            'title': 'Updated note',
            'text': 'Updated text',
            'slug': 'updated-slug',
        }
        response = self.author_client.post(self.edit_url, data=form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, form_data['title'])
        self.assertEqual(self.note.text, form_data['text'])
        self.assertEqual(self.note.slug, form_data['slug'])

    def test_reader_cannot_edit_foreign_note(self):
        response = self.reader_client.post(
            self.edit_url,
            data={
                'title': 'Foreign update',
                'text': 'Foreign text',
                'slug': 'foreign-slug',
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NOTE_TITLE)
        self.assertEqual(self.note.text, NOTE_TEXT)
        self.assertEqual(self.note.slug, 'note-slug')

    def test_author_can_delete_own_note(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_reader_cannot_delete_foreign_note(self):
        notes_count = Note.objects.count()
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
