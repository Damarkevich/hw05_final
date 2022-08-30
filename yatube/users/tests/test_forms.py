from django.test import TestCase
from django.urls import reverse

from ..models import User


class UserCreateFormTest(TestCase):
    def test_signup(self):
        users_count = User.objects.count()
        form_data = {
            'username': 'jsmith',
            'password1': 'G4dbtem45%',
            'password2': 'G4dbtem45%'
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='jsmith',
            ).exists()
        )
