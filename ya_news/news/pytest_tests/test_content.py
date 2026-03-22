from django.conf import settings

from news.forms import CommentForm


def test_home_page_contains_not_more_than_ten_news(
    client,
    home_url,
    all_news,
):
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_on_home_page_are_sorted_from_newest_to_oldest(
    client,
    home_url,
    all_news,
):
    response = client.get(home_url)
    object_list = response.context['object_list']
    dates = [news_item.date for news_item in object_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_on_detail_page_are_sorted_from_old_to_new(
    client,
    detail_url,
    all_comments,
):
    response = client.get(detail_url)
    comments = response.context['news'].comment_set.all()
    created_dates = [comment.created for comment in comments]
    assert created_dates == sorted(created_dates)


def test_anonymous_user_has_no_comment_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_user_has_comment_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert isinstance(response.context.get('form'), CommentForm)
