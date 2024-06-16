# -*- coding: utf-8 -*-
# Copyright (c) 2024 MainFrame Monkey <https://www.mainframemonkey.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Knowledge Share with token",
    "summary": "This modules allows token generation for knowledge.",
    "version": "16.0.1.1.0",
    "website": "https://www.mainframemonkey.com",
    "author": "Mainframe Monkey",
    "license": "LGPL-3",
    "depends": [
        "website_knowledge",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "wizard/knowledge_token_invite_views.xml",
        "views/knowledge_article_views.xml",
        "views/knowledge_article_token_views.xml",
        "views/knowledge_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "knowledge_share_with_token/static/src/js/knowledge_frontend.js",
        ],
    },
    "application": False,
    "installable": True,
}
