from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA = {'text': 'New comment'}
UPDATED_FORM_DATA = {'text': 'Updated comment'}
FOREIGN_FORM_DATA = {'text': 'Foreign comment'}


def test_anonymous_user_cannot_create_comment(client, detail_url, login_url):
    comments_count = Comment.objects.count()
    response = client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, f'{login_url}?next={detail_url}')
    assert Comment.objects.count() == comments_count


def test_authorized_user_can_create_comment(
    author_client,
    author,
    news,
    detail_url,
):
    comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comments_count + 1
    comment = Comment.objects.get(text=FORM_DATA['text'])
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_bad_words_is_not_created(
    author_client,
    detail_url,
    bad_word,
):
    comments_count = Comment.objects.count()
    bad_data = {'text': f'Text {bad_word}'}
    response = author_client.post(detail_url, data=bad_data)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == comments_count
    assertFormError(response.context['form'], 'text', [WARNING])


def test_author_can_edit_own_comment(
    author_client,
    comment,
    edit_url,
    detail_url,
):
    form_data = UPDATED_FORM_DATA.copy()
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_reader_cannot_edit_foreign_comment(
    reader_client,
    comment,
    edit_url,
):
    response = reader_client.post(edit_url, data=FOREIGN_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Comment text'


def test_author_can_delete_own_comment(
    author_client,
    comment,
    delete_url,
    detail_url,
):
    comments_count = Comment.objects.count()
    response = author_client.post(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comments_count - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_reader_cannot_delete_foreign_comment(
    reader_client,
    comment,
    delete_url,
):
    comments_count = Comment.objects.count()
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count
    assert Comment.objects.filter(pk=comment.pk).exists()
