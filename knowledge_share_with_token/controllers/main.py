# -*- coding: utf-8 -*-
# Copyright (c) 2024 MainFrame Monkey <https://www.mainframemonkey.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.addons.website_knowledge.controllers import main
from odoo.http import request


class KnowledgeWebsiteController(main.KnowledgeWebsiteController):
    @http.route(
        "/knowledge/article/<int:article_id>/<string:access_token>",
        type="http",
        auth="public",
        website=True,
    )
    def redirect_to_article_with_token(self, **kwargs):
        """This route will redirect internal users to the backend view of the
        article and the share users to the frontend view instead."""
        if "access_token" not in kwargs or "article_id" not in kwargs:
            return self._redirect_to_backend_view(False)

        article_id = kwargs["article_id"]
        access_token = kwargs["access_token"]
        article = request.env["knowledge.article"].sudo().browse(article_id)

        if not article.exists():
            return self._redirect_to_backend_view(article)

        if article and access_token and article.share_with_token:
            if not article.valid_access_token(access_token):
                return self._redirect_to_backend_view(article)

            if not request.env.user.has_group("base.group_user"):
                return self._redirect_to_portal_view(article)

        return self._redirect_to_backend_view(article)

    @http.route(
        "/knowledge_share_with_token/tree_panel/portal",
        type="json",
        auth="public",
    )
    def get_tree_panel_portal_token(
        self,
        active_article_id=False,
        unfolded_articles_ids=False,
        unfolded_favorite_articles_ids=False,
        access_token=False,
    ):
        """Frontend view of left panel tree for the portal users."""
        template_values = self._prepare_articles_tree_html_values(
            active_article_id,
            unfolded_articles_ids=unfolded_articles_ids,
            unfolded_favorite_articles_ids=unfolded_favorite_articles_ids,
        )

        template_values["access_token"] = access_token

        return request.env["ir.qweb"]._render(
            "knowledge.knowledge_article_tree_frontend", template_values
        )

    @http.route(
        "/knowledge_share_with_token/tree_panel/portal/search",
        type="json",
        auth="public",
    )
    def get_tree_panel_portal_search_token(
        self,
        search_term,
        active_article_id=False,
        access_token=False,
    ):
        # Get all shared token articles based on the search term
        all_visible_articles = request.env["knowledge.article"]

        if (
            request.env.user.is_public
            and active_article_id
            and (access_token := request.params.get("access_token"))
        ):
            article = request.env["knowledge.article"].sudo().browse(active_article_id)
            if article.valid_access_token(access_token):
                shared_articles = (
                    request.env["knowledge.article.token"]
                    .sudo()
                    .search([("access_token", "=", access_token)])
                )
                all_visible_articles = (
                    request.env["knowledge.article"]
                    .sudo()
                    .search(
                        [
                            ("id", "in", shared_articles.article_id.ids),
                            ("name", "ilike", search_term),
                        ],
                        order="name",
                        limit=self._KNOWLEDGE_TREE_ARTICLES_LIMIT,
                    )
                )

        values = {
            "search_tree": True,
            "active_article_id": active_article_id,
            "portal_readonly_mode": True,
            "articles": all_visible_articles,
            "access_token": access_token,
        }

        return request.env["ir.qweb"]._render(
            "knowledge.knowledge_article_tree_frontend", values
        )

    def _check_tree_shared_article(self):
        if access_token := request.params.get("access_token"):
            shared_articles = (
                request.env["knowledge.article.token"]
                .sudo()
                .search_count([("access_token", "=", access_token)])
            )
            return shared_articles > 1

        return False

    def _redirect_to_portal_view(self, article, hide_side_bar=False):
        if not request.params.get("access_token"):
            return super()._redirect_to_portal_view(
                article, hide_side_bar=hide_side_bar
            )

        return request.render(
            "knowledge.knowledge_article_view_frontend",
            {
                "article": article,
                "portal_readonly_mode": True,
                "show_sidebar": self._check_tree_shared_article(),
                "access_token": request.params.get("access_token"),
            },
        )

    def _prepare_articles_tree_html_values(
        self,
        active_article_id=False,
        unfolded_articles_ids=False,
        unfolded_favorite_articles_ids=False,
    ):
        values = super()._prepare_articles_tree_html_values(
            active_article_id=active_article_id,
            unfolded_articles_ids=unfolded_articles_ids,
            unfolded_favorite_articles_ids=unfolded_favorite_articles_ids,
        )

        if request.env.user.is_public and (
            access_token := request.params.get("access_token")
        ):
            article = request.env["knowledge.article"].sudo().browse(active_article_id)
            if not article.valid_access_token(access_token):
                return values

            if root_article := article.get_root_article_by_token(access_token):
                values["token_articles_ids"] = root_article.get_child_articles()
                values["access_token"] = access_token

        return values
