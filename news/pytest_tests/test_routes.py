import pytest
from pytest_django.asserts import assertRedirects  # type: ignore
from http import HTTPStatus

from django.urls import reverse



@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, news_object):
    """Тест доступности различных страниц для анонимных пользователей."""
    if news_object is not None:
        url = reverse(name, args=(news_object.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (
            pytest.lazy_fixture('not_author_comment_client'),
            HTTPStatus.NOT_FOUND
        ),
        (pytest.lazy_fixture('autor_comment_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_pages_availability_comment_for_different_users(
    parametrized_client, expected_status, name, comment
):
    """
    Тест доступности страниц редактирования и
    удаления комментариев для различных пользователей.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    return response.status_code == expected_status


@pytest.mark.parametrize(
    'name, comment_object',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment'))
    ),
)
def test_redirect_for_anonymous_client(client, name, comment_object):
    """
    Тест проверки перенаправления анонимного пользователя,
    который пытается редактировать или удалять чужие комментарии.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment_object.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
