// POKEDEX는 data.js에서 전역으로 온다.

function typePill(t) {
  return `<span class="type-pill" style="background:var(--type-${CSS.escape(t)});color:var(--type-${CSS.escape(t)}-fg)">${t}</span>`;
}

function highlight(text, query) {
  if (!query) return text;
  const idx = text.indexOf(query);
  if (idx === -1) return text;
  return text.slice(0, idx) + "<mark>" + text.slice(idx, idx + query.length) + "</mark>" + text.slice(idx + query.length);
}

function findByName(name) {
  return POKEDEX.find(m => m.name_ko === name);
}

function renderEvolution(evo, currentName) {
  if (!evo || evo.length === 0) {
    return `<div class="evo-single">진화 없음</div>`;
  }
  const order = [evo[0].from];
  evo.forEach(e => { if (order[order.length - 1] === e.from) order.push(e.to); });

  let html = '<div class="evo-chain">';
  order.forEach((name, i) => {
    const isCurrent = name === currentName;
    const available = !isCurrent && findByName(name);
    if (isCurrent) {
      html += `<span class="evo-node current">${name}</span>`;
    } else if (available) {
      html += `<button type="button" class="evo-node" data-goto="${name}" title="${name} 정보 보기">${name}</button>`;
    } else {
      html += `<button type="button" class="evo-node" disabled title="도감에 없는 포켓몬">${name}</button>`;
    }
    if (i < order.length - 1) {
      const cond = evo[i].condition;
      html += `<span class="evo-arrow">
        <svg width="20" height="14" viewBox="0 0 20 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="1" y1="7" x2="17" y2="7"/><polyline points="12 2 17 7 12 12"/></svg>
        <span class="cond">${cond}</span>
      </span>`;
    }
  });
  html += '</div>';
  return html;
}

function renderLocations(loc) {
  const groups = [
    { label: "본편 (스칼렛 · 바이올렛)", items: loc.base_game },
    { label: "DLC", items: loc.dlc },
  ];
  return '<div class="loc-groups">' + groups.map(g => {
    if (!g.items || g.items.length === 0) {
      return `<div class="loc-group"><h4>${g.label}</h4><div class="loc-empty">확인된 필드 입수처 없음 (진화/교환 등으로만 획득)</div></div>`;
    }
    return `<div class="loc-group"><h4>${g.label}</h4><div class="loc-tags">${g.items.map(i => `<span class="tag">${i}</span>`).join('')}</div></div>`;
  }).join('') + '</div>';
}

let currentMoveDetails = {};

function moveButton(name, extraClass) {
  return `<button type="button" class="move-name ${extraClass || ''}" data-move="${name}">${name}</button>`;
}

function renderDetail(mon) {
  currentMoveDetails = mon.move_details || {};
  const el = document.getElementById('detail-card');
  el.innerHTML = `
    <div class="detail-head">
      <div class="mon-portrait">${mon.image_url ? `<img src="${mon.image_url}" alt="${mon.name_ko}" loading="lazy" />` : ''}</div>
      <div>
        <div class="id">No. ${String(mon.dex_number).padStart(3, '0')}</div>
        <h2>${mon.name_ko}</h2>
        <div class="types">${mon.types.map(typePill).join('')}</div>
      </div>
    </div>

    <section class="block">
      <h3>진화</h3>
      ${renderEvolution(mon.evolution, mon.name_ko)}
    </section>

    <section class="block">
      <h3>기술 <span class="hint">(이름을 탭하면 세부정보)</span></h3>
      <div class="moves-grid">
        <div class="moves-col">
          <h4>레벨업 (${mon.moves.level_up.length})</h4>
          <ul class="move-list">
            ${mon.moves.level_up.map(m => `<li>${moveButton(m.move)}<span class="lv">Lv.${m.level}</span></li>`).join('')}
          </ul>
        </div>
        <div class="moves-col">
          <h4>기술머신 (${mon.moves.machine.length})</h4>
          <div class="tm-tags">${mon.moves.machine.map(m => moveButton(m, 'tag')).join('')}</div>
        </div>
      </div>
    </section>

    <section class="block">
      <h3>스칼렛 · 바이올렛 입수 방법</h3>
      ${renderLocations(mon.sv_locations)}
    </section>
  `;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function goToPokemon(name) {
  const mon = findByName(name);
  if (!mon) return;
  renderDetail(mon);
  document.getElementById('search-input').value = mon.name_ko;
}

document.getElementById('detail-card').addEventListener('click', (e) => {
  const gotoBtn = e.target.closest('button[data-goto]');
  if (gotoBtn) { goToPokemon(gotoBtn.dataset.goto); return; }

  const moveBtn = e.target.closest('button[data-move]');
  if (moveBtn) showMoveTooltip(moveBtn.dataset.move);
});

// --- 기술 세부정보 툴팁 ---
const tooltipBackdrop = document.getElementById('move-tooltip-backdrop');
const tooltipCard = document.getElementById('move-tooltip-card');

function statRow(label, value) {
  return `<div class="tooltip-stat"><span class="tooltip-stat-label">${label}</span><span class="tooltip-stat-value">${value}</span></div>`;
}

function showMoveTooltip(name) {
  const d = currentMoveDetails[name];
  tooltipCard.innerHTML = `
    <button type="button" class="tooltip-close" id="tooltip-close" aria-label="닫기">✕</button>
    <div class="tooltip-header">
      <span class="tooltip-name">${name}</span>
      ${d ? typePill(d.type) : ''}
    </div>
    ${d ? `
      <div class="tooltip-stats">
        ${statRow('분류', d.category)}
        ${statRow('위력', d.power ?? '-')}
        ${statRow('명중률', d.accuracy != null ? d.accuracy + '%' : '-')}
        ${statRow('PP', d.pp ?? '-')}
      </div>
      ${d.description ? `<p class="tooltip-desc">${d.description.replace(/\n/g, '<br>')}</p>` : ''}
    ` : `<p class="tooltip-desc">세부 정보를 찾을 수 없습니다.</p>`}
  `;
  tooltipBackdrop.hidden = false;
}

function hideMoveTooltip() {
  tooltipBackdrop.hidden = true;
}

tooltipBackdrop.addEventListener('click', (e) => {
  // 카드 바깥(배경) 클릭 또는 닫기 버튼 클릭 시 닫는다
  if (e.target === tooltipBackdrop || e.target.closest('#tooltip-close')) {
    hideMoveTooltip();
  }
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !tooltipBackdrop.hidden) hideMoveTooltip();
});

// --- 검색/자동완성 ---
const input = document.getElementById('search-input');
const suggestionsEl = document.getElementById('suggestions');
const countEl = document.getElementById('search-count');
let activeIndex = -1;
let currentMatches = [];

function updateSuggestions() {
  const q = input.value.trim();
  activeIndex = -1;
  if (!q) {
    suggestionsEl.hidden = true;
    return;
  }
  currentMatches = POKEDEX.filter(m => m.name_ko.includes(q));
  if (currentMatches.length === 0) {
    suggestionsEl.hidden = false;
    suggestionsEl.innerHTML = `<div class="suggestion" style="cursor:default">검색 결과 없음</div>`;
    return;
  }
  suggestionsEl.innerHTML = currentMatches.slice(0, 30).map((m, i) => `
    <button type="button" class="suggestion" data-index="${i}" role="option">
      <span class="dex-no">#${String(m.dex_number).padStart(3,'0')}</span>
      ${m.image_url ? `<img class="thumb" src="${m.image_url}" alt="" loading="lazy" />` : ''}
      <span>${highlight(m.name_ko, q)}</span>
      <span class="types">${m.types.map(typePill).join('')}</span>
    </button>
  `).join('');
  suggestionsEl.hidden = false;
}

function selectMatch(i) {
  const mon = currentMatches[i];
  if (!mon) return;
  renderDetail(mon);
  input.value = mon.name_ko;
  suggestionsEl.hidden = true;
}

input.addEventListener('input', updateSuggestions);
input.addEventListener('focus', () => { if (input.value.trim()) updateSuggestions(); });
document.addEventListener('click', (e) => {
  if (!e.target.closest('.search-area')) suggestionsEl.hidden = true;
});
suggestionsEl.addEventListener('click', (e) => {
  const btn = e.target.closest('.suggestion[data-index]');
  if (btn) selectMatch(Number(btn.dataset.index));
});
input.addEventListener('keydown', (e) => {
  if (suggestionsEl.hidden || currentMatches.length === 0) return;
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    activeIndex = Math.min(activeIndex + 1, currentMatches.length - 1);
    updateActive();
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    activeIndex = Math.max(activeIndex - 1, 0);
    updateActive();
  } else if (e.key === 'Enter') {
    e.preventDefault();
    selectMatch(activeIndex >= 0 ? activeIndex : 0);
  } else if (e.key === 'Escape') {
    suggestionsEl.hidden = true;
  }
});
function updateActive() {
  [...suggestionsEl.children].forEach((c, i) => c.classList.toggle('active', i === activeIndex));
  const activeEl = suggestionsEl.children[activeIndex];
  if (activeEl) activeEl.scrollIntoView({ block: 'nearest' });
}

// --- 초기 상태 & PWA 등록 ---
countEl.textContent = `총 ${POKEDEX.length}종`;
const first = [...POKEDEX].sort((a, b) => a.dex_number - b.dex_number)[0];
if (first) renderDetail(first);

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch(() => {});
  });
}
