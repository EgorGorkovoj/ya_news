import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_news_count(client, news_on_homepage):
    """Тестирование новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_on_homepage):
    """
    Тестирование сортировки новостей на главной странице, от новой к старой.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, comment_sort, id_for_args):
    """
    Тестирование сортировки комментариев на отдельной странице новости,
    от старого к новому.
    """
    url = reverse('news:detail', args=id_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, id_for_args):
    """Тест доступности формы для анонимных пользователей."""
    url = reverse('news:detail', args=id_for_args)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(autor_comment_client, id_for_args):
    """Тест доступности формы для авторизованных пользователей."""
    url = reverse('news:detail', args=id_for_args)
    response = autor_comment_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
