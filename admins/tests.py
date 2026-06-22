from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from users.models import UserProfile, PredictionHistory


# ── Public pages ──────────────────────────────────────────
class PublicPagesTest(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_admin_login_page_loads(self):
        response = self.client.get(reverse('AdminLogin'))
        self.assertEqual(response.status_code, 200)

    def test_user_login_page_loads(self):
        response = self.client.get(reverse('UserLogin'))
        self.assertEqual(response.status_code, 200)

    def test_user_login_redirects_if_already_logged_in(self):
        session = self.client.session
        session['user_id'] = 1
        session.save()
        self.assertRedirects(self.client.get(reverse('UserLogin')), reverse('UserHome'))

    def test_user_register_page_loads(self):
        response = self.client.get(reverse('UserRegister'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)


# ── Admin login ───────────────────────────────────────────
class AdminLoginCheckTest(TestCase):
    def test_correct_credentials_logs_in(self):
        response = self.client.post(reverse('AdminLoginCheck'), {
            'username': settings.ADMIN_USERNAME,
            'password': settings.ADMIN_PASSWORD,
        })
        self.assertRedirects(response, reverse('AdminHome'))
        self.assertTrue(self.client.session.get('admin'))

    def test_wrong_password_shows_error(self):
        response = self.client.post(reverse('AdminLoginCheck'), {
            'username': settings.ADMIN_USERNAME,
            'password': 'definitely_wrong_password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials')
        self.assertNotIn('admin', self.client.session)

    def test_wrong_username_shows_error(self):
        response = self.client.post(reverse('AdminLoginCheck'), {
            'username': 'not_the_admin',
            'password': settings.ADMIN_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials')


# ── Admin access control ─────────────────────────────────
class AdminAccessControlTest(TestCase):
    def test_adminhome_redirects_if_not_admin(self):
        self.assertRedirects(self.client.get(reverse('AdminHome')), reverse('AdminLogin'))

    def test_register_users_view_redirects_if_not_admin(self):
        self.assertRedirects(self.client.get(reverse('RegisterUsersView')), reverse('AdminLogin'))

    def test_activate_user_redirects_if_not_admin(self):
        self.assertRedirects(self.client.get(reverse('ActivaUsers')), reverse('AdminLogin'))


# ── AdminHome dashboard ───────────────────────────────────
class AdminHomeTest(TestCase):
    def setUp(self):
        session = self.client.session
        session['admin'] = True
        session.save()

    def test_loads_with_correct_counts(self):
        user1 = UserProfile.objects.create(
            name='Sai', email='sai@example.com', password='pwd', is_active=True
        )
        UserProfile.objects.create(
            name='Pending', email='pending@example.com', password='pwd', is_active=False
        )
        PredictionHistory.objects.create(
            user=user1, brand='Maruti', car_model='Swift', vehicle_age=3,
            km_driven=30000, fuel_type='Petrol', transmission_type='Manual', predicted_price=300000,
        )

        response = self.client.get(reverse('AdminHome'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_users'], 2)
        self.assertEqual(response.context['active_users'], 1)
        self.assertEqual(response.context['total_predictions'], 1)

    def test_loads_with_zero_data(self):
        response = self.client.get(reverse('AdminHome'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_users'], 0)
        self.assertEqual(response.context['avg_price'], 0)


# ── User management ───────────────────────────────────────
class RegisterUsersViewTest(TestCase):
    def setUp(self):
        session = self.client.session
        session['admin'] = True
        session.save()

    def test_lists_all_users(self):
        UserProfile.objects.create(name='A', email='a@example.com', password='pwd')
        UserProfile.objects.create(name='B', email='b@example.com', password='pwd')
        response = self.client.get(reverse('RegisterUsersView'))
        self.assertEqual(len(response.context['users']), 2)


class ActivaUsersTest(TestCase):
    def setUp(self):
        session = self.client.session
        session['admin'] = True
        session.save()
        self.user = UserProfile.objects.create(
            name='Pending', email='pending@example.com', password='pwd', is_active=False
        )

    def test_activates_user_and_redirects(self):
        response = self.client.get(reverse('ActivaUsers'), {'id': self.user.id})
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertRedirects(response, reverse('RegisterUsersView'))

    def test_invalid_user_id_does_not_crash(self):
        response = self.client.get(reverse('ActivaUsers'), {'id': 99999})
        self.assertRedirects(response, reverse('RegisterUsersView'))