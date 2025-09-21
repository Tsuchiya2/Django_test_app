from django.urls import path
from .views import ArticleListView, ArticleCreateView, ArticleDetailView, ArticleUpdateView, ArticleDeleteView

app_name = 'articles'

urlpatterns = [
    path('', ArticleListView.as_view(), name='list'),
    path('create/', ArticleCreateView.as_view(), name='create'),
    path('<int:pk>/', ArticleDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ArticleUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', ArticleDeleteView.as_view(), name='delete'),
]
