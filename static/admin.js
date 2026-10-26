// Y-Key Admin Dashboard Logic

let currentSection = 'dashboard';

document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
  loadStats();
});

async function checkAuth() {
  try {
    const res = await fetch('/api/admin/check');
    if (!res.ok) {
      window.location.href = '/login';
      return;
    }
    const data = await res.json();
    if (!data.authenticated) {
      window.location.href = '/login';
      return;
    }
    document.getElementById('admin-name').textContent = data.admin.name;
    document.getElementById('admin-username').textContent = '@' + data.admin.username;
  } catch {
    window.location.href = '/login';
  }
}

async function logout() {
  await fetch('/api/admin/logout', { method: 'DELETE' });
  window.location.href = '/login';
}

function showSection(section) {
  document.querySelectorAll('[id^="section-"]').forEach(el => el.style.display = 'none');
  document.getElementById('section-' + section).style.display = 'block';
  document.querySelectorAll('.admin-nav a').forEach(a => a.classList.remove('active'));
  event.target.classList.add('active');
  currentSection = section;

  if (section === 'dashboard') loadStats();
  else if (section === 'orders') loadOrders();
  else if (section === 'customers') loadCustomers();
  else if (section === 'products') loadProducts();
  else if (section === 'chats') loadChats();
}

// ===== STATS =====
async function loadStats() {
  try {
    const res = await fetch('/api/admin/stats');
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById('stats-grid').innerHTML = `
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--emerald);">💰</div>
        <div class="stat-label">Total Revenue</div>
        <div class="stat-value">Rp${(data.revenue.total || 0).toLocaleString('id-ID')}</div>
        <div class="stat-sub">dari order PAID+SHIPPED+DONE</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--blue);">👥</div>
        <div class="stat-label">Total Customer</div>
        <div class="stat-value">${data.counts.customers}</div>
        <div class="stat-sub">${data.counts.chats} sesi chat AI</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--pink-primary);">🛍️</div>
        <div class="stat-label">Total Order</div>
        <div class="stat-value">${data.counts.orders}</div>
        <div class="stat-sub">${data.revenue.PENDING || 0} pending payment</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--amber);">📦</div>
        <div class="stat-label">Total Produk</div>
        <div class="stat-value">${data.counts.products}</div>
        <div class="stat-sub">yogurt & keychain</div>
      </div>
    `;

    const total = (data.byCategory.YOGURT || 0) + (data.byCategory.KEYCHAIN || 0);
    document.getElementById('category-grid').innerHTML = `
      <div class="category-card">
        <div class="category-icon">🍓</div>
        <div class="category-label">Yogurt</div>
        <div class="category-count">${data.byCategory.YOGURT || 0} pcs</div>
        <div class="category-bar"><div class="category-bar-fill" style="width: ${total ? Math.round((data.byCategory.YOGURT / total) * 100) : 0}%"></div></div>
        <p style="font-size: 0.6875rem; color: var(--gray-light); margin-top: 0.5rem;">${total ? Math.round((data.byCategory.YOGURT / total) * 100) : 0}% dari total penjualan</p>
      </div>
      <div class="category-card">
        <div class="category-icon">🏷️</div>
        <div class="category-label">Keychain</div>
        <div class="category-count">${data.byCategory.KEYCHAIN || 0} pcs</div>
        <div class="category-bar"><div class="category-bar-fill" style="width: ${total ? Math.round((data.byCategory.KEYCHAIN / total) * 100) : 0}%"></div></div>
        <p style="font-size: 0.6875rem; color: var(--gray-light); margin-top: 0.5rem;">${total ? Math.round((data.byCategory.KEYCHAIN / total) * 100) : 0}% dari total penjualan</p>
      </div>
    `;

    document.getElementById('top-products').innerHTML = (data.topProducts || []).map((p, i) => `
      <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
        <div style="width: 36px; height: 36px; background: var(--gray-bg); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;">${p.image}</div>
        <div style="flex: 1;">
          <div style="font-size: 0.875rem; font-weight: 600;">${p.name}</div>
          <span class="tag">${p.category}</span>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 0.875rem; font-weight: 700; color: var(--pink-primary);">${p.qty} pcs</div>
          <div style="font-size: 0.625rem; color: var(--gray-light);">Rp${p.revenue.toLocaleString('id-ID')}</div>
        </div>
        ${i === 0 ? '<div style="color: var(--amber); font-size: 0.75rem; font-weight: 700;">#1</div>' : ''}
      </div>
    `).join('') || '<p style="text-align: center; color: var(--gray-light); padding: 1.5rem;">Belum ada penjualan</p>';

    document.getElementById('recent-orders').innerHTML = (data.recentOrders || []).map(o => `
      <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.625rem; border: 1px solid var(--border); border-radius: 12px; margin-bottom: 0.625rem;">
        <div style="width: 32px; height: 32px; background: var(--pink-light); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.875rem;">🛍️</div>
        <div style="flex: 1;">
          <div style="font-size: 0.875rem; font-weight: 600;">${o.customerName}</div>
          <div style="font-size: 0.6875rem; color: var(--gray-light);">${o.code}</div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 0.875rem; font-weight: 700;">Rp${o.total.toLocaleString('id-ID')}</div>
          <span class="status-badge status-${o.status}">${o.status}</span>
        </div>
      </div>
    `).join('') || '<p style="text-align: center; color: var(--gray-light); padding: 1.5rem;">Belum ada order</p>';
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

// ===== ORDERS =====
async function loadOrders() {
  const search = document.getElementById('order-search').value;
  const status = document.getElementById('order-status-filter').value;
  const category = document.getElementById('order-category-filter').value;
  const params = new URLSearchParams();
  if (status !== 'ALL') params.set('status', status);
  if (category !== 'ALL') params.set('category', category);
  if (search) params.set('search', search);

  try {
    const res = await fetch('/api/admin/orders?' + params.toString());
    if (res.status === 401) { window.location.href = '/login'; return; }
    const data = await res.json();
    document.getElementById('orders-count').textContent = data.count + ' order ditemukan';
    document.getElementById('orders-tbody').innerHTML = (data.orders || []).map(o => {
      const cats = new Set(o.items.map(it => it.category));
      const productBadges = [
        cats.has('YOGURT') ? '<span class="tag" style="background: #fee2e2; color: #991b1b;">🍓 Yogurt</span>' : '',
        cats.has('KEYCHAIN') ? '<span class="tag" style="background: #fef3c7; color: #92400e;">🏷️ Keychain</span>' : '',
      ].join(' ');
      return `
        <tr>
          <td><strong>${o.code}</strong><br><small style="color: var(--gray-light);">${o.items.length} item</small></td>
          <td>${o.customer.name}<br><small style="color: var(--gray-light);">${o.customer.whatsapp || ''}</small></td>
          <td>${productBadges}</td>
          <td><strong>Rp${o.total.toLocaleString('id-ID')}</strong></td>
          <td><span class="status-badge status-${o.status}">${o.status}</span></td>
          <td><small>${new Date(o.createdAt).toLocaleDateString('id-ID')}</small></td>
        </tr>
      `;
    }).join('') || '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--gray-light);">Belum ada order</td></tr>';
  } catch (err) {
    console.error('Failed to load orders:', err);
  }
}

// ===== CUSTOMERS =====
async function loadCustomers() {
  const search = document.getElementById('customer-search').value;
  const category = document.getElementById('customer-category-filter').value;
  const params = new URLSearchParams();
  if (category !== 'ALL') params.set('category', category);
  if (search) params.set('search', search);

  try {
    const res = await fetch('/api/admin/customers?' + params.toString());
    if (res.status === 401) { window.location.href = '/login'; return; }
    const data = await res.json();
    document.getElementById('customers-count').textContent = data.count + ' customer';
    document.getElementById('customers-grid').innerHTML = (data.customers || []).map(c => `
      <div class="stat-card">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
          <div style="width: 48px; height: 48px; background: var(--pink-light); color: var(--pink-primary); border-radius: 16px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.125rem; text-transform: uppercase;">${c.name.charAt(0)}</div>
          <div style="flex: 1; min-width: 0;">
            <div style="font-weight: 700; font-size: 0.875rem;">${c.name}</div>
            ${c.whatsapp ? `<div style="font-size: 0.6875rem; color: var(--gray-light);">💬 ${c.whatsapp}</div>` : ''}
          </div>
        </div>
        <div style="display: flex; gap: 0.25rem; margin-bottom: 0.75rem; flex-wrap: wrap;">
          ${c.categories.includes('YOGURT') ? `<span class="tag" style="background: #fee2e2; color: #991b1b;">🍓 Yogurt × ${c.yogurtQty}</span>` : ''}
          ${c.categories.includes('KEYCHAIN') ? `<span class="tag" style="background: #fef3c7; color: #92400e;">🏷️ Keychain × ${c.keychainQty}</span>` : ''}
          ${c.categories.length === 0 ? '<span class="tag">Belum ada order</span>' : ''}
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border);">
          <div><div style="font-size: 0.625rem; color: var(--gray-light); text-transform: uppercase;">Order</div><div style="font-weight: 700;">${c.ordersCount}</div></div>
          <div><div style="font-size: 0.625rem; color: var(--gray-light); text-transform: uppercase;">Total Belanja</div><div style="font-weight: 700; color: var(--pink-primary);">Rp${c.totalSpent.toLocaleString('id-ID')}</div></div>
        </div>
      </div>
    `).join('') || '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--gray-light);">Belum ada customer</div>';
  } catch (err) {
    console.error('Failed to load customers:', err);
  }
}

// ===== PRODUCTS =====
async function loadProducts() {
  try {
    const res = await fetch('/api/admin/products');
    if (res.status === 401) { window.location.href = '/login'; return; }
    const data = await res.json();
    document.getElementById('products-count').textContent = data.products.length + ' produk';
    document.getElementById('products-tbody').innerHTML = (data.products || []).map(p => {
      const tags = (p.tags || '').split(',').filter(Boolean);
      const isBestSeller = tags.includes('best-seller');
      const isLowStock = p.stock < 30;
      return `
        <tr>
          <td>
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <span style="font-size: 1.5rem;">${p.image}</span>
              <div>
                <div style="font-weight: 600;">${p.name} ${isBestSeller ? '⭐' : ''}</div>
                <small style="color: var(--gray-light);">${p.description}</small>
              </div>
            </div>
          </td>
          <td><span class="tag" style="background: ${p.category === 'YOGURT' ? '#fee2e2' : '#fef3c7'}; color: ${p.category === 'YOGURT' ? '#991b1b' : '#92400e'};">${p.category === 'YOGURT' ? '🍓 Yogurt' : '🏷️ Keychain'}</span></td>
          <td><strong>Rp${p.price.toLocaleString('id-ID')}</strong></td>
          <td style="color: ${isLowStock ? 'orange' : 'inherit'}; font-weight: ${isLowStock ? 700 : 400};">${p.stock} pcs</td>
          <td>${isLowStock ? '<span class="status-badge" style="background: #fed7aa; color: #9a3412;">⚠️ Stok Tipis</span>' : '<span class="status-badge status-PAID">✓ Tersedia</span>'}</td>
        </tr>
      `;
    }).join('') || '<tr><td colspan="5" style="text-align: center; padding: 2rem;">Belum ada produk</td></tr>';
  } catch (err) {
    console.error('Failed to load products:', err);
  }
}

// ===== CHATS =====
async function loadChats() {
  try {
    const res = await fetch('/api/admin/chats');
    if (res.status === 401) { window.location.href = '/login'; return; }
    const data = await res.json();
    document.getElementById('chats-grid').innerHTML = (data.sessions || []).map(s => `
      <div class="stat-card" onclick="openChat('${s.id}')" style="cursor: pointer;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
          <div style="width: 36px; height: 36px; background: var(--pink-light); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--pink-primary);">🤖</div>
          <div style="flex: 1; min-width: 0;">
            <div style="font-weight: 700; font-size: 0.875rem;">${s.customer?.name || s.visitorName || 'Anonymous'}</div>
            <div style="font-size: 0.6875rem; color: var(--gray-light);">${s.messageCount} pesan</div>
          </div>
          <span class="status-badge status-${s.status}">${s.status}</span>
        </div>
        <div style="background: var(--gray-bg); padding: 0.5rem; border-radius: 8px; font-size: 0.6875rem; color: var(--gray-light); font-style: italic;">"${s.lastMessage.substring(0, 80)}${s.lastMessage.length > 80 ? '...' : ''}"</div>
      </div>
    `).join('') || '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--gray-light);">Belum ada chat</div>';
  } catch (err) {
    console.error('Failed to load chats:', err);
  }
}

async function openChat(sessionId) {
  try {
    const res = await fetch('/api/admin/chats?sessionId=' + sessionId);
    const data = await res.json();
    const s = data.session;
    const messages = s.messages.map(m => `
      <div class="message ${m.role}">
        <div class="message-bubble">${m.content}</div>
      </div>
    `).join('');
    // Simple alert-based display (in real app, use modal)
    const win = window.open('', '_blank', 'width=500,height=700');
    win.document.write(`
      <html><head><title>Chat ${s.customer?.name || 'Anonymous'}</title>
      <link rel="stylesheet" href="/static/style.css"></head>
      <body style="padding: 1rem;">
        <h2>🤖 Chat dengan ${s.customer?.name || s.visitorName || 'Anonymous'}</h2>
        <p style="font-size: 0.75rem; color: var(--gray-light); margin-bottom: 1rem;">${s.messageCount || s.messages.length} pesan</p>
        <div class="chatbot-messages" style="background: var(--cream-bg); padding: 1rem; border-radius: 12px; height: 70vh; overflow-y: auto;">
          ${messages}
        </div>
        ${s.waNumber || s.customer?.whatsapp ? `<a href="https://wa.me/${s.waNumber || s.customer.whatsapp}" target="_blank" class="btn btn-emerald" style="margin-top: 1rem; width: 100%; justify-content: center;">💬 Lanjut via WhatsApp</a>` : ''}
      </body></html>
    `);
  } catch (err) {
    console.error('Failed to load chat:', err);
  }
}