import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='username')
        cls.user2 = User.objects.create_user(username='username2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        for i in range(1, settings.AMOUNT_OF_POSTS + 2):
            cls.post = Post.objects.create(
                pk=i,
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
                image=cls.uploaded,
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_other_client = Client()
        self.authorized_other_client.force_login(self.user2)

    def test_pages_uses_correct_template(self):
        reverse_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', args={self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', args={self.post.pk}):
                'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in reverse_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def compare_post_context_for_default_values(self, post_obj):
        compare_post_dict = {
            post_obj.pk: self.post.pk,
            post_obj.text: self.post.text,
            post_obj.author: self.post.author,
            post_obj.group: self.post.group,
            post_obj.image: self.post.image,
        }
        for context_type, value in compare_post_dict.items():
            self.assertEqual(context_type, value)

    def test_list_pages_show_correct_context(self):
        list_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for list_page in list_pages:
            response = self.authorized_client.get(list_page)
            first_object = response.context['page_obj'][0]
            self.compare_post_context_for_default_values(first_object)

    def test_page_detail_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        args={self.post.pk})))
        self.compare_post_context_for_default_values(response.context['post'])

    def post_pages_show_correct_form_content(self, response):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_content(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.post_pages_show_correct_form_content(response)

    def test_post_edit_show_correct_content(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={self.post.pk}))
        self.post_pages_show_correct_form_content(response)

    def page_contains_amount_of_records(self, page_number, amount_of_record):
        reverse_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        }
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name
                                                      + f'?page={page_number}')
                self.assertEqual(len(response.context['page_obj']),
                                 amount_of_record)

    def test_fist_page_contains_full_stack_of_records(self):
        self.page_contains_amount_of_records(1, settings.AMOUNT_OF_POSTS)

    def test_second_page_contains_one_records(self):
        self.page_contains_amount_of_records(2, Post.objects.count()
                                             - settings.AMOUNT_OF_POSTS)

    def test_post_not_in_other_group(self):
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': self.group2.slug})))
        self.assertNotContains(response, 'post')

    def test_cache_index_page(self):
        post_data = {'text': 'cache test', 'author': self.user}
        post = Post.objects.create(text=post_data['text'],
                                   author=post_data['author'])
        response = self.client.get(reverse('posts:index'))
        cached_response_content = response.content
        post.delete()
        self.assertEqual(cached_response_content, response.content)
        self.assertIn(post_data['text'].encode(), response.content)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(cached_response_content, response.content)
        self.assertNotIn(post_data['text'].encode(), response.content)

    def test_follow_create_and_delete(self):
        follow_count = Follow.objects.count()
        response = self.authorized_other_client.post(
            reverse('posts:profile_follow', args={self.user}),
            follow=True,
        )
        self.assertRedirects(response,
                             reverse('posts:profile', args={self.user}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user2,
                author=self.user,
            ).exists()
        )
        response = self.authorized_other_client.post(
            reverse('posts:profile_unfollow', args={self.user}),
            follow=True,
        )
        self.assertRedirects(response,
                             reverse('posts:profile', args={self.user}))
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user2,
                author=self.user,
            ).exists()
        )

    def test_follow_show_correct_content(self):
        Follow.objects.create(
            user=self.user2,
            author=self.user,
        )
        response = self.authorized_other_client.get(
            reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.compare_post_context_for_default_values(first_object)

    def test_follow_not_show_for_other_users(self):
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertNotContains(response, 'post')
