from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(username='author')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(username='reader')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='News title', text='News text')


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Comment text',
    )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def all_news():
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    today = timezone.now().date()
    News.objects.bulk_create(
        News(
            title=f'News {index}',
            text='News text',
            date=today - timedelta(days=index),
        )
        for index in range(news_count)
    )
    return News.objects.order_by('-date')


@pytest.fixture
def all_comments(author, news):
    now = timezone.now()
    for index in range(3):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Comment {index}',
        )
        comment.created = now + timedelta(minutes=index)
        comment.save(update_fields=('created',))
    return Comment.objects.filter(news=news).order_by('created')
