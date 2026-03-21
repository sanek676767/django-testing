from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cannot_create_comment(client, detail_url, form_data):
    comments_count = Comment.objects.count()
    login_url = reverse('users:login')
    response = client.post(detail_url, data=form_data)
    assertRedirects(response, f'{login_url}?next={detail_url}')
    assert Comment.objects.count() == comments_count


def test_authorized_user_can_create_comment(
    author_client,
    author,
    news,
    detail_url,
    form_data,
):
    comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comments_count + 1
    comment = Comment.objects.get(text=form_data['text'])
    assert comment.author == author
    assert comment.news == news


def test_comment_with_bad_words_is_not_created(
    author_client,
    detail_url,
):
    bad_data = {'text': f'Текст {BAD_WORDS[0]}'}
    response = author_client.post(detail_url, data=bad_data)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0
    assert WARNING in response.context['form'].errors['text']


def test_author_can_edit_own_comment(author_client, comment, edit_url, detail_url):
    response = author_client.post(edit_url, data={'text': 'Обновлённый текст'})
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == 'Обновлённый текст'


def test_other_user_cannot_edit_foreign_comment(
    reader_client,
    comment,
    edit_url,
):
    response = reader_client.post(edit_url, data={'text': 'Чужой текст'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


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


def test_other_user_cannot_delete_foreign_comment(
    reader_client,
    comment,
    delete_url,
):
    comments_count = Comment.objects.count()
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count
    assert Comment.objects.filter(pk=comment.pk).exists()
