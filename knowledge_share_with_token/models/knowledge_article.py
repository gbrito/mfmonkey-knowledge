# -*- coding: utf-8 -*-
# Copyright (c) 2024 MainFrame Monkey <https://www.mainframemonkey.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class KnowledgeArticle(models.Model):
    _inherit = "knowledge.article"

    share_with_token = fields.Boolean(
        compute="_compute_share_with_token",
        store=True,
    )
    share_with_token_count = fields.Integer(
        compute="_compute_share_with_token",
        store=True,
    )
    shared_token_ids = fields.One2many(
        "knowledge.article.token",
        "article_id",
    )

    @api.depends("shared_token_ids")
    def _compute_share_with_token(self):
        for article in self:
            count = len(article.shared_token_ids)
            article.share_with_token = bool(count)
            article.share_with_token_count = count

    def valid_access_token(self, access_token):
        self.ensure_one()
        return self.shared_token_ids.filtered(lambda x: x.access_token == access_token)

    def _prepare_share_token_values(
        self,
        name,
        token,
        partner=False,
        root_article=False,
    ):
        self.ensure_one()
        return {
            "name": name,
            "article_id": self.id,
            "access_token": token,
            "partner_id": partner.id,
            "root_article": root_article,
        }

    @api.model
    def get_root_article_by_token(self, access_token):
        return (
            self.env["knowledge.article.token"]
            .search(
                [
                    ("access_token", "=", access_token),
                    ("root_article", "=", True),
                ]
            )
            .article_id
        )

    def get_child_articles(self):
        articles = self.env["knowledge.article"]

        articles |= self.child_ids

        if articles.child_ids:
            articles |= articles.get_child_articles()

        return articles

    def create_shared_token(self, name, token, partner=False, root_article=False):
        self.ensure_one()

        create_values = [
            self._prepare_share_token_values(
                name, token, partner=partner, root_article=root_article
            )
        ]

        if root_article:
            create_values.extend(
                article._prepare_share_token_values(
                    name, token, partner=partner, root_article=False
                )
                for article in self.get_child_articles()
            )

        return self.shared_token_ids.create(create_values)

    def action_open_manage_share_token(self):
        self.ensure_one()

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "knowledge_share_with_token.action_knowledge_token_invite"
        )

        access_token = self.shared_token_ids.generate_unique_access_token()

        action["context"] = {
            "default_article_id": self.id,
            "default_access_token": access_token,
        }

        return action
