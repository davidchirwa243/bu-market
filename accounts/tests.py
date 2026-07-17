from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRoleTestCase(TestCase):
    def test_user_creation_with_roles(self):
        # Create Buyer
        buyer = User.objects.create_user(username='buyer1', email='buyer@test.com', password='pass', role=User.Role.BUYER)
        self.assertTrue(buyer.is_buyer)
        self.assertFalse(buyer.is_seller)
        self.assertFalse(buyer.is_accountant)
        self.assertFalse(buyer.is_moderator)
        self.assertFalse(buyer.is_admin_role)

        # Create Seller
        seller = User.objects.create_user(username='seller1', email='seller@test.com', password='pass', role=User.Role.SELLER)
        self.assertFalse(seller.is_buyer)
        self.assertTrue(seller.is_seller)
        self.assertFalse(seller.is_accountant)
        self.assertFalse(seller.is_moderator)
        self.assertFalse(seller.is_admin_role)

        # Create Accountant
        accountant = User.objects.create_user(username='acc1', email='acc@test.com', password='pass', role=User.Role.ACCOUNTANT)
        self.assertFalse(accountant.is_buyer)
        self.assertFalse(accountant.is_seller)
        self.assertTrue(accountant.is_accountant)
        self.assertFalse(accountant.is_moderator)
        self.assertFalse(accountant.is_admin_role)

        # Create Moderator
        moderator = User.objects.create_user(username='mod1', email='mod@test.com', password='pass', role=User.Role.MODERATOR)
        self.assertFalse(moderator.is_buyer)
        self.assertFalse(moderator.is_seller)
        self.assertFalse(moderator.is_accountant)
        self.assertTrue(moderator.is_moderator)
        self.assertFalse(moderator.is_admin_role)

        # Create Admin
        admin = User.objects.create_user(username='admin_role', email='admin_role@test.com', password='pass', role=User.Role.ADMIN)
        self.assertFalse(admin.is_buyer)
        self.assertFalse(admin.is_seller)
        self.assertFalse(admin.is_accountant)
        self.assertFalse(admin.is_moderator)
        self.assertTrue(admin.is_admin_role)


from django.urls import reverse
from accounts.forms import CustomUserCreationForm

class UserRegistrationTestCase(TestCase):
    def test_custom_user_creation_form_validation(self):
        # 1. Valid BUYER role
        form_data = {
            'username': 'buyer_test_user',
            'email': 'buyer_test@example.com',
            'first_name': 'Buyer',
            'last_name': 'Test',
            'role': User.Role.BUYER,
            'password1': 'pass12345',
            'password2': 'pass12345',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.role, User.Role.BUYER)
        self.assertTrue(user.is_buyer)

        # 2. Valid SELLER role
        form_data['username'] = 'seller_test_user'
        form_data['role'] = User.Role.SELLER
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.role, User.Role.SELLER)
        self.assertTrue(user.is_seller)

        # 3. Missing role
        form_data['username'] = 'missing_role_user'
        form_data.pop('role')
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)

        # 4. Invalid role (e.g. ADMIN role should not be allowed for registration selection)
        form_data['username'] = 'admin_try_user'
        form_data['role'] = User.Role.ADMIN
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)

    def test_registration_view_get(self):
        url = reverse('accounts:register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_registration_view_post_success(self):
        url = reverse('accounts:register')
        post_data = {
            'username': 'new_registered_user',
            'email': 'new_reg@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': User.Role.SELLER,
            'password1': 'mypassword123',
            'password2': 'mypassword123',
        }
        response = self.client.post(url, data=post_data)
        # Should redirect to dashboard:home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:home'))

        # Verify user is created in db
        user = User.objects.get(username='new_registered_user')
        self.assertEqual(user.role, User.Role.SELLER)

        # Verify user is logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)


