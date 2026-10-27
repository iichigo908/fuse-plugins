// Renders the list page (index.html) and the detail page (plugin.html?id=...)
// from window.SITE_DATA (data/plugins.js, generated from data/plugins.json).
(function () {
	const data = window.SITE_DATA;
	const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
	const kb = (n) => (n >= 1024 * 1024 ? (n / 1024 / 1024).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1024)) + " KB");
	const $ = (sel) => document.querySelector(sel);

	function header() {
		$("#site-name").textContent = data.site.name;
		document.querySelectorAll("[data-site-name]").forEach((el) => (el.textContent = data.site.name));
		const tag = $("#site-tagline");
		if (tag) tag.textContent = data.site.tagline;
		const about = $("#site-about");
		if (about) about.textContent = data.site.about;
		const year = $("#year");
		if (year) year.textContent = new Date().getFullYear();
	}

	// ------------------------------------------------------------- list page
	function card(p) {
		return `<a class="card" href="plugin.html?id=${encodeURIComponent(p.id)}">
			<div class="thumb"><img src="${esc(p.coverUrl)}" alt="" loading="lazy"></div>
			<div class="body">
				<div class="meta"><span class="badge">${esc(p.category)}</span><span>v${esc(p.version)}</span></div>
				<h2>${esc(p.name)}</h2>
				<p class="summary">${esc(p.summary)}</p>
				<div class="meta">${p.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>
			</div>
		</a>`;
	}

	function listPage() {
		const grid = $("#grid"), search = $("#search"), chips = $("#chips");
		// chips = categories; tags are found through the search box
		const tags = [...new Set(data.plugins.map((p) => p.category))];
		let active = "";
		chips.innerHTML = [`<button class="chip" aria-pressed="true" data-tag="">すべて</button>`]
			.concat(tags.map((t) => `<button class="chip" aria-pressed="false" data-tag="${esc(t)}">${esc(t)}</button>`)).join("");
		function render() {
			const q = search.value.trim().toLowerCase();
			const list = data.plugins.filter((p) => {
				if (active && p.category !== active && !p.tags.includes(active)) return false;
				if (!q) return true;
				return [p.name, p.summary, p.category, ...p.tags, ...p.description].join(" ").toLowerCase().includes(q);
			});
			grid.innerHTML = list.length ? list.map(card).join("") : `<p class="empty">該当するプラグインがありません</p>`;
		}
		chips.addEventListener("click", (e) => {
			const b = e.target.closest(".chip");
			if (!b) return;
			active = b.dataset.tag;
			chips.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", String(c === b)));
			render();
		});
		search.addEventListener("input", render);
		render();
	}

	// ------------------------------------------------------------- detail page
	function detailPage() {
		const id = new URLSearchParams(location.search).get("id");
		const p = data.plugins.find((x) => x.id === id);
		const main = $("#detail");
		if (!p) {
			main.innerHTML = `<p class="empty">プラグインが見つかりません。<a href="index.html">一覧へ戻る</a></p>`;
			return;
		}
		document.title = `${p.name} | ${data.site.name}`;
		const inst = data.install[p.install];
		const steps = (arr) => `<ol>${arr.map((s) => `<li>${esc(s)}</li>`).join("")}</ol>`;
		const credits = p.credits.length
			? `<div class="box credits"><h3>クレジット</h3><ul>${p.credits.map((c) =>
				`<li>${c.url ? `<a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.text)}</a>` : esc(c.text)}${c.license ? `（${esc(c.license)}）` : ""}</li>`).join("")}</ul>
				${p.credits.some((c) => c.license) ? `<p class="manual">ライセンス表記は zip 内の THIRD_PARTY_NOTICES.txt にあります。</p>` : ""}</div>`
			: "";
		main.innerHTML = `
			<a class="back" href="index.html">← 一覧へ戻る</a>
			<div class="detail-head">
				<div class="hero"><img src="${esc(p.coverUrl)}" alt=""></div>
				<div>
					<div class="meta"><span class="badge">${esc(p.category)}</span>${p.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>
					<h1>${esc(p.name)}</h1>
					<p class="lead">${esc(p.summary)}</p>
					<a class="btn" href="${esc(p.download.url)}" download>ダウンロード <small>v${esc(p.version)} ・ ${kb(p.download.size)}</small></a>
					<div class="sub">更新日 ${esc(p.updated)} ・ Mac / Windows</div>
				</div>
			</div>
			<div class="sections">
				<div>
					<section class="section"><h2>概要</h2>${p.description.map((d) => `<p>${esc(d)}</p>`).join("")}</section>
					<section class="section"><h2>主な機能</h2><ul>${p.features.map((f) => `<li>${esc(f)}</li>`).join("")}</ul></section>
					<section class="section"><h2>使い方</h2>${steps(p.usage)}</section>
					${p.galleryUrls.length ? `<section class="section"><h2>サンプル</h2><div class="gallery">${p.galleryUrls.map((g) =>
						`<figure><img src="${esc(g.url)}" alt="${esc(g.caption)}" loading="lazy"><figcaption>${esc(g.caption)}</figcaption></figure>`).join("")}</div></section>` : ""}
				</div>
				<aside class="side">
					<div class="box">
						<h3>${esc(inst.title)}</h3>
						<div class="tabs" role="tablist">
							<button class="tab" role="tab" aria-selected="true" data-os="mac">Mac</button>
							<button class="tab" role="tab" aria-selected="false" data-os="windows">Windows</button>
						</div>
						<div data-panel="mac">${steps(inst.mac)}</div>
						<div data-panel="windows" hidden>${steps(inst.windows)}</div>
						<p class="manual">${esc(inst.manual)}</p>
					</div>
					<div class="box"><h3>動作環境</h3><p>${esc(p.requirements)}</p></div>
					${credits}
					<div class="box"><h3>更新履歴</h3><ul class="changelog">${p.changelog.map((c) =>
						`<li><span class="v">v${esc(c.version)}</span><span class="d">${esc(c.date)}</span>${esc(c.notes)}</li>`).join("")}</ul></div>
				</aside>
			</div>`;
		// default tab follows the visitor's OS
		const isWin = /Win/i.test(navigator.platform || navigator.userAgent);
		const tabs = main.querySelectorAll(".tab");
		const show = (os) => {
			tabs.forEach((t) => t.setAttribute("aria-selected", String(t.dataset.os === os)));
			main.querySelectorAll("[data-panel]").forEach((el) => (el.hidden = el.dataset.panel !== os));
		};
		tabs.forEach((t) => t.addEventListener("click", () => show(t.dataset.os)));
		show(isWin ? "windows" : "mac");
	}

	header();
	if (document.body.dataset.page === "list") listPage();
	if (document.body.dataset.page === "detail") detailPage();
})();
