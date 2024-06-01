from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import WARNING

FORM_DATA = {'text': 'Новый текст'}


def test_anonymous_user_cant_create_comment(client, id_for_args):
    """
    Тест на проверку, что анонимный пользователь
    не может создать комментарий.
    """
    url = reverse('news:detail', args=id_for_args)
    client.post(url, data=FORM_DATA)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        autor_comment_client, news, autor_comment, id_for_args):
    """
    Тест на проверку, что зарегистрированный пользователь
    может создать комментарий.
    """
    Comment.objects.all().delete()
    url = reverse('news:detail', args=id_for_args)
    response = autor_comment_client.post(url, data=FORM_DATA)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == autor_comment


def test_user_cant_use_bad_words(
        autor_comment_client, id_for_args, bad_words_data):
    """Тест проверяющий использования запрещенных слов в комментариях."""
    url = reverse('news:detail', args=id_for_args)
    response = autor_comment_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(autor_comment_client, comment, id_for_args):
    """
    Тест проверяющий,
    что автор комментария может удалить свой комментарий.
    """
    url = reverse('news:delete', args=(comment.id,))
    response = autor_comment_client.delete(url)
    url_detail = reverse('news:detail', args=id_for_args)
    expected_url = f'{url_detail}#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_comment_client, comment):
    """
    Тест проверяющий,что зарегистрированный пользователь
    не может удалить чужой комментарий.
    """
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_comment_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        autor_comment_client, comment, news, autor_comment, id_for_args):
    """
    Тест проверяющий,
    что автор комментария может редактировать свой комментарий.
    """
    url = reverse('news:edit', args=(comment.id,))
    response = autor_comment_client.post(url, data=FORM_DATA)
    url_detail = url = reverse('news:detail', args=id_for_args)
    expected_url = f'{url_detail}#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == autor_comment


def test_user_cant_edit_comment_of_another_user(
        not_author_comment_client, comment):
    """
    Тест проверяющий,что зарегистрированный пользователь
    не может редактировать чужой комментарий.
    """
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_comment_client.post(url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != FORM_DATA['text']
