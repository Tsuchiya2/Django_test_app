# Jazz Guitarist Paper - Accounts App 実装

Djangoプロジェクトにメールアドレスベースのユーザー認証システム（accounts app）を実装しました。

## 機能概要

- **ユーザー登録**: アカウント名、メールアドレス、パスワード、パスワード確認
- **ログイン**: メールアドレスとパスワードでログイン
- **ログアウト**: セッション終了

## 実装手順

### 1. プロジェクト構造の確認

```bash
# プロジェクト構造を確認
find . -name "*.py" | head -20
ls -la
```

既存のDjangoプロジェクト構成：
- メインプロジェクト: `jazz_guitarist_paper`
- 既存アプリ: `tribute`
- Django 5.2.6 使用
- SQLiteデータベース

### 2. Codex MCPを使用したaccountsアプリの実装

Codex MCPを活用して以下を一括実装：

```bash
# Codex MCPコマンド実行（概要）
# - accounts アプリケーション作成
# - カスタムUserモデル実装
# - 認証フォーム作成
# - ビューとURL設定
# - テンプレート作成
# - settings.py更新
```

### 3. データベースのリセットとマイグレーション

既存データベースを削除してカスタムユーザーモデルに対応：

```bash
# 既存データベースを削除
rm -f db.sqlite3

# 新しいカスタムユーザーモデルでマイグレーション実行
python manage.py migrate
```

### 4. 設定確認

```bash
# Django設定の検証
python manage.py check
```

## 実装詳細

### カスタムユーザーモデル (`accounts/models.py`)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        return self.email or self.username
```

### フォーム (`accounts/forms.py`)

1. **RegistrationForm**: ユーザー登録用フォーム
   - メールアドレス重複チェック機能付き
   - username, email, password1, password2 フィールド

2. **EmailAuthenticationForm**: メールアドレスログイン用フォーム
   - メールアドレスをユーザー名として使用

### ビュー (`accounts/views.py`)

- **RegisterView**: ユーザー登録処理とログイン
- **LoginView**: メールアドレスベースログイン
- **LogoutView**: ログアウト処理

### URL設定 (`accounts/urls.py`)

```python
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
```

### テンプレート

- `templates/accounts/register.html`: 日本語対応登録フォーム
- `templates/accounts/login.html`: 日本語対応ログインフォーム

### 設定更新 (`jazz_guitarist_paper/settings.py`)

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',  # 追加
    'tribute',
]

# テンプレートディレクトリ設定
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 追加
        # ...
    },
]

# カスタムユーザーモデル設定
AUTH_USER_MODEL = 'accounts.User'

# ログイン/ログアウト後のリダイレクト設定
LOGIN_REDIRECT_URL = 'for_reinhardt'
LOGOUT_REDIRECT_URL = 'accounts:login'
LOGIN_URL = 'accounts:login'
```

## 使用方法

### 開発サーバーの起動

```bash
python manage.py runserver
```

### アクセスURL

- ユーザー登録: `http://127.0.0.1:8000/accounts/register/`
- ログイン: `http://127.0.0.1:8000/accounts/login/`
- ログアウト: `http://127.0.0.1:8000/accounts/logout/`

### スーパーユーザーの作成

```bash
python manage.py createsuperuser
```

## 技術仕様

- **Django**: 5.2.6
- **データベース**: SQLite
- **認証方式**: メールアドレスベース
- **言語**: 日本語対応
- **テンプレートエンジン**: Django標準

## セキュリティ機能

- CSRFトークン保護
- パスワードバリデーション（Django標準）
- メールアドレス重複チェック
- セッションベース認証

## 今後の拡張可能性

- パスワードリセット機能
- メール確認機能
- ユーザープロフィール管理
- ソーシャルログイン連携