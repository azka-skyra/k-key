// Y-Key Frontend Logic - Vanilla JavaScript (no npm)

document.addEventListener('DOMContentLoaded', () => {
  loadProducts();
});

// ===== Load & Render Products =====
async function loadProducts() {
  try {
    const res = await fetch('/api/products');
    const data = await res.json();
    const products = data.products || [];

    const yogurtGrid = document.getElementById('yogurt-grid');
    const keychainGrid = document.getElementById('keychain-grid');

    const yogurts = products.filter(p => p.category === 'YOGURT');
    const keychains = products.filter(p => p.category === 'KEYCHAIN');

    yogurtGrid.innerHTML = yogurts.map(p => productCardHTML(p)).join('');
    keychainGrid.innerHTML = keychains.map(p => productCardHTML(p)).join('');
  } catch (err) {
    console.error('Failed to load products:', err);
  }
}

function productCardHTML(product) {
  const tags = (product.tags || '').split(',').filter(Boolean);
  const isBestSeller = tags.includes('best-seller');
  const category = product.category === 'YOGURT' ? '🍓 Yogurt' : '🏷️ Keychain';

  return `
    <div class="product-card">
      ${isBestSeller ? '<div class="btn-best-seller">⭐ BEST SELLER</div>' : ''}
      <div class="btn-category">${category}</div>
      <div class="product-image">${product.image}</div>
      <div class="product-info">
        <h3 class="product-name">${product.name}</h3>
        <p class="product-desc">${product.description}</p>
        <div class="product-tags">
          ${tags.slice(0, 2).map(t => `<span class="tag">${t}</span>`).join('')}
        </div>
      </div>
      <div class="product-footer">
        <span class="product-price">Rp${(product.price || 0).toLocaleString('id-ID')}</span>
        <span class="product-stock">stok: ${product.stock}</span>
      </div>
      <div class="product-actions">
        <button class="btn btn-primary btn-sm" onclick="quickOrder('${product.id}')" ${product.stock <= 0 ? 'disabled' : ''}>
          🛒 Pesan
        </button>
        <button class="btn btn-outline btn-sm" onclick="contactWA('${product.name}', ${product.price}, '${category}')">
          💬 WA
        </button>
      </div>
    </div>
  `;
}

// ===== Quick Order =====
async function quickOrder(productId) {
  try {
    const res = await fetch('/api/orders/quick', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productId, qty: 1 }),
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || 'Gagal membuat order', 'error');
      return;
    }
    showToast(`Pesanan dibuat! 🎉 Kode: ${data.order.code}`, 'success');
    setTimeout(() => {
      showToast(`💳 VA BCA: ${data.order.vaNumber} — Total Rp${data.order.total.toLocaleString('id-ID')}`, 'success');
    }, 1500);
  } catch (err) {
    showToast('Gagal terhubung ke server', 'error');
  }
}

// ===== WhatsApp Redirect =====
function contactWA(productName, price, category) {
  const msg = `Halo Y-Key! Aku mau pesan ${productName} (${category}). Harga Rp${price.toLocaleString('id-ID')}. Bisa dibantu?`;
  window.open(`https://wa.me/6281234567890?text=${encodeURIComponent(msg)}`, '_blank');
}

// ===== Toast Notification =====
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}