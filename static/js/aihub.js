/**
 * ITRI AI Hub — Frontend Logic
 * Handles: search/filter, pagination, sort, tabs, mobile filter toggle, login form
 */

const AIHub = (() => {
  // ---- State ----
  let state = {
    cards: [],          // all .model-card elements
    filtered: [],       // after filter+search
    page: 1,
    perPage: 10,
    sortMode: 'default',
  };

  // ---- Init ----
  function init() {
    state.cards = Array.from(document.querySelectorAll('.model-card'));
    state.filtered = [...state.cards];
    renderGrid();
    renderPagination();
    updateCount();
    buildFilterGroups();
  }

  // ---- Search ----
  function filterModels() {
    applyFilters();
  }

  // ---- Filters ----
  function applyFilters() {
    const query = (document.getElementById('searchInput')?.value || '').toLowerCase().trim();
    const devices   = checkedValues('.device-filter-cb');
    const chipsets  = checkedValues('.chipset-filter-cb');
    const tasks     = checkedValues('.task-filter-cb');

    state.filtered = state.cards.filter(card => {
      const name    = card.dataset.name    || '';
      const device  = card.dataset.device  || '';
      const chipset = card.dataset.chipset || '';
      const task    = card.dataset.task    || '';

      if (query && !name.includes(query) && !device.includes(query) && !task.includes(query))
        return false;
      if (devices.length  && !devices.some(d  => device.includes(d.toLowerCase())))
        return false;
      if (chipsets.length && !chipsets.some(c => chipset.includes(c.toLowerCase())))
        return false;
      if (tasks.length    && !tasks.some(t    => task.includes(t.toLowerCase())))
        return false;

      return true;
    });

    state.page = 1;
    sortCards();
    renderGrid();
    renderPagination();
    updateCount();
  }

  function checkedValues(selector) {
    return Array.from(document.querySelectorAll(selector))
      .filter(cb => cb.checked)
      .map(cb => cb.value);
  }

  function clearFilters() {
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    const search = document.getElementById('searchInput');
    if (search) search.value = '';
    state.filtered = [...state.cards];
    state.page = 1;
    renderGrid();
    renderPagination();
    updateCount();
  }

  // ---- Sort ----
  function sortModels(mode) {
    state.sortMode = mode;
    sortCards();
    renderGrid();
  }

  function sortCards() {
    if (state.sortMode === 'name_asc') {
      state.filtered.sort((a, b) => a.dataset.name.localeCompare(b.dataset.name));
    } else if (state.sortMode === 'name_desc') {
      state.filtered.sort((a, b) => b.dataset.name.localeCompare(a.dataset.name));
    }
    // 'default' keeps original DOM order (already set by filtered)
  }

  // ---- Grid render ----
  function renderGrid() {
    const grid = document.getElementById('modelGrid');
    if (!grid) return;

    const start = (state.page - 1) * state.perPage;
    const end   = start + state.perPage;
    const visible = state.filtered.slice(start, end);

    // Hide all, show page slice
    state.cards.forEach(c => c.style.display = 'none');
    visible.forEach(c => c.style.display = '');

    grid.style.opacity = '0.85';
    requestAnimationFrame(() => { grid.style.opacity = '1'; });
  }

  function updateCount() {
    const el = document.getElementById('resultNum');
    if (el) el.textContent = state.filtered.length;
  }

  // ---- Pagination ----
  function renderPagination() {
    const container = document.getElementById('pageNumbers');
    if (!container) return;

    const total = Math.ceil(state.filtered.length / state.perPage);
    container.innerHTML = '';

    if (total <= 1) return;

    const range = pageRange(state.page, total);
    range.forEach(p => {
      if (p === '…') {
        const span = document.createElement('span');
        span.textContent = '…';
        span.className = 'px-2 text-neutral-400 text-sm';
        container.appendChild(span);
      } else {
        const btn = document.createElement('button');
        btn.textContent = p;
        btn.className = 'page-btn' + (p === state.page ? ' active' : '');
        btn.onclick = () => goPage(p);
        container.appendChild(btn);
      }
    });
  }

  function pageRange(current, total) {
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const pages = [];
    pages.push(1);
    if (current > 3) pages.push('…');
    for (let p = Math.max(2, current - 1); p <= Math.min(total - 1, current + 1); p++)
      pages.push(p);
    if (current < total - 2) pages.push('…');
    pages.push(total);
    return pages;
  }

  function goPage(p) {
    const total = Math.ceil(state.filtered.length / state.perPage);
    state.page = Math.max(1, Math.min(p, total));
    renderGrid();
    renderPagination();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function prevPage()    { goPage(state.page - 1); }
  function nextPage()    { goPage(state.page + 1); }
  function goLastPage()  { goPage(Math.ceil(state.filtered.length / state.perPage)); }

  // ---- Mobile filter toggle ----
  function toggleMobileFilter() {
    const content  = document.getElementById('mobileFilterContent');
    const chevron  = document.getElementById('mobileFilterChevron');
    const btn      = document.getElementById('mobileFilterBtn');
    if (!content) return;

    const isOpen = !content.classList.contains('hidden');
    content.classList.toggle('hidden', isOpen);
    if (chevron) chevron.classList.toggle('rotated', !isOpen);
    if (btn) btn.setAttribute('aria-expanded', String(!isOpen));
  }

  // ---- Filter group accordion (desktop) ----
  function toggleFilter(panelId, btn) {
    const panel   = document.getElementById(panelId);
    const chevron = btn?.querySelector('.chevron-icon, svg, img');
    if (!panel) return;

    const collapsed = panel.classList.contains('collapsed') ||
                      panel.style.maxHeight === '0px';
    if (collapsed) {
      panel.classList.remove('collapsed');
      panel.classList.add('expanded');
      if (chevron) chevron.classList.add('rotated');
    } else {
      panel.classList.add('collapsed');
      panel.classList.remove('expanded');
      if (chevron) chevron.classList.remove('rotated');
    }
  }

  // ---- Dynamically build filter groups from card data ----
  function buildFilterGroups() {
    const container = document.getElementById('filterGroups');
    if (!container || state.cards.length === 0) return;

    const groups = {
      'Supported Device':  { key: 'device',  cls: 'device-filter-cb' },
      'Supported Chipset': { key: 'chipset', cls: 'chipset-filter-cb' },
      'Task':              { key: 'task',    cls: 'task-filter-cb' },
    };

    Object.entries(groups).forEach(([label, { key, cls }]) => {
      const values = [...new Set(
        state.cards
          .map(c => c.dataset[key])
          .filter(Boolean)
          .map(v => v.split(',').map(s => s.trim()))
          .flat()
          .filter(Boolean)
      )].sort();

      if (values.length === 0) return;

      const panelId = `filter-${key}`;
      const html = `
        <div>
          <button onclick="AIHub.toggleFilter('${panelId}', this)"
                  class="flex items-center justify-between w-full py-3 font-semibold
                         text-sm text-neutral-700 border-b border-gray-200">
            <span>${label}</span>
            <svg class="w-4 h-4 transition-transform duration-200 chevron-icon"
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="m6 9 6 6 6-6"/>
            </svg>
          </button>
          <div id="${panelId}" class="filter-panel expanded mt-3 space-y-2">
            ${values.map(v => `
              <label class="flex items-center gap-2 text-sm text-neutral-600
                            cursor-pointer hover:text-neutral-900">
                <input type="checkbox" value="${v}" class="rounded ${cls}"
                       onchange="AIHub.applyFilters()"/>
                <span>${v.charAt(0).toUpperCase() + v.slice(1)}</span>
              </label>
            `).join('')}
          </div>
        </div>
      `;
      container.insertAdjacentHTML('beforeend', html);
    });
  }

  // ---- Tabs (model detail page) ----
  function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabName);
      btn.classList.toggle('border-sky-500', btn.dataset.tab === tabName);
      btn.classList.toggle('text-sky-500', btn.dataset.tab === tabName);
      btn.classList.toggle('border-transparent', btn.dataset.tab !== tabName);
      btn.classList.toggle('text-neutral-400', btn.dataset.tab !== tabName);
    });
    const panel = document.getElementById(`tab-${tabName}`);
    if (panel) panel.classList.remove('hidden');
  }

  // ---- Login form ----
  function handleLogin(e) {
    e.preventDefault();
    const email    = document.getElementById('emailInput')?.value;
    const password = document.getElementById('passwordInput')?.value;
    const errEl    = document.getElementById('loginError');

    if (!email || !password) {
      if (errEl) { errEl.textContent = '請填寫信箱與密碼'; errEl.classList.remove('hidden'); }
      return;
    }

    // Submit form normally (server handles auth)
    e.target.submit();
  }

  // ---- Auto-init on DOMContentLoaded ----
  document.addEventListener('DOMContentLoaded', init);

  // Public API
  return {
    init,
    filterModels,
    applyFilters,
    clearFilters,
    sortModels,
    goPage,
    prevPage,
    nextPage,
    goLastPage,
    toggleMobileFilter,
    toggleFilter,
    switchTab,
    handleLogin,
  };
})();
