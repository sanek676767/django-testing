from notes.forms import NoteForm

from .common import ADD_URL, LIST_URL, BaseNoteTestCase


class TestNoteContent(BaseNoteTestCase):

    def test_author_note_is_in_object_list(self):
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_other_user_note_is_not_in_object_list(self):
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.other_note, object_list)

    def test_add_and_edit_pages_contain_note_form(self):
        for url in (ADD_URL, self.edit_url):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                form = response.context.get('form')
                self.assertIsInstance(form, NoteForm)
