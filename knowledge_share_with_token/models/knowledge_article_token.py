# -*- coding: utf-8 -*-
# Copyright (c) 2024 MainFrame Monkey <https://www.mainframemonkey.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import uuid

from odoo import api, fields, models
from werkzeug.urls import url_join


class KnowledgeArticleToken(models.Model):
    _name = "knowledge.article.token"
    _description = "Knowledge Article Token"

    name = fields.Char(
        required=True,
        readonly=True,
    )
    article_id = fields.Many2one(
        "knowledge.article",
        required=True,
        readonly=True,
    )
    access_token = fields.Char(
        required=True,
        copy=False,
        readonly=True,
    )
    token_article_url = fields.Char(
        compute="_compute_token_article_url",
    )
    partner_id = fields.Many2one(
        "res.partner",
        readonly=True,
    )
    root_article = fields.Boolean(
        readonly=True,
    )

    _sql_constraints = [
        (
            "access_token_article_uniq",
            "unique (access_token, article_id)",
            "The access token must be unique per article.",
        ),
        (
            "name_article_uniq",
            "unique (name, article_id)",
            "The name must be unique per article.",
        ),
    ]

    @api.depends("article_id", "access_token")
    def _compute_token_article_url(self):
        for record in self:
            record.token_article_url = url_join(
                record.article_id.get_base_url(),
                f"knowledge/article/{record.article_id.id}/{record.access_token}",
            )

    @api.model
    def _check_token_uniqueness(self, token):
        return self.search_count([("access_token", "=", token)], limit=1) == 0

    @api.model
    def generate_unique_access_token(self):
        token = str(uuid.uuid4())
        if not self._check_token_uniqueness(token):
            token = self.generate_unique_access_token()
        return token

    def action_delete_token(self):
        self.unlink()
