from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='username')
        cls.user2 = User.objects.create_user(username='username_2')
        cls.authorized_client = Client()
        cls.authorized_client_2 = Client()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Т' * 20,
        )

    def setUp(self):
        cache.clear()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user2)

    def test_guest_client_pages(self):
        url_response = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list', args={self.group.slug}): HTTPStatus.OK,
            reverse('posts:profile', args={self.user}): HTTPStatus.OK,
            reverse('posts:post_detail', args={self.post.pk}): HTTPStatus.OK,
            '/unexisting_page': HTTPStatus.NOT_FOUND,
        }
        for address, code in url_response.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, code)

    def test_guest_client_redirect(self):
        url_redirect = {
            reverse('posts:post_edit', args={self.post.pk}):
                reverse('users:login') + f'?next=/posts/{self.post.pk}/edit/',
            reverse('posts:add_comment', args={self.post.pk}):
                reverse('users:login')
                + f'?next=/posts/{self.post.pk}/comment/',
            reverse('posts:post_create'):
                reverse('users:login') + '?next=/create/',
            reverse('posts:profile_follow', args={self.user}):
                reverse('users:login') + f'?next=/profile/{self.user}/follow/',
        }
        for address, redirect in url_redirect.items():
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                self.assertRedirects(response, redirect)

    def test_authorized_pages(self):
        url_response = {
            reverse('posts:post_edit', args={self.post.pk}): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse('posts:follow_index'): HTTPStatus.OK,
        }
        for address, code in url_response.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_another_authorized_redirect(self):
        response = self.authorized_client_2.get(
            reverse('posts:post_edit', args={self.post.pk}),
            follow=True)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args={self.post.pk})
        )
