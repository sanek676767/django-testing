from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News


pytestmark = pytest.mark.django_db


def test_home_page_contains_not_more_than_ten_news(client):
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    today = timezone.now().date()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст',
            date=today - timedelta(days=index),
        )
        for index in range(news_count)
    )
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_on_home_page_are_sorted_from_newest_to_oldest(client):
    today = timezone.now().date()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст',
            date=today - timedelta(days=index),
        )
        for index in range(3)
    )
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    dates = [news_item.date for news_item in object_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_on_detail_page_are_sorted_from_old_to_new(
    client,
    news,
    detail_url,
    author,
):
    now = timezone.now()
    for index in range(3):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        comment.created = now + timedelta(minutes=index)
        comment.save(update_fields=('created',))
    response = client.get(detail_url)
    news_from_context = response.context['news']
    created_dates = [
        comment.created for comment in news_from_context.comment_set.all()
    ]
    assert created_dates == sorted(created_dates)


def test_anonymous_user_has_no_comment_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_user_has_comment_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
