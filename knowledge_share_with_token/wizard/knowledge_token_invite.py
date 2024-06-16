# -*- coding: utf-8 -*-
# Copyright (c) 2024 MainFrame Monkey <https://www.mainframemonkey.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from werkzeug.urls import url_join


class KnowledgeTokenInvite(models.TransientModel):
    _name = "knowledge.token.invite"
    _description = "Knowledge Token Invite Wizard"

    name = fields.Char(required=True)
    article_id = fields.Many2one("knowledge.article", required=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner")
    root_article = fields.Boolean(help="Share all child articles recursively.")
    access_token = fields.Char(readonly=True)
    token_article_url = fields.Char(compute="_compute_token_article_url")
    token_article_ids = fields.One2many(related="article_id.shared_token_ids")

    @api.depends("article_id", "access_token")
    def _compute_token_article_url(self):
        for record in self:
            record.token_article_url = url_join(
                record.article_id.get_base_url(),
                f"knowledge/article/{record.article_id.id}/{record.access_token}",
            )

    def action_save_token(self):
        self.ensure_one()
        self.article_id.create_shared_token(
            self.name,
            self.access_token,
            partner=self.partner_id,
            root_article=self.root_article,
        )
        return {"type": "ir.actions.act_window_close"}
