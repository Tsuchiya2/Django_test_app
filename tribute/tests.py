from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TemplateLinksTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_and_register_links_for_anonymous_user(self):
        """未認証ユーザーにログイン・新規登録リンクが表示される"""
        response = self.client.get(reverse('for_reinhardt'))

        # ステータスコード確認
        self.assertEqual(response.status_code, 200)

        # ログインリンクの存在確認
        self.assertContains(response, 'href="/accounts/login/"')
        self.assertContains(response, 'ログイン')

        # 新規登録リンクの存在確認
        self.assertContains(response, 'href="/accounts/register/"')
        self.assertContains(response, '新規登録')

    def test_logout_link_for_authenticated_user(self):
        """認証済みユーザーにログアウトリンクが表示される"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('for_reinhardt'))

        # ログアウトフォームの存在確認
        self.assertContains(response, 'action="/accounts/logout/"')
        self.assertContains(response, 'ログアウト')

        # ユーザー名表示確認
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'こんにちは')

    def test_template_structure_anonymous(self):
        """未認証時のテンプレート構造確認"""
        response = self.client.get(reverse('for_reinhardt'))

        # 認証情報が表示されていない
        self.assertNotContains(response, 'こんにちは')
        self.assertNotContains(response, 'ログアウト')

        # 認証リンクが表示されている
        self.assertContains(response, 'ログイン')
        self.assertContains(response, '新規登録')

    def test_csrf_token_in_logout_form(self):
        """ログアウトフォームにCSRFトークンが含まれている"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('for_reinhardt'))

        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, '<input type="hidden"')

    def test_links_functionality(self):
        """リンクが実際に動作するか確認"""
        # ログインページへのアクセス
        login_url = reverse('accounts:login')
        login_response = self.client.get(login_url)
        self.assertEqual(login_response.status_code, 200)

        # 新規登録ページへのアクセス
        register_url = reverse('accounts:register')
        register_response = self.client.get(register_url)
        self.assertEqual(register_response.status_code, 200)

    def test_header_jazz_guitarist_paper_link(self):
        """ヘッダーの「Jazz Guitarist Paper」リンクが存在し、正しいURLを指している"""
        response = self.client.get(reverse('for_reinhardt'))

        # ステータスコード確認
        self.assertEqual(response.status_code, 200)

        # ヘッダーにJazz Guitarist Paperのリンクが存在することを確認
        self.assertContains(response, 'Jazz Guitarist Paper')
        self.assertContains(response, 'href="/for_reinhardt/"')

        # リンクがaタグ内に正しく配置されていることを確認
        self.assertContains(response, '<a href="/for_reinhardt/"')

    def test_header_link_navigation(self):
        """ヘッダーリンクから実際にページ遷移できることを確認"""
        # 別のページ（例：ログインページ）からヘッダーリンクを確認
        login_response = self.client.get(reverse('accounts:login'))
        self.assertEqual(login_response.status_code, 200)

        # ログインページにもヘッダーのリンクが表示されることを確認
        self.assertContains(login_response, 'Jazz Guitarist Paper')
        self.assertContains(login_response, 'href="/for_reinhardt/"')

        # for_reinhardtページへの直接アクセスが可能であることを確認
        target_response = self.client.get('/for_reinhardt/')
        self.assertEqual(target_response.status_code, 200)

    def test_header_link_in_all_pages(self):
        """すべてのページでヘッダーリンクが統一して表示される"""
        pages_to_test = [
            reverse('for_reinhardt'),
            reverse('accounts:login'),
            reverse('accounts:register'),
        ]

        for page_url in pages_to_test:
            with self.subTest(page=page_url):
                response = self.client.get(page_url)
                self.assertEqual(response.status_code, 200)

                # 各ページでヘッダーリンクが存在することを確認
                self.assertContains(response, 'Jazz Guitarist Paper')
                self.assertContains(response, 'href="/for_reinhardt/"')

                # ヘッダーの構造が正しいことを確認
                self.assertContains(response, '<header class="bg-black">')
                self.assertContains(response, '<h1 class="text-xl font-bold text-white">')
