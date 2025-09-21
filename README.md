# Jazz Guitarist Paper - 記事CRUD機能実装ガイド

このプロジェクトは、プログラミング初学者向けの学習アプリとして、Django を使った記事（Article）のCRUD機能を段階的に実装していきます。

## プロジェクト概要

- **フレームワーク**: Django 5.2.6
- **データベース**: SQLite3
- **認証**: カスタムユーザーモデル（メール認証）
- **アプリ構成**:
  - `accounts`: ユーザー認証機能
  - `tribute`: 記事管理機能

## 実装する機能

### 記事（Article）モデルの仕様
- **author**: 投稿者（Userモデルへの外部キー）
- **title**: 記事タイトル
- **content**: 記事内容
- **created_at**: 作成日時
- **updated_at**: 更新日時

### ページ仕様
1. **記事一覧ページ**: タイトルと作成日時を表示、タイトルクリックで詳細ページへ
2. **記事詳細ページ**: 全ての記事情報を表示、投稿者のみ編集・削除可能
3. **記事投稿ページ**: 新規記事作成フォーム
4. **記事編集ページ**: 既存記事編集フォーム（投稿者のみアクセス可能）

### セキュリティ仕様
- 編集ページへの直接URLアクセス時、投稿者以外は詳細ページへリダイレクト
- 削除機能も投稿者のみ実行可能

## 段階的実装手順

### Chapter 1: 記事モデルのマイグレーション

#### 1.1 学習目標
- Djangoモデルの設計方法
- 外部キー（ForeignKey）の理解
- マイグレーションの概念と実行方法

#### 1.2 実装手順

**Step 1**: `tribute/models.py` に Article モデルを作成

```python
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='投稿者')
    title = models.CharField(max_length=200, verbose_name='タイトル')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '記事'
        verbose_name_plural = '記事'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'pk': self.pk})
```

**Step 2**: マイグレーションファイルの作成と実行

```bash
python manage.py makemigrations
python manage.py migrate
```

**Step 3**: Django Admin への登録（`tribute/admin.py`）

```python
from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
```

### Chapter 2: 記事一覧・投稿機能とバリデーション

#### 2.1 学習目標
- Django のClass-Based Views（ListView, CreateView）
- フォームバリデーション
- テンプレートの継承とfor文の使用

#### 2.2 実装手順

**Step 1**: `tribute/forms.py` の作成

```python
from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 3:
            raise forms.ValidationError('タイトルは3文字以上で入力してください。')
        return title

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 10:
            raise forms.ValidationError('内容は10文字以上で入力してください。')
        return content
```

**Step 2**: `tribute/views.py` の更新

```python
from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Article
from .forms import ArticleForm

def for_reinhardt(request):
    return render(request, "tribute/for_reinhardt.html")

class ArticleListView(ListView):
    model = Article
    template_name = 'tribute/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'tribute/article_form.html'
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, '記事を投稿しました。')
        return super().form_valid(form)
```

**Step 3**: `tribute/urls.py` の更新

```python
from django.urls import path
from . import views

urlpatterns = [
    path("for_reinhardt/", views.for_reinhardt, name="for_reinhardt"),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
]
```

**Step 4**: テンプレートファイルの作成

`templates/tribute/base.html`:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Jazz Guitarist Paper{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'article_list' %}">Jazz Guitarist Paper</a>
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <a class="nav-link" href="{% url 'article_create' %}">記事投稿</a>
                    <a class="nav-link" href="{% url 'accounts:logout' %}">ログアウト</a>
                {% else %}
                    <a class="nav-link" href="{% url 'accounts:login' %}">ログイン</a>
                    <a class="nav-link" href="{% url 'accounts:register' %}">会員登録</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}

        {% block content %}
        {% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

`templates/tribute/article_list.html`:

```html
{% extends 'tribute/base.html' %}

{% block title %}記事一覧 - Jazz Guitarist Paper{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>記事一覧</h1>
    {% if user.is_authenticated %}
        <a href="{% url 'article_create' %}" class="btn btn-primary">新規投稿</a>
    {% endif %}
</div>

{% if articles %}
    <div class="row">
        {% for article in articles %}
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="{% url 'article_detail' article.pk %}" class="text-decoration-none">
                                {{ article.title }}
                            </a>
                        </h5>
                        <p class="card-text text-muted">
                            投稿者: {{ article.author }} |
                            {{ article.created_at|date:"Y年m月d日 H:i" }}
                        </p>
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>

    {% if is_paginated %}
        <nav aria-label="Page navigation">
            <ul class="pagination justify-content-center">
                {% if page_obj.has_previous %}
                    <li class="page-item">
                        <a class="page-link" href="?page=1">最初</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.previous_page_number }}">前へ</a>
                    </li>
                {% endif %}

                <li class="page-item active">
                    <span class="page-link">{{ page_obj.number }}</span>
                </li>

                {% if page_obj.has_next %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.next_page_number }}">次へ</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}">最後</a>
                    </li>
                {% endif %}
            </ul>
        </nav>
    {% endif %}
{% else %}
    <div class="text-center">
        <p>まだ記事が投稿されていません。</p>
        {% if user.is_authenticated %}
            <a href="{% url 'article_create' %}" class="btn btn-primary">最初の記事を投稿する</a>
        {% endif %}
    </div>
{% endif %}
{% endblock %}
```

`templates/tribute/article_form.html`:

```html
{% extends 'tribute/base.html' %}

{% block title %}記事投稿 - Jazz Guitarist Paper{% endblock %}

{% block content %}
<h1>記事投稿</h1>

<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label for="{{ form.title.id_for_label }}" class="form-label">タイトル</label>
        {{ form.title }}
        {% if form.title.errors %}
            <div class="text-danger">
                {% for error in form.title.errors %}
                    <small>{{ error }}</small>
                {% endfor %}
            </div>
        {% endif %}
    </div>

    <div class="mb-3">
        <label for="{{ form.content.id_for_label }}" class="form-label">内容</label>
        {{ form.content }}
        {% if form.content.errors %}
            <div class="text-danger">
                {% for error in form.content.errors %}
                    <small>{{ error }}</small>
                {% endfor %}
            </div>
        {% endif %}
    </div>

    <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary">投稿する</button>
        <a href="{% url 'article_list' %}" class="btn btn-secondary">キャンセル</a>
    </div>
</form>
{% endblock %}
```

### Chapter 3: 記事詳細機能

#### 3.1 学習目標
- DetailView の使用方法
- URL パラメータの取得
- 条件分岐（投稿者判定）

#### 3.2 実装手順

**Step 1**: `tribute/views.py` に DetailView を追加

```python
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'tribute/article_detail.html'
    context_object_name = 'article'
```

**Step 2**: `tribute/urls.py` を更新

```python
urlpatterns = [
    path("for_reinhardt/", views.for_reinhardt, name="for_reinhardt"),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
]
```

**Step 3**: `templates/tribute/article_detail.html` の作成

```html
{% extends 'tribute/base.html' %}

{% block title %}{{ article.title }} - Jazz Guitarist Paper{% endblock %}

{% block content %}
<div class="row">
    <div class="col-lg-8">
        <article>
            <header class="mb-4">
                <h1>{{ article.title }}</h1>
                <div class="text-muted mb-3">
                    <i class="fas fa-user"></i> {{ article.author }} |
                    <i class="fas fa-calendar"></i> {{ article.created_at|date:"Y年m月d日 H:i" }}
                    {% if article.updated_at != article.created_at %}
                        | <i class="fas fa-edit"></i> 更新: {{ article.updated_at|date:"Y年m月d日 H:i" }}
                    {% endif %}
                </div>
            </header>

            <div class="content">
                {{ article.content|linebreaks }}
            </div>
        </article>

        {% if user == article.author %}
            <div class="mt-4 d-flex gap-2">
                <a href="{% url 'article_update' article.pk %}" class="btn btn-warning">編集</a>
                <a href="{% url 'article_delete' article.pk %}" class="btn btn-danger">削除</a>
            </div>
        {% endif %}
    </div>

    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h5>記事情報</h5>
            </div>
            <div class="card-body">
                <p><strong>投稿者:</strong> {{ article.author }}</p>
                <p><strong>作成日:</strong> {{ article.created_at|date:"Y年m月d日 H:i" }}</p>
                <p><strong>更新日:</strong> {{ article.updated_at|date:"Y年m月d日 H:i" }}</p>
            </div>
        </div>
    </div>
</div>

<div class="mt-4">
    <a href="{% url 'article_list' %}" class="btn btn-secondary">記事一覧に戻る</a>
</div>
{% endblock %}
```

### Chapter 4: 記事編集と更新機能

#### 4.1 学習目標
- UpdateView の使用方法
- ユーザー権限チェック（UserPassesTestMixin）
- リダイレクト処理

#### 4.2 実装手順

**Step 1**: `tribute/views.py` に UpdateView を追加

```python
class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'tribute/article_form.html'

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author

    def handle_no_permission(self):
        article = self.get_object()
        messages.warning(self.request, '他のユーザーの記事は編集できません。')
        return redirect('article_detail', pk=article.pk)

    def form_valid(self, form):
        messages.success(self.request, '記事を更新しました。')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('article_detail', kwargs={'pk': self.object.pk})
```

**Step 2**: `tribute/urls.py` を更新

```python
urlpatterns = [
    path("for_reinhardt/", views.for_reinhardt, name="for_reinhardt"),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<int:pk>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
]
```

**Step 3**: `templates/tribute/article_form.html` を編集用に対応

```html
{% extends 'tribute/base.html' %}

{% block title %}
    {% if object %}記事編集{% else %}記事投稿{% endif %} - Jazz Guitarist Paper
{% endblock %}

{% block content %}
<h1>{% if object %}記事編集{% else %}記事投稿{% endif %}</h1>

<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label for="{{ form.title.id_for_label }}" class="form-label">タイトル</label>
        {{ form.title }}
        {% if form.title.errors %}
            <div class="text-danger">
                {% for error in form.title.errors %}
                    <small>{{ error }}</small>
                {% endfor %}
            </div>
        {% endif %}
    </div>

    <div class="mb-3">
        <label for="{{ form.content.id_for_label }}" class="form-label">内容</label>
        {{ form.content }}
        {% if form.content.errors %}
            <div class="text-danger">
                {% for error in form.content.errors %}
                    <small>{{ error }}</small>
                {% endfor %}
            </div>
        {% endif %}
    </div>

    <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary">
            {% if object %}更新する{% else %}投稿する{% endif %}
        </button>
        <a href="{% if object %}{% url 'article_detail' object.pk %}{% else %}{% url 'article_list' %}{% endif %}"
           class="btn btn-secondary">キャンセル</a>
    </div>
</form>
{% endblock %}
```

### Chapter 5: デバッグと記事削除機能

#### 5.1 学習目標
- DeleteView の使用方法
- 削除確認ページの実装
- Django のデバッグ技法

#### 5.2 実装手順

**Step 1**: `tribute/views.py` に DeleteView を追加

```python
from django.shortcuts import redirect

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'tribute/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author

    def handle_no_permission(self):
        article = self.get_object()
        messages.warning(self.request, '他のユーザーの記事は削除できません。')
        return redirect('article_detail', pk=article.pk)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '記事を削除しました。')
        return super().delete(request, *args, **kwargs)
```

**Step 2**: `tribute/urls.py` を更新

```python
urlpatterns = [
    path("for_reinhardt/", views.for_reinhardt, name="for_reinhardt"),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<int:pk>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
]
```

**Step 3**: `templates/tribute/article_confirm_delete.html` の作成

```html
{% extends 'tribute/base.html' %}

{% block title %}記事削除確認 - Jazz Guitarist Paper{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header bg-danger text-white">
                <h4 class="mb-0">記事削除確認</h4>
            </div>
            <div class="card-body">
                <p class="text-danger">
                    <strong>注意:</strong> 以下の記事を本当に削除しますか？<br>
                    この操作は取り消すことができません。
                </p>

                <div class="border p-3 mb-4 bg-light">
                    <h5>{{ article.title }}</h5>
                    <p class="text-muted">
                        投稿者: {{ article.author }} |
                        作成日: {{ article.created_at|date:"Y年m月d日 H:i" }}
                    </p>
                    <p>{{ article.content|truncatewords:30 }}</p>
                </div>

                <form method="post">
                    {% csrf_token %}
                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-danger">削除する</button>
                        <a href="{% url 'article_detail' article.pk %}" class="btn btn-secondary">キャンセル</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## MCP Codex を使った実装

各チャプターの実装は、MCP Codex を使用して以下のように進めます：

### 使用方法

```bash
# MCP Codex セッションの開始
mcp codex --prompt "Chapter 1の記事モデルを実装してください"

# 続きの実装
mcp codex-reply --conversation-id [ID] --prompt "Chapter 2のビューとテンプレートを実装してください"
```

### 各チャプターでのCodex プロンプト例

**Chapter 1**:
```
tribute/models.py に Article モデルを実装し、マイグレーションを実行してください。
- author（User外部キー）
- title（文字列、最大200文字）
- content（テキスト）
- created_at（自動作成日時）
- updated_at（自動更新日時）
```

**Chapter 2**:
```
記事一覧と投稿機能を実装してください。
- ArticleListView と ArticleCreateView
- フォームバリデーション（タイトル3文字以上、内容10文字以上）
- Bootstrap を使った一覧・投稿テンプレート
```

**Chapter 3-5**:
同様に各機能ごとにプロンプトを細分化して実装

## テスト方法

各チャプター完了後に以下を確認：

1. **機能テスト**
   - 各ページの表示確認
   - フォーム送信の動作確認
   - 権限制御の動作確認

2. **Django管理画面での確認**
   ```bash
   python manage.py createsuperuser
   python manage.py runserver
   # http://127.0.0.1:8000/admin/ でデータ確認
   ```

3. **コードレビュー項目**
   - セキュリティ（権限チェック）
   - バリデーション
   - テンプレートの適切な継承
   - URL設計の一貫性

## 学習のポイント

各チャプターで重要な概念：
- **Chapter 1**: モデル設計、データベース設計
- **Chapter 2**: CBV（Class-Based Views）、フォーム処理
- **Chapter 3**: 詳細表示、テンプレートでの条件分岐
- **Chapter 4**: 権限制御、カスタムバリデーション
- **Chapter 5**: 削除処理、ユーザビリティ

## 次のステップ

基本CRUD実装後の拡張機能案：
- コメント機能
- 検索機能
- タグ機能
- 記事のお気に入り機能
- API化（Django REST Framework）

---

このガイドに従って、段階的に実装を進めることで、Django のCRUD操作とWebアプリケーション開発の基本を習得できます。