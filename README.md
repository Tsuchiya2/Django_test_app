
⏺ 初学者向けに分かりやすく説明しますね！

  1. N+1クエリ問題とは？

  問題のある例：
  # ArticleListViewで10個の記事を取得する場合
  # 変更前（問題あり）
  class ArticleListView(ListView):
      model = Article  # get_querysetなし

  実際に実行されるSQL：
  -- 1回目：記事一覧を取得
  SELECT * FROM articles_article; -- 10件の記事

  -- テンプレートで {{ article.author.username }} を表示する際
  -- 記事ごとに追加でクエリが発生（10回）
  SELECT * FROM auth_user WHERE id = 1;  -- 記事1の投稿者
  SELECT * FROM auth_user WHERE id = 2;  -- 記事2の投稿者
  SELECT * FROM auth_user WHERE id = 3;  -- 記事3の投稿者
  ...（計10回）

  合計：1 + 10 = 11回のクエリ（N+1問題）

  2. select_related()で解決

  修正後：
  class ArticleListView(ListView):
      def get_queryset(self):
          return super().get_queryset().select_related('author')

  実際に実行されるSQL：
  -- 1回だけ！JOIN で記事と投稿者を同時取得
  SELECT articles_article.*, auth_user.*
  FROM articles_article
  INNER JOIN auth_user ON (articles_article.author_id = auth_user.id);

  結果：11回 → 1回に削減！

  3. 各Viewでの違い

  ArticleListView & ArticleDetailView

  - 目的: パフォーマンス改善（N+1問題解決）
  - 手法: select_related('author')でJOIN
  - 理由: テンプレートで{{ article.author.username }}を表示するため

  ArticleUpdateView

  - 目的: セキュリティ（権限制御）
  - 手法: filter(author=self.request.user)で絞り込み
  - 理由: 他人の記事を編集させないため

  def get_queryset(self):
      # 投稿者本人の記事のみ取得
      return super().get_queryset().filter(author=self.request.user)

  実行されるSQL：
  SELECT * FROM articles_article
  WHERE author_id = <ログイン中のユーザーID>;

  4. handle_no_permission()の役割

  def handle_no_permission(self):
      return redirect('/')  # ホームページにリダイレクト

  シナリオ：
  - ユーザーAが他人（ユーザーB）の記事編集URL /articles/5/edit/ にアクセス
  - get_queryset()でフィルタリング → 該当なし（404的な状態）
  - handle_no_permission()が呼ばれ → / にリダイレクト

  なぜ必要？
  - デフォルトではログインページにリダイレクトされるが、今回は「権限なし」なのでホームページが適切

  まとめ

  - ListViewとDetailView: N+1問題解決のためselect_related
  - UpdateView: セキュリティのためfilter + リダイレクト設定
  - 共通: より効率的で安全なアプリケーションに！
