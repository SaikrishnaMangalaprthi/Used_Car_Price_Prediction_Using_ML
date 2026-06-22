from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile, PredictionHistory


# ── Models ────────────────────────────────────────────────
class UserProfileModelTest(TestCase):
    def test_create_user_profile(self):
        user = UserProfile.objects.create(
            name='Sai Krishna', email='sai@example.com',
            password='test123', is_active=True
        )
        self.assertEqual(user.name, 'Sai Krishna')
        self.assertTrue(user.is_active)

    def test_is_active_defaults_to_false(self):
        user = UserProfile.objects.create(
            name='Inactive User', email='inactive@example.com', password='test123'
        )
        self.assertFalse(user.is_active)


class PredictionHistoryModelTest(TestCase):
    def test_create_prediction_history(self):
        user = UserProfile.objects.create(
            name='Sai', email='sai2@example.com', password='pwd', is_active=True
        )
        record = PredictionHistory.objects.create(
            user=user, brand='Maruti', car_model='Swift', vehicle_age=5,
            km_driven=45000, fuel_type='Petrol', transmission_type='Manual',
            predicted_price=350000,
        )
        self.assertEqual(record.user, user)
        self.assertIn('Rs.', str(record))


# ── Login / Logout ────────────────────────────────────────
class LoginTest(TestCase):
    def setUp(self):
        self.active_user = UserProfile.objects.create(
            name='Sai', email='active@example.com', password='pass123', is_active=True
        )
        self.inactive_user = UserProfile.objects.create(
            name='New', email='inactive@example.com', password='pass123', is_active=False
        )

    def test_login_success_redirects_to_home(self):
        response = self.client.post(reverse('UserLoginCheck'), {
            'email': 'active@example.com', 'password': 'pass123',
        })
        self.assertRedirects(response, reverse('UserHome'))

    def test_login_wrong_password_shows_error(self):
        response = self.client.post(reverse('UserLoginCheck'), {
            'email': 'active@example.com', 'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password')

    def test_inactive_user_cannot_login(self):
        response = self.client.post(reverse('UserLoginCheck'), {
            'email': 'inactive@example.com', 'password': 'pass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('user_id', self.client.session)


class LogoutTest(TestCase):
    def test_logout_clears_session_and_redirects(self):
        session = self.client.session
        session['user_id'] = 1
        session.save()
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('index'))
        self.assertNotIn('user_id', self.client.session)


# ── Access control (redirect if not logged in) ───────────
class AccessControlTest(TestCase):
    def test_userhome_redirects_if_not_logged_in(self):
        self.assertRedirects(self.client.get(reverse('UserHome')), reverse('UserLogin'))

    def test_prediction_redirects_if_not_logged_in(self):
        self.assertRedirects(self.client.get(reverse('prediction')), reverse('UserLogin'))

    def test_history_redirects_if_not_logged_in(self):
        self.assertRedirects(self.client.get(reverse('prediction_history')), reverse('UserLogin'))

    def test_compare_redirects_if_not_logged_in(self):
        self.assertRedirects(self.client.get(reverse('compare_cars')), reverse('UserLogin'))


# ── Prediction form validation ───────────────────────────
class PredictionFormValidationTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            name='Sai', email='sai3@example.com', password='pwd', is_active=True
        )
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

    def test_invalid_year_shows_error(self):
        response = self.client.post(reverse('prediction'), {
            'year': '1800', 'km_driven': '45000', 'fuel': 'Petrol',
            'transmission': 'Manual', 'brand': 'Maruti', 'car_model': 'Swift',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('Year must be' in e for e in response.context['errors']))

    def test_invalid_km_shows_error(self):
        response = self.client.post(reverse('prediction'), {
            'year': '2019', 'km_driven': 'abc', 'fuel': 'Petrol',
            'transmission': 'Manual', 'brand': 'Maruti', 'car_model': 'Swift',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('KM driven must be' in e for e in response.context['errors']))


# ── Prediction success path (mocked, so it doesn't need ──
# ── a real trained .pkl on disk)                          ──
class PredictionSuccessTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            name='Sai', email='sai4@example.com', password='pwd', is_active=True
        )
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

    @patch('pathlib.Path.exists', return_value=True)
    @patch('ml_pipeline.predict.get_price_tag')
    @patch('ml_pipeline.predict.get_similar_cars')
    @patch('ml_pipeline.predict.predict_price')
    def test_valid_submission_creates_history(self, mock_predict, mock_similar, mock_tag, mock_exists):
        mock_predict.return_value = {'predicted': 350000, 'lower': 320000, 'upper': 380000}
        mock_similar.return_value = []
        mock_tag.return_value = 'Fair Price'

        response = self.client.post(reverse('prediction'), {
            'year': '2019', 'km_driven': '45000', 'fuel': 'Petrol',
            'transmission': 'Manual', 'brand': 'Maruti', 'car_model': 'Swift',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PredictionHistory.objects.count(), 1)
        self.assertEqual(PredictionHistory.objects.first().predicted_price, 350000)


# ── History: data isolation between users (security test) ─
class PredictionHistoryViewTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            name='Sai', email='sai5@example.com', password='pwd', is_active=True
        )

    def test_shows_only_own_predictions(self):
        other = UserProfile.objects.create(
            name='Other', email='other@example.com', password='pwd', is_active=True
        )
        PredictionHistory.objects.create(
            user=self.user, brand='Maruti', car_model='Swift', vehicle_age=3,
            km_driven=30000, fuel_type='Petrol', transmission_type='Manual', predicted_price=300000,
        )
        PredictionHistory.objects.create(
            user=other, brand='Hyundai', car_model='i20', vehicle_age=2,
            km_driven=20000, fuel_type='Diesel', transmission_type='Manual', predicted_price=500000,
        )
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

        response = self.client.get(reverse('prediction_history'))
        self.assertEqual(len(response.context['history']), 1)


class DeletePredictionTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            name='Sai', email='sai6@example.com', password='pwd', is_active=True
        )
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()
        self.record = PredictionHistory.objects.create(
            user=self.user, brand='Maruti', car_model='Swift', vehicle_age=3,
            km_driven=30000, fuel_type='Petrol', transmission_type='Manual', predicted_price=300000,
        )

    def test_deletes_own_prediction(self):
        self.client.get(reverse('delete_prediction', args=[self.record.id]))
        self.assertFalse(PredictionHistory.objects.filter(id=self.record.id).exists())

    def test_cannot_delete_other_users_prediction(self):
        other = UserProfile.objects.create(
            name='Other', email='other2@example.com', password='pwd', is_active=True
        )
        other_record = PredictionHistory.objects.create(
            user=other, brand='Hyundai', car_model='i20', vehicle_age=2,
            km_driven=20000, fuel_type='Diesel', transmission_type='Manual', predicted_price=500000,
        )
        self.client.get(reverse('delete_prediction', args=[other_record.id]))
        self.assertTrue(PredictionHistory.objects.filter(id=other_record.id).exists())