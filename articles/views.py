from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Article
from .forms import ArticleForm


class ArticleListView(ListView):
    model = Article
    template_name = 'articles/list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return super().get_queryset().select_related('author')


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/create.html'
    success_url = reverse_lazy('articles:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '記事を投稿する',
            'cancel_url': reverse_lazy('articles:list'),
            'cancel_text': 'キャンセル',
            'submit_text': '投稿する',
            'submit_icon_path': 'M12 6v6m0 0v6m0-6h6m-6 0H6'
        })
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'articles/detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return super().get_queryset().select_related('author')


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/edit.html'
    context_object_name = 'article'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs
        return qs.filter(author=self.request.user)

    def handle_no_permission(self):
        return redirect('/for_reinhardt')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '記事を編集する',
            'cancel_url': reverse_lazy('articles:detail', kwargs={'pk': self.object.pk}),
            'cancel_text': 'キャンセル',
            'submit_text': '更新する',
            'submit_icon_path': 'M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12'
        })
        return context

    def get_success_url(self):
        return reverse_lazy('articles:detail', kwargs={'pk': self.object.pk})
