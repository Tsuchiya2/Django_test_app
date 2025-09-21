from django.test import TestCase, TransactionTestCase
from django.db import connection
from django.contrib.auth import get_user_model
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import ProjectState
from django.core.management import call_command
from django.apps import apps
from .models import Article
import io
import sys

User = get_user_model()


class ArticleMigrationTest(TransactionTestCase):
    """Articleモデルのマイグレーションが期待通りに適用されているかをテストする"""

    def setUp(self):
        self.executor = MigrationExecutor(connection)
        self.app_name = 'articles'
        self.migration_name = '0001_initial'

    def test_migration_creates_article_table(self):
        """マイグレーション適用後にArticleテーブルが正しく作成される"""
        # テーブルが存在することを確認
        table_names = connection.introspection.table_names()
        self.assertIn('articles_article', table_names)

    def test_article_model_fields(self):
        """Articleモデルのフィールドが期待通りに作成されている"""
        # モデルのフィールドを取得
        article_model = apps.get_model('articles', 'Article')
        fields = {field.name: field for field in article_model._meta.get_fields()}

        # 必要なフィールドが存在することを確認
        required_fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'author']
        for field_name in required_fields:
            self.assertIn(field_name, fields, f"フィールド '{field_name}' が見つかりません")

        # フィールドの属性を確認
        self.assertEqual(fields['title'].max_length, 200)
        self.assertEqual(fields['title'].verbose_name, 'タイトル')
        self.assertEqual(fields['content'].verbose_name, '内容')
        self.assertEqual(fields['created_at'].verbose_name, '作成日時')
        self.assertEqual(fields['updated_at'].verbose_name, '更新日時')
        self.assertEqual(fields['author'].verbose_name, '投稿者')

        # auto_now_add と auto_now の確認
        self.assertTrue(fields['created_at'].auto_now_add)
        self.assertTrue(fields['updated_at'].auto_now)

    def test_article_model_meta_options(self):
        """Articleモデルのメタ情報が正しく設定されている"""
        article_model = apps.get_model('articles', 'Article')
        meta = article_model._meta

        # orderingの確認
        self.assertEqual(meta.ordering, ['-created_at'])

        # verbose_nameの確認
        self.assertEqual(meta.verbose_name, '記事')
        self.assertEqual(meta.verbose_name_plural, '記事')

    def test_foreign_key_constraint(self):
        """ForeignKeyの制約が正しく設定されている"""
        article_model = apps.get_model('articles', 'Article')
        author_field = article_model._meta.get_field('author')

        # ForeignKeyであることを確認
        self.assertTrue(author_field.many_to_one)

        # CASCADE削除が設定されていることを確認
        from django.db.models import CASCADE
        self.assertEqual(author_field.remote_field.on_delete, CASCADE)

        # 関連先がUserモデルであることを確認
        self.assertEqual(author_field.related_model, User)

    def test_database_table_structure(self):
        """データベーステーブルの構造が期待通りである"""
        # テーブル構造を取得
        table_description = connection.introspection.get_table_description(connection.cursor(), 'articles_article')

        # カラム名を取得
        column_names = [col.name for col in table_description]

        # 期待するカラムが存在することを確認
        expected_columns = ['id', 'title', 'content', 'created_at', 'updated_at', 'author_id']
        for column in expected_columns:
            self.assertIn(column, column_names, f"カラム '{column}' が見つかりません")

    def test_model_creation_with_migration(self):
        """マイグレーション適用後にモデルインスタンスが正常に作成できる"""
        # Userを作成
        user = User.objects.create_user(username='testuser', email='test@example.com')

        # Articleを作成
        article_model = apps.get_model('articles', 'Article')
        article = article_model.objects.create(
            title='テスト記事',
            content='これはテスト記事の内容です。',
            author=user
        )

        # 正常に作成されたことを確認
        self.assertEqual(article.title, 'テスト記事')
        self.assertEqual(article.content, 'これはテスト記事の内容です。')
        self.assertEqual(article.author, user)
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)


class ArticleModelTest(TestCase):
    """Articleモデルの基本機能テスト"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')

    def test_article_creation(self):
        """記事の作成テスト"""
        article = Article.objects.create(
            title='テスト記事',
            content='これはテスト記事です。',
            author=self.user
        )

        self.assertEqual(str(article), 'テスト記事')
        self.assertEqual(article.author, self.user)
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)

    def test_article_ordering(self):
        """記事の並び順テスト"""
        article1 = Article.objects.create(
            title='記事1',
            content='内容1',
            author=self.user
        )

        article2 = Article.objects.create(
            title='記事2',
            content='内容2',
            author=self.user
        )

        # 新しい記事が先に来ることを確認
        articles = Article.objects.all()
        self.assertEqual(articles[0], article2)
        self.assertEqual(articles[1], article1)
