document.addEventListener('DOMContentLoaded', () => {
  loadFilterOptions();
  refreshAllAnalytics();

  // Apply filters button
  document.getElementById('applyFiltersBtn').addEventListener('click', () => {
    refreshAllAnalytics();
  });

  // Reset filters button
  document.getElementById('resetFiltersBtn').addEventListener('click', () => {
    document.getElementById('filterRegion').value = '';
    document.getElementById('filterCategory').value = '';
    document.getElementById('filterChannel').value = '';
    document.getElementById('filterStartDate').value = '';
    document.getElementById('filterEndDate').value = '';
    refreshAllAnalytics();
  });

  // Run ad-hoc query button
  document.getElementById('runQueryBtn').addEventListener('click', executeAdhocSlice);
  document.getElementById('adhocDimension').addEventListener('change', executeAdhocSlice);
  document.getElementById('adhocMetric').addEventListener('change', executeAdhocSlice);

  // Export CSV
  document.getElementById('exportCsvBtn').addEventListener('click', handleExportCsv);

  // Sub Tab switching
  document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.sub-content').forEach(c => c.classList.remove('active'));

      e.target.classList.add('active');
      const targetSub = e.target.getAttribute('data-sub');
      document.getElementById(targetSub).classList.add('active');
    });
  });
});

function getActiveFilters() {
  return {
    region: document.getElementById('filterRegion').value,
    category: document.getElementById('filterCategory').value,
    channel: document.getElementById('filterChannel').value,
    start_date: document.getElementById('filterStartDate').value,
    end_date: document.getElementById('filterEndDate').value
  };
}

function buildQueryString(filters) {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v) params.append(k, v);
  }
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

async function loadFilterOptions() {
  try {
    const res = await fetch('/api/v1/metrics/filter-options');
    if (!res.ok) return;
    const data = await res.json();

    const regSelect = document.getElementById('filterRegion');
    data.regions.forEach(r => {
      const opt = document.createElement('option');
      opt.value = r;
      opt.textContent = r;
      regSelect.appendChild(opt);
    });

    const catSelect = document.getElementById('filterCategory');
    data.categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      catSelect.appendChild(opt);
    });

    const chanSelect = document.getElementById('filterChannel');
    data.channels.forEach(ch => {
      const opt = document.createElement('option');
      opt.value = ch;
      opt.textContent = ch;
      chanSelect.appendChild(opt);
    });
  } catch (err) {
    console.error('Failed to load filter options:', err);
  }
}

async function refreshAllAnalytics() {
  const filters = getActiveFilters();
  await Promise.all([
    fetchKpis(filters),
    fetchTrends(filters),
    fetchCategories(filters),
    fetchRegions(filters),
    executeAdhocSlice()
  ]);
}

async function fetchKpis(filters) {
  try {
    const res = await fetch(`/api/v1/metrics/kpis${buildQueryString(filters)}`);
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById('kpiRevenue').textContent = formatCurrency(data.total_revenue);
    document.getElementById('kpiRevenueSub').textContent = `${data.total_orders} Total Orders`;
    document.getElementById('kpiProfit').textContent = formatCurrency(data.total_profit);
    document.getElementById('kpiMargin').textContent = `${data.blended_margin_pct.toFixed(1)}%`;
    document.getElementById('kpiAOV').textContent = formatCurrency(data.avg_order_value);
    document.getElementById('kpiVolume').textContent = `${data.total_units.toLocaleString()} units`;
    document.getElementById('kpiCustomers').textContent = `${data.unique_customers} Unique Customers`;
  } catch (err) {
    console.error('Failed to fetch KPIs:', err);
  }
}

async function fetchTrends(filters) {
  try {
    const res = await fetch(`/api/v1/metrics/trends${buildQueryString(filters)}`);
    if (!res.ok) return;
    const trends = await res.json();
    const tbody = document.getElementById('trendsTableBody');

    if (!trends || trends.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="text-dim">No transactions in selected range.</td></tr>';
      return;
    }

    tbody.innerHTML = trends.map(t => `
      <tr>
        <td><code>${t.date}</code></td>
        <td class="text-right text-emerald">${formatCurrency(t.revenue)}</td>
        <td class="text-right text-blue">${formatCurrency(t.profit)}</td>
        <td class="text-right">${t.units}</td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Failed to fetch trends:', err);
  }
}

async function fetchCategories(filters) {
  try {
    const res = await fetch(`/api/v1/metrics/categories${buildQueryString(filters)}`);
    if (!res.ok) return;
    const cats = await res.json();
    const tbody = document.getElementById('categoriesTableBody');

    if (!cats || cats.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="text-dim">No category data available.</td></tr>';
      return;
    }

    tbody.innerHTML = cats.map(c => `
      <tr>
        <td><strong>${escapeHtml(c.category)}</strong></td>
        <td class="text-right text-emerald">${formatCurrency(c.revenue)}</td>
        <td class="text-right text-gold">${c.margin_pct.toFixed(1)}%</td>
        <td class="text-right">${c.orders}</td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Failed to fetch categories:', err);
  }
}

async function fetchRegions(filters) {
  try {
    const res = await fetch(`/api/v1/metrics/regions${buildQueryString(filters)}`);
    if (!res.ok) return;
    const regions = await res.json();
    const tbody = document.getElementById('regionsTableBody');

    if (!regions || regions.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="text-dim">No regional data available.</td></tr>';
      return;
    }

    tbody.innerHTML = regions.map(r => `
      <tr>
        <td><strong>${escapeHtml(r.region)}</strong></td>
        <td class="text-right text-emerald">${formatCurrency(r.revenue)}</td>
        <td class="text-right text-blue">${formatCurrency(r.profit)}</td>
        <td class="text-right">${formatCurrency(r.avg_order_value)}</td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Failed to fetch regions:', err);
  }
}

async function executeAdhocSlice() {
  const dim = document.getElementById('adhocDimension').value;
  const metric = document.getElementById('adhocMetric').value;
  const filters = getActiveFilters();

  document.getElementById('thDimension').textContent = `Dimension: ${dim.toUpperCase()}`;
  document.getElementById('thMetric').textContent = `Metric: ${metric.toUpperCase()}`;

  const payload = {
    dimension: dim,
    metric: metric,
    region: filters.region || null,
    category: filters.category || null,
    channel: filters.channel || null,
    start_date: filters.start_date || null,
    end_date: filters.end_date || null,
    sort: 'DESC'
  };

  try {
    const res = await fetch('/api/v1/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) return;
    const results = await res.json();
    const tbody = document.getElementById('adhocTableBody');

    if (!results || results.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="text-dim">No records matching active slice.</td></tr>';
      return;
    }

    tbody.innerHTML = results.map(row => {
      let metricFormatted = row.metric_value;
      if (metric === 'revenue' || metric === 'profit' || metric === 'avg_order_value') {
        metricFormatted = formatCurrency(row.metric_value);
      } else if (metric === 'avg_margin') {
        metricFormatted = `${row.metric_value.toFixed(1)}%`;
      } else {
        metricFormatted = row.metric_value.toLocaleString();
      }

      return `
        <tr>
          <td><strong>${escapeHtml(row.dimension_value || 'Unassigned')}</strong></td>
          <td class="text-right text-emerald">${metricFormatted}</td>
          <td class="text-right">${row.transaction_count}</td>
          <td class="text-right">${formatCurrency(row.total_revenue)}</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Ad-hoc query failed:', err);
  }
}

function handleExportCsv() {
  const filters = getActiveFilters();
  const url = `/api/v1/export/csv${buildQueryString(filters)}`;
  window.location.href = url;
}

function formatCurrency(val) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(val || 0);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
