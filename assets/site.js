/* ================================================================
   HEAVY MACHINERY ENCYCLOPEDIA — SHARED SITE SCRIPT
   Builds header nav + the site index overlay from graph.json, and
   computes every "Related" / "Real-World Applications" block at
   runtime from the same graph — authored once per page, linked
   automatically everywhere else.
   ================================================================ */
(function () {
  "use strict";
  var BASE = "/machinery/";
  var GRAPH_URL = BASE + "data/graph.json";

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === "text") n.textContent = attrs[k];
      else if (k === "html") n.innerHTML = attrs[k];
      else if (attrs[k] != null) n.setAttribute(k, attrs[k]);
    }
    (kids || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  function pageData() {
    var s = document.getElementById("page-data");
    if (!s) return null;
    try { return JSON.parse(s.textContent); } catch (e) { return null; }
  }
  function labelFor(list, id) {
    var m = list.filter(function (x) { return x.id === id; })[0];
    return m ? m.label : id;
  }

  /* ---- header + overlay ------------------------------------- */
  function buildHeader(graph) {
    var header = document.getElementById("site-header");
    if (!header) return;
    var inner = header.querySelector(".hdr-inner");
    if (!inner) return;
    var menuBtn = el("button", { type: "button", "aria-haspopup": "dialog", "aria-expanded": "false", "aria-controls": "site-overlay", text: "Index" });
    var nav = inner.querySelector(".hdr-nav") || el("div", { "class": "hdr-nav" });
    if (!inner.contains(nav)) inner.appendChild(nav);
    nav.appendChild(menuBtn);

    var overlay = el("div", { "class": "overlay", id: "site-overlay", hidden: "", role: "dialog", "aria-modal": "true", "aria-label": "Site index" });
    var top = el("div", { "class": "overlay-top" }, [
      el("span", { "class": "overlay-title", text: (graph.site && graph.site.title) || "Index" }),
      el("button", { "class": "overlay-close", type: "button", text: "Close ✕" })
    ]);
    var body = el("div", { "class": "overlay-body" });

    var machineGroup = el("div", { "class": "overlay-group" }, [el("h3", { text: "Machines" })]);
    (graph.categories || []).forEach(function (cat) {
      var machines = (graph.machines || []).filter(function (m) { return m.category === cat.id; });
      if (!machines.length) return;
      var ul = el("ul");
      machines.forEach(function (m) {
        ul.appendChild(el("li", null, [el("a", { href: BASE + "machines/" + m.slug + "/", text: m.title })]));
      });
      var group = el("div", { "class": "overlay-group" }, [el("h3", { text: cat.label }), ul]);
      body.appendChild(group);
    });

    (graph.domains || []).forEach(function (dom) {
      var concepts = (graph.concepts || []).filter(function (c) { return c.domain === dom.id; });
      if (!concepts.length) return;
      var ul = el("ul");
      concepts.forEach(function (c) {
        ul.appendChild(el("li", null, [el("a", { href: BASE + "concepts/" + c.slug + "/", text: c.title })]));
      });
      body.appendChild(el("div", { "class": "overlay-group" }, [el("h3", { text: "Concepts — " + dom.label }), ul]));
    });

    overlay.appendChild(top);
    overlay.appendChild(body);
    document.body.appendChild(overlay);

    var closeBtn = top.querySelector(".overlay-close");
    function setOpen(open) {
      overlay.hidden = !open;
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
      document.documentElement.style.overflow = open ? "hidden" : "";
      if (open) closeBtn.focus(); else menuBtn.focus();
    }
    menuBtn.addEventListener("click", function () { setOpen(overlay.hidden); });
    closeBtn.addEventListener("click", function () { setOpen(false); });
    overlay.addEventListener("click", function (e) { if (e.target === overlay) setOpen(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !overlay.hidden) setOpen(false); });
  }

  /* ---- related-machines (machine pages) ---------------------- */
  function renderRelatedMachines(graph, here) {
    var mount = document.getElementById("relatedMachines");
    if (!mount) return;
    var others = (graph.machines || []).filter(function (m) { return m.slug !== here.slug; });
    var scored = others.map(function (m) {
      var shared = (m.principles || []).filter(function (p) { return (here.principles || []).indexOf(p) > -1; }).length;
      var sameCat = m.category === here.category ? 1 : 0;
      return { m: m, score: shared * 2 + sameCat };
    }).filter(function (x) { return x.score > 0; });
    scored.sort(function (a, b) { return b.score - a.score; });
    var top = scored.slice(0, 6).map(function (x) { return x.m; });
    if (!top.length) { mount.innerHTML = ""; mount.appendChild(el("p", { "class": "related-empty", text: "No cross-linked machines yet." })); return; }
    top.forEach(function (m) {
      mount.appendChild(el("a", { "class": "related-card", href: BASE + "machines/" + m.slug + "/" }, [
        el("span", { "class": "rc-cat", text: labelFor(graph.categories, m.category) }),
        el("span", { "class": "rc-title", text: m.title })
      ]));
    });
  }

  /* ---- real-world applications + related concepts (concept pages) */
  function renderConceptRelations(graph, here) {
    var appMount = document.getElementById("realWorldApplications");
    if (appMount) {
      var applying = (graph.machines || []).filter(function (m) { return (m.principles || []).indexOf(here.slug) > -1; });
      if (!applying.length) {
        appMount.appendChild(el("p", { "class": "related-empty", text: "No machine pages cite this concept yet." }));
      } else {
        applying.forEach(function (m) {
          appMount.appendChild(el("a", { "class": "related-card", href: BASE + "machines/" + m.slug + "/" }, [
            el("span", { "class": "rc-cat", text: labelFor(graph.categories, m.category) }),
            el("span", { "class": "rc-title", text: m.title })
          ]));
        });
      }
    }
    var relMount = document.getElementById("relatedConcepts");
    if (relMount) {
      var ids = here.relatedConcepts || [];
      var concepts = ids.map(function (id) { return (graph.concepts || []).filter(function (c) { return c.slug === id; })[0]; }).filter(Boolean);
      if (!concepts.length) {
        relMount.appendChild(el("p", { "class": "related-empty", text: "—" }));
      } else {
        concepts.forEach(function (c) {
          relMount.appendChild(el("a", { "class": "related-card", href: BASE + "concepts/" + c.slug + "/" }, [
            el("span", { "class": "rc-cat", text: labelFor(graph.domains, c.domain) }),
            el("span", { "class": "rc-title", text: c.title })
          ]));
        });
      }
    }
  }

  function boot() {
    fetch(GRAPH_URL, { cache: "default" })
      .then(function (r) { if (!r.ok) throw new Error("graph " + r.status); return r.json(); })
      .then(function (graph) {
        buildHeader(graph);
        var here = pageData();
        if (!here) return;
        if (here.type === "machine") renderRelatedMachines(graph, here);
        if (here.type === "concept") renderConceptRelations(graph, here);
      })
      .catch(function (err) { console.warn("site graph unavailable", err); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
