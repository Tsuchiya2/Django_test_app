from django.urls import path
from .views import ArticleListView, ArticleCreateView, ArticleDetailView

app_name = 'articles'

urlpatterns = [
    path('', ArticleListView.as_view(), name='list'),
    path('create/', ArticleCreateView.as_view(), name='create'),
    path('<int:pk>/', ArticleDetailView.as_view(), name='detail'),
]
