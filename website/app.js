const app = document.getElementById("app");
let events = [], elos = {};
const LOCAL = ["localhost", "127.0.0.1", "[::1]"].includes(location.hostname); // team analysis needs website.py

const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const clean = s => s.replace(/(Competition|Override)�/g, "$1™");
const uniq = a => [...new Set(a.filter(Boolean))].sort();
const CHANGE = /^(\S+?)(?: \(([\d.]+)x\))?: ([+-]\d+) \((\d+) -> (\d+)\)$/;

function prep(e, i) {
  const [a, b] = e.Date.split(" to ");
  const matches = e.Divisions.flatMap(d => d.Matches);
  const teams = new Set();
  for (const m of matches) for (const t of m.Matchup.split(/ \+ | vs\. /)) teams.add(t);
  const cut = e.Region.lastIndexOf(", ");
  return { ...e, i, country: cut < 0 ? e.Region : e.Region.slice(cut + 2), state: cut < 0 ? "" : e.Region.slice(0, cut), sku: e.Link.match(/([^/]+)\.html$/)[1], Name: clean(e.Name), start: a, date: a === b ? a : e.Date.replace(" to ", " – "),
           matches, teams, search: clean(e.Name).toLowerCase() };
}

const tabs = on => `<nav class="tabs"><a href="#/" class="${on === "t" ? "on" : ""}">Tournaments</a><a href="#/teams" class="${on === "m" ? "on" : ""}">Teams</a></nav>`;

// team -> { name, evs: [{ e, before, after, w, l }], elo, rank }, built on first use
let teamIdx;
function teamIndex() {
  if (teamIdx) return teamIdx;
  teamIdx = new Map();
  const chrono = [...events].sort((a, b) => (a.start < b.start ? -1 : a.start > b.start ? 1 : a.i - b.i));
  for (const e of chrono) {
    const rec = new Map();
    for (const m of e.matches) {
      const ch = parseChanges(m);
      for (const t of m.Matchup.split(/ \+ | vs\. /)) {
        if (!rec.has(t)) {
          const r = { e, before: null, after: null, w: 0, l: 0, t: 0, q: [0, 0, 0], el: [0, 0, 0] };
          rec.set(t, r);
          if (!teamIdx.has(t)) teamIdx.set(t, { name: t, evs: [], elo: null });
          teamIdx.get(t).evs.push(r);
        }
        const c = ch.get(t), r = rec.get(t);
        if (!c) continue;
        if (r.before === null) r.before = c.before;
        r.after = c.after;
        const sc = /^(\d+)-(\d+)$/.exec(m.Score);
        if (!sc || +sc[1] + +sc[2] === 0) continue; // skip 0-0
        const i = sc[1] === sc[2] ? 2 : (+sc[1] > +sc[2]) === m.Matchup.split(" vs. ")[0].split(" + ").includes(t) ? 0 : 1;
        r["wlt"[i]]++;
        (m.Match.startsWith("Qual") ? r.q : r.el)[i]++;
      }
    }
  }
  for (const t of teamIdx.values()) t.elo = elos[t.name] ?? t.evs.findLast(r => r.after !== null)?.after ?? null;
  // stable sort, so ties keep elos.json's order
  Object.keys(elos).sort((a, b) => elos[b] - elos[a]).forEach((n, i) => { if (teamIdx.has(n)) teamIdx.get(n).rank = i + 1; });
  return teamIdx;
}

function teamsView() {
  app.innerHTML = `
    <h1>PElo</h1>${tabs("m")}
    <div class="controls"><input type="search" id="q" placeholder="Search by team number"></div>
    <div class="muted" id="count"></div>
    <table class="events ranks"><thead><tr><th>Rank</th><th>Team</th><th>Elo</th></tr></thead><tbody id="rows"></tbody></table><div class="pager"></div>`;
  const PER = 100;
  const q = app.querySelector("#q"), pagers = app.querySelectorAll(".pager");
  const all = [...teamIndex().values()].sort((a, b) => (b.elo ?? -1) - (a.elo ?? -1));
  let page = 0;
  const render = () => {
    const s = q.value.trim().toLowerCase();
    const list = all.filter(t => t.name.toLowerCase().includes(s));
    const pages = Math.max(1, Math.ceil(list.length / PER));
    page = Math.min(page, pages - 1);
    const shown = list.slice(page * PER, (page + 1) * PER);
    app.querySelector("#count").textContent = `${shown.length} of ${list.length} teams`;
    app.querySelector("#rows").innerHTML = shown.map(t => `<tr>
      <td>${t.rank ?? "–"}</td><td><a href="#/team/${encodeURIComponent(t.name)}">${esc(t.name)}</a></td>
      <td>${t.elo ?? "–"}</td></tr>`).join("");
    const btn = (p, label = p + 1) => `<button data-page="${p}" ${p === page ? "class=on" : ""} ${p < 0 || p >= pages ? "disabled" : ""}>${label}</button>`;
    const nums = [...new Set([0, page - 2, page - 1, page, page + 1, page + 2, pages - 1])].filter(p => p >= 0 && p < pages).sort((a, b) => a - b);
    pagers.forEach(p => p.innerHTML = pages < 2 ? "" : btn(page - 1, "&lt;") + nums.map((p, i) => (i && p - nums[i - 1] > 1 ? "<span>…</span>" : "") + btn(p)).join("") + btn(page + 1, "&gt;"));
  };
  q.addEventListener("input", () => { page = 0; render(); });
  pagers.forEach(p => p.addEventListener("click", ev => {
    const p = ev.target.dataset?.page;
    if (p !== undefined) { page = +p; render(); }
  }));
  render();
}

const SCORES = ["Skills", "Matches", "Driving", "Auton", "Judging", "Overall"];

// asks website.py to run eval.py for this team and shows the printed result
async function runEval(team, btn) {
  const out = app.querySelector("#evalout"), msg = app.querySelector("#evalmsg");
  btn.disabled = true; msg.textContent = " Running analysis…"; out.innerHTML = "";
  try {
    const r = await fetch("eval?team=" + encodeURIComponent(team));
    const lines = (await r.text()).split("\n").map(l => l.trim()).filter(Boolean);
    const scores = new Map(), notes = [];
    for (const l of lines) {
      const m = /^(\w+): (\d+)$/.exec(l);
      m && SCORES.includes(m[1]) ? scores.set(m[1], m[2]) : notes.push(l);
    }
    out.innerHTML = (scores.size ? `<div class="scores">${SCORES.filter(k => scores.has(k)).map(k =>
      `<div class="${k === "Overall" ? "overall" : ""}"><span>${k}</span>${scores.get(k)}</div>`).join("")}</div>` : "")
      + `<ul class="notes">${notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul>`;
    msg.remove();
    btn.remove(); // results take the button's place
  } catch (err) {
    msg.textContent = " Could not reach the server (is website.py running?)";
  }
  btn.disabled = false;
}

function teamView(t) {
  const sum = k => t.evs.reduce((a, r) => a.map((x, i) => x + (k === "all" ? [r.w, r.l, r.t][i] : r[k][i])), [0, 0, 0]).join("-");
  app.innerHTML = `
    <a href="#/teams">← All teams</a>
    <h1>${esc(t.name)}</h1>
    <div class="info">
      <div><span>Elo</span>${t.elo ?? "–"}</div><div><span>Rank</span>${t.rank ?? "–"}</div>
      <div><span>Events</span>${t.evs.length}</div><div><span>Match Record</span>${sum("all")}</div><div><span>Qual Record</span>${sum("q")}</div><div><span>Elim Record</span>${sum("el")}</div>
    </div>
    ${LOCAL ? `<div class="eval"><button id="eval">Run team analysis</button><span class="muted" id="evalmsg"></span><div id="evalout"></div></div>` : ""}
    <h2>Events</h2>
    <table class="events"><thead><tr><th>Date</th><th>Event</th><th>Record</th><th>Quals</th><th>Elo</th></tr></thead><tbody>
    ${[...t.evs].reverse().map(r => {
      const d = r.after === null ? "" : r.after - r.before;
      return `<tr><td>${esc(r.e.date)}</td><td><a href="#/event/${encodeURIComponent(r.e.sku)}?team=${encodeURIComponent(t.name)}">${esc(r.e.Name)}</a></td>
      <td>${r.w}-${r.l}-${r.t}</td><td>${r.q.join("-")}</td><td>${r.after === null ? "–" : `${r.before} → ${r.after} <span class="d"><span class="${d >= 0 ? "up" : "down"}">(${d > 0 ? "+" : ""}${d})</span></span>`}</td></tr>`;
    }).join("")}</tbody></table>`;
  app.querySelector("#eval")?.addEventListener("click", ev => runEval(t.name, ev.target));
}

function listView() {
  app.innerHTML = `
    <h1>PElo</h1>${tabs("t")}<div class="muted" id="count"></div>
    <div class="controls">
      <input type="search" id="q" placeholder="Search by event name">
      <select id="type"><option value="">All types</option>${[...new Set(events.map(e => e.Type))].sort().map(t => `<option>${esc(t)}</option>`).join("")}</select>
      <select id="country"><option value="">All countries</option>${uniq(events.map(e => e.country)).map(c => `<option>${esc(c)}</option>`).join("")}</select>
      <select id="region"></select>
      <select id="sort"><option value="new">Newest first</option><option value="old">Oldest first</option></select>
    </div>
    <table class="events"><thead><tr><th>Date</th><th>Event</th><th class="hide-sm">Region</th><th class="hide-sm">Type</th></tr></thead><tbody id="rows"></tbody></table>`;
  const q = app.querySelector("#q"), type = app.querySelector("#type"), sort = app.querySelector("#sort"), region = app.querySelector("#region"), country = app.querySelector("#country");
  const fillRegions = () => {
    const regions = uniq(events.filter(e => !country.value || e.country === country.value).map(e => e.state));
    region.innerHTML = `<option value="">All regions</option>` + regions.map(r => `<option>${esc(r)}</option>`).join("");
  };
  if (events.some(e => e.country === "United States")) country.value = "United States";
  fillRegions();
  country.addEventListener("input", fillRegions);
  const render = () => {
    const s = q.value.trim().toLowerCase();
    const list = events.filter(e => (!type.value || e.Type === type.value) && (!country.value || e.country === country.value) && (!region.value || e.state === region.value) && e.search.includes(s));
    list.sort((a, b) => (a.start < b.start ? -1 : a.start > b.start ? 1 : a.i - b.i) * (sort.value === "new" ? -1 : 1));
    app.querySelector("#count").textContent = `${list.length} of ${events.length} events`;
    app.querySelector("#rows").innerHTML = list.map(e => `<tr>
      <td>${esc(e.date)}</td><td><a href="#/event/${encodeURIComponent(e.sku)}">${esc(e.Name)}</a></td>
      <td class="hide-sm">${esc(e.Region)}</td>
      <td class="hide-sm"><span class="tag t-${e.Type.split(" ")[0].toLowerCase()}">${esc(e.Type)}</span></td></tr>`).join("");
  };
  [q, type, country, region, sort].forEach(el => el.addEventListener("input", render));
  render();
}

// red: elo on the outer left, name by the score; blue is the mirror image
function teamCell(name, ch, red) {
  const c = ch.get(name);
  const d = c ? `<span class="d"><span class="${c.delta > 0 ? "up" : "down"}">${c.delta > 0 ? "+" : ""}${c.delta}</span> (${c.before} → ${c.after})</span>` : "";
  const a = `<a href="#" data-team="${esc(name)}">${esc(name)}</a>`;
  return `<div class="team ${red ? "r" : ""}">${red ? d + a : a + d}</div>`;
}

function parseChanges(m) {
  const ch = new Map();
  for (const line of m.Changes || []) {
    const r = CHANGE.exec(line);
    if (r) ch.set(r[1], { delta: +r[3], before: +r[4], after: +r[5] });
  }
  return ch;
}

function matchRow(m) {
  const ch = parseChanges(m);
  const [red, blue] = m.Matchup.split(" vs. ").map(s => s.split(" + "));
  const sc = /^(\d+)-(\d+)$/.exec(m.Score);
  const score = sc
    ? `<b class="${+sc[1] > +sc[2] ? "red" : ""}">${sc[1]}</b> – <b class="${+sc[2] > +sc[1] ? "blue" : ""}">${sc[2]}</b>`
    : `<span class="dq">${{ "Blue DQ": `<b class="red">Blue DQ</b>`, "Red DQ": `<b class="blue">Red DQ</b>` }[m.Score] || esc(m.Score)}</span>`;
  const win = sc ? Math.sign(sc[1] - sc[2]) : { "Blue DQ": 1, "Red DQ": -1 }[m.Score] ?? 0;
  return `<tr data-teams=" ${esc(red.concat(blue).join(" ").toLowerCase())} " data-red=" ${esc(red.join(" ").toLowerCase())} " data-win="${win}">
    <td class="match-id">${esc(m.Match)}</td>
    <td class="red">${red.map(t => teamCell(t, ch, true)).join("")}</td>
    <td class="score">${score}<div class="res"></div></td>
    <td class="blue">${blue.map(t => teamCell(t, ch)).join("")}</td></tr>`;
}

function eventView(e) {
  app.innerHTML = `
    <a href="#/">← All tournaments</a>
    <h1>${esc(e.Name)}</h1>
    <div class="info">
      <div><span>Date</span>${esc(e.date)}</div><div><span>Region</span>${esc(e.Region)}</div>
      <div><span>Type</span>${esc(e.Type)}</div><div><span>Teams</span>${e.teams.size}</div>
      <div><span>Matches</span>${e.matches.length}</div>
      <div><span>Event page</span><a href="${esc(e.Link)}" target="_blank" rel="noopener">events.vex.com</a></div>
    </div>
    <div class="controls">
      <input type="search" id="team" placeholder="Filter by team (e.g. 3477D)">
      <select id="round"><option value="">All rounds</option><option value="Qual">Qualifications</option><option value="elim">Eliminations</option></select>
    </div>
    <div id="divs">${e.Divisions.map((d, n) => `<details${e.Divisions.length > 1 ? "" : " open"}><summary><h2>${esc(d.Name || `Division ${n + 1}`)}</h2></summary>
      <table class="matches"><thead><tr><th>Match</th><th class="red">Red alliance</th><th></th><th class="blue">Blue alliance</th></tr></thead>
      <tbody>${d.Matches.map(matchRow).join("")}</tbody></table></details>`).join("")}</div>`;
  const team = app.querySelector("#team"), round = app.querySelector("#round");
  team.value = new URLSearchParams(location.hash.split("?")[1]).get("team") || "";
  const rows = [...app.querySelectorAll("tbody tr")];
  const apply = () => {
    const t = team.value.trim().toLowerCase();
    rows.forEach((r, i) => {
      const isQual = e.matches[i].Match.startsWith("Qual");
      const exact = t && r.dataset.teams.includes(` ${t} `);
      const res = r.querySelector(".res");
      const w = exact ? +r.dataset.win * (r.dataset.red.includes(` ${t} `) ? 1 : -1) : null;
      res.textContent = w === null ? "" : w > 0 ? "W" : w < 0 ? "L" : "T";
      res.className = "res" + (w === null ? "" : w > 0 ? " w" : w < 0 ? " l" : " t");
      r.hidden = !(r.dataset.teams.includes(t) && (!round.value || (round.value === "Qual") === isQual));
    });
    app.querySelectorAll("#divs details").forEach(s => s.hidden = !s.querySelector("tbody tr:not([hidden])"));
  };
  [team, round].forEach(el => el.addEventListener("input", apply));
  apply();
  app.querySelector("#divs").addEventListener("click", ev => {
    const t = ev.target.dataset?.team;
    if (t) { ev.preventDefault(); team.value = t; apply(); }
  });
}

function route() {
  const m = /^#\/event\/([^/?]+)/.exec(location.hash);
  const e = m && events.find(e => e.sku === decodeURIComponent(m[1]));
  const t = /^#\/team\/([^/?]+)/.exec(location.hash);
  if (e) eventView(e);
  else if (t && teamIndex().has(decodeURIComponent(t[1]))) teamView(teamIndex().get(decodeURIComponent(t[1])));
  else if (location.hash.startsWith("#/teams")) teamsView();
  else listView();
  window.scrollTo(0, 0);
}

Promise.all(["events.json", "elos.json"].map(u => fetch(u).then(r => r.json()))).then(([d, e]) => {
  events = d.map(prep);
  elos = e;
  window.addEventListener("hashchange", route);
  route();
}).catch(err => { app.textContent = "Could not load data: " + err; });
