from __future__ import annotations

from rest_framework.routers import DefaultRouter, SimpleRouter


class NoFormatSuffixRouter(SimpleRouter):
    """
    format_suffix_patternsを適用しないルーター。
    複数のルーターを使用する際のコンバーター重複登録エラーを防ぐ。
    SimpleRouterを継承し、DefaultRouterのformat_suffix_patternsを回避。
    """

    include_root_view = True
    routes = DefaultRouter.routes
