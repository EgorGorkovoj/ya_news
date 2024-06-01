from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment
from news.forms import BAD_WORDS


@pytest.fixture
def autor_comment(django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def not_author_comment(django_user_model):
    return django_user_model.objects.create(username='Не автор комментария')


@pytest.fixture
def autor_comment_client(autor_comment):
    client = Client()
    client.force_login(autor_comment)
    return client


@pytest.fixture
def not_author_comment_client(not_author_comment):
    client = Client()
    client.force_login(not_author_comment)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def news_on_homepage():
    today = datetime.today()
    all_news = [
        News.objects.create(
            title=f'Заголовок {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return all_news


@pytest.fixture
def comment(autor_comment, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=autor_comment
    )
    return comment


@pytest.fixture
def comment_sort(autor_comment, news):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=autor_comment, text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def id_for_args(news):
    return (news.id,)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
