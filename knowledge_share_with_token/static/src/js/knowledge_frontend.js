/** @odoo-module */
"use strict";

import publicWidget from "web.public.widget";

publicWidget.registry.KnowledgeWidget.include({
  is_valid_uuid4: function (uuid) {
    let uuidRegex =
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
  },

  renderViewLinks() {
    let access_token = window.location.pathname.split("/").pop();
    if (this.is_valid_uuid4(access_token)) {
      for (const viewLink of this.el.getElementsByClassName(
        "o_knowledge_article_structure_link",
      )) {
        let article_id = viewLink.href.split("/").pop();
        viewLink.href = `/knowledge/article/${article_id}/${access_token}`;
      }
      for (const viewLink of this.el.getElementsByClassName(
        "o_knowledge_behavior_type_article",
      )) {
        let article_id = viewLink.href.split("/").pop();
        viewLink.href = `/knowledge/article/${article_id}/${access_token}`;
      }
    } else {
      this._super.apply(this, arguments);
    }
  },

  _searchArticles: async function (ev) {
    let access_token = window.location.pathname.split("/").pop();
    if (this.is_valid_uuid4(access_token)) {
      ev.preventDefault();
      const searchTerm = this.$(".knowledge_search_bar").val();
      if (!searchTerm) {
        // Renders the basic user article tree (with only its cached articles unfolded)
        await this._renderTree(this.$id, "/knowledge/tree_panel/portal");
        return;
      }
      // Renders articles based on search term in a flatenned tree (no sections nor child articles)
      const container = this.el.querySelector(".o_knowledge_tree");
      try {
        const htmlTree = await this._rpc({
          route: "/knowledge_share_with_token/tree_panel/portal/search",
          params: {
            search_term: searchTerm,
            active_article_id: this.$id,
            access_token: access_token,
          },
        });
        container.innerHTML = htmlTree;
      } catch {
        container.innerHTML = "";
      }
    } else {
      this._super.apply(this, arguments);
    }
  },

  _renderTree: async function (active_article_id, route) {
    let access_token = window.location.pathname.split("/").pop();
    if (this.is_valid_uuid4(access_token)) {
      const container = this.el.querySelector(".o_knowledge_tree");
      let unfoldedArticlesIds = localStorage.getItem("knowledge.unfolded.ids");
      unfoldedArticlesIds = unfoldedArticlesIds
        ? unfoldedArticlesIds.split(";").map(Number)
        : [];
      let unfoldedFavoriteArticlesIds = localStorage.getItem(
        "knowledge.unfolded.favorite.ids",
      );
      unfoldedFavoriteArticlesIds = unfoldedFavoriteArticlesIds
        ? unfoldedFavoriteArticlesIds.split(";").map(Number)
        : [];
      const params = new URLSearchParams(document.location.search);
      if (Boolean(params.get("auto_unfold"))) {
        unfoldedArticlesIds.push(active_article_id);
        unfoldedFavoriteArticlesIds.push(active_article_id);
      }
      if (route === "/knowledge/tree_panel/portal") {
        route = "/knowledge_share_with_token/tree_panel/portal";
      }
      try {
        const htmlTree = await this._rpc({
          route: route,
          params: {
            active_article_id: active_article_id,
            unfolded_articles_ids: unfoldedArticlesIds,
            unfolded_favorite_articles_ids: unfoldedFavoriteArticlesIds,
            access_token: access_token,
          },
        });
        container.innerHTML = htmlTree;
        this._setTreeFavoriteListener();
      } catch {
        container.innerHTML = "";
      }
    } else {
      return this._super.apply(this, arguments);
    }
  },
});
