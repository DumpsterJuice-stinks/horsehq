// ========================
// The Horse HQ — App Logic
// ========================

const CATEGORIES = [
  { name: 'Founding Farms' },
  { name: 'Racing Quarter Horse' },
  { name: 'Racing Thoroughbred' },
  { name: 'Yearlings' },
  { name: 'Member Stallions' },
  { name: 'Roping/Rodeo Horses' },
  { name: 'Ranch Horses' },
  { name: 'Horses Under 3k' },
  { name: 'Hay' },
  { name: 'Transporters' },
  { name: 'Horse Trailers' },
  { name: 'Training Equipment' },
  { name: 'Art' }
];

const MAX_BUNDLE_SLOTS = 4;

const STRIPE_LINKS = {
  standard: 'https://buy.stripe.com/dRmbJ05an5FfdC139U6Vq01',
  bundle: 'https://buy.stripe.com/cNiaEWauH3x71TjfWG6Vq05',
  boost: 'https://buy.stripe.com/aFaaEWbyLaZz2Xn25Q6Vq04',
  featured: 'https://buy.stripe.com/aFaaEWdGTaZz1Tj25Q6Vq03',
  adSlot: 'https://buy.stripe.com/7sY5kCdGTc3DbtT7qa6Vq02',
  stallion: 'https://buy.stripe.com/7sYfZg32f2t3dC1bGq6Vq06'
};

let allListings = [];
let currentCategory = '';
let lastSubmittedListingIds = [];
let submitMode = 'standard';

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
  loadListings();
  populateCategoryDropdowns();
  renderCategories();
  renderFeatured();
  renderAllListings();
  renderStallions();

  // Support deep links like thehorsehq.com/#submit from outside pages (e.g. the blog)
  const entryPage = location.hash.replace('#', '');
  const linkablePages = ['home', 'listings', 'stallions', 'submit-stallion', 'submit', 'pricing'];
  if (linkablePages.includes(entryPage)) showPage(entryPage);
});

// ---- DATA ----
async function loadListings() {
  try {
    const stored = localStorage.getItem('thehorsehq_listings');
    if (stored) {
      allListings = JSON.parse(stored);
    } else {
      const res = await fetch('data/listings.json');
      allListings = res.ok ? await res.json() : [];
    }
  } catch {
    allListings = [];
  }
  renderCategories();
  renderFeatured();
  renderAllListings();
  renderStallions();
}

function persistListings() {
  try {
    localStorage.setItem('thehorsehq_listings', JSON.stringify(allListings));
  } catch {}
}

function isCurrentlyFeatured(listing) {
  if (!listing.featured) return false;
  if (!listing.featuredUntil) return true;
  return listing.featuredUntil >= new Date().toISOString().split('T')[0];
}

function isExpired(listing) {
  if (!listing.expiresAt) return false;
  return listing.expiresAt < new Date().toISOString().split('T')[0];
}

// ---- PAGE NAVIGATION ----
function showPage(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById(`page-${page}`);
  if (target) target.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  // Re-render listings when navigating
  if (page === 'listings') renderAllListings();
  if (page === 'stallions') renderStallions();
}

function showCategoryPage(category) {
  currentCategory = category;
  showPage('category');
  document.getElementById('categoryTitle').textContent = category;
  renderCategoryListings(category);
}

function renderCategoryListings(category) {
  const grid = document.getElementById('categoryGrid');
  const filtered = allListings
    .filter(l => l.category === category && !isExpired(l))
    .sort((a, b) => (b.boosted ? 1 : 0) - (a.boosted ? 1 : 0) || new Date(b.date) - new Date(a.date));
  grid.innerHTML = filtered.length
    ? filtered.map(l => makeCard(l)).join('')
    : `<div class="no-results"><p>No listings in this category yet.</p></div>`;
}

function toggleMobileMenu() {
  document.getElementById('mobileNav').classList.toggle('open');
}

// ---- RENDER CATEGORIES ----
function categoryNav(name) {
  return name === 'Member Stallions' ? `showPage('stallions')` : `showCategoryPage('${name}')`;
}

function renderCategories() {
  const counts = {};
  CATEGORIES.forEach(c => counts[c.name] = 0);
  allListings.forEach(l => { if (counts[l.category] !== undefined && !isExpired(l)) counts[l.category]++; });

  const grid = document.getElementById('categoriesGrid');
  if (grid) {
    grid.innerHTML = CATEGORIES.map(c => `
      <a class="category-list-item" href="#" onclick="${categoryNav(c.name)}; return false;">${c.name} <span class="category-list-count">${counts[c.name] || 0}</span></a>
    `).join('');
  }

  const panelList = document.getElementById('categoriesPanelList');
  if (panelList) {
    panelList.innerHTML = CATEGORIES.map(c => `
      <a class="categories-panel-item" href="#" onclick="closeCategoriesPanel(); ${categoryNav(c.name)}; return false;">
        <span>${c.name}</span>
        <span class="categories-panel-count">${counts[c.name] || 0}</span>
      </a>
    `).join('');
  }
}

function openCategoriesPanel() {
  document.getElementById('categoriesPanel').classList.add('open');
  document.getElementById('categoriesPanelOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeCategoriesPanel() {
  document.getElementById('categoriesPanel').classList.remove('open');
  document.getElementById('categoriesPanelOverlay').classList.remove('open');
  document.body.style.overflow = '';
}

// ---- RENDER MEMBER STALLIONS ----
let stallionSearchTerm = '';

function renderStallions() {
  const grid = document.getElementById('stallionsGrid');
  if (!grid) return;

  let filtered = allListings.filter(l => l.category === 'Member Stallions' && !isExpired(l));

  if (stallionSearchTerm) {
    const term = stallionSearchTerm.toLowerCase();
    filtered = filtered.filter(l =>
      (l.title && l.title.toLowerCase().includes(term)) ||
      (l.sire && l.sire.toLowerCase().includes(term)) ||
      (l.dam && l.dam.toLowerCase().includes(term))
    );
  }

  filtered = filtered.sort((a, b) => (b.boosted ? 1 : 0) - (a.boosted ? 1 : 0) || new Date(b.date) - new Date(a.date));

  const banner = stallionSearchTerm
    ? `<div class="stallion-search-banner">Showing horses related to "<strong>${stallionSearchTerm}</strong>" — <a href="#" onclick="clearStallionSearch(); return false;">Clear search</a></div>`
    : '';

  grid.innerHTML = banner + (filtered.length
    ? filtered.map(l => makeCard(l)).join('')
    : `<div class="no-results"><p>No standing stallions found${stallionSearchTerm ? ' for this search' : ' yet'}. <a href="#" onclick="showPage('submit-stallion');return false;" style="color:var(--green)">Be the first →</a></p></div>`);
}

function searchPedigreeName(name) {
  if (!name) return;
  stallionSearchTerm = name;
  closeModal();
  showPage('stallions');
}

function clearStallionSearch() {
  stallionSearchTerm = '';
  renderStallions();
}

function escAttr(str) {
  return String(str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

// ---- PEDIGREE TREE ----
const PED_LINK_ICON = '<svg class="ped-icon" viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="3"><path d="M7 17L17 7M9 7h8v8"/></svg>';

function pedNode(name, extraClass) {
  const cls = extraClass ? ` ${extraClass}` : '';
  if (!name) return `<span class="ped-node${cls} ped-empty">—</span>`;
  return `<button type="button" class="ped-node${cls}" onclick="searchPedigreeName('${escAttr(name)}')">${name}${PED_LINK_ICON}</button>`;
}

// gen1: [nameA, nameB]; gen2: [[gp for A, gp for A], [gp for B, gp for B]] — only rendered if any entry present
function pedBranch(label, rootName, gen1, gen2) {
  const hasGen1 = !!(gen1 && (gen1[0] || gen1[1]));
  const hasGen2 = !!(gen2 && gen2.some(pair => pair[0] || pair[1]));

  let inner;
  if (!hasGen1) {
    inner = pedNode(rootName, 'ped-root');
  } else if (!hasGen2) {
    inner = `
      ${pedNode(rootName, 'ped-root ped-linked')}
      <div class="ped-fork">
        ${pedNode(gen1[0])}
        ${pedNode(gen1[1])}
      </div>
    `;
  } else {
    inner = `
      ${pedNode(rootName, 'ped-root ped-linked')}
      <div class="ped-fork ped-fork-deep">
        <div class="ped-item">
          ${pedNode(gen1[0], 'ped-linked')}
          <div class="ped-fork">${pedNode(gen2[0][0])}${pedNode(gen2[0][1])}</div>
        </div>
        <div class="ped-item">
          ${pedNode(gen1[1], 'ped-linked')}
          <div class="ped-fork">${pedNode(gen2[1][0])}${pedNode(gen2[1][1])}</div>
        </div>
      </div>
    `;
  }

  return `
    <div class="ped-branch-block">
      <span class="ped-branch-label">${label}</span>
      <div class="ped-branch">${inner}</div>
    </div>
  `;
}

// ---- RENDER FEATURED ----
function renderFeatured() {
  const featured = allListings.filter(l => isCurrentlyFeatured(l) && !isExpired(l));
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;
  grid.innerHTML = featured.length
    ? featured.map(l => makeCard(l)).join('')
    : '<p style="color:var(--gray-400);font-size:14px;">No featured listings yet. <a href="#" onclick="showPage(\'submit\');return false;" style="color:var(--green)">Be the first →</a></p>';
}

// ---- RENDER ALL LISTINGS ----
function renderAllListings() {
  const grid = document.getElementById('allListingsGrid');
  if (!grid) return;

  const catFilter = document.getElementById('categoryFilter');
  const sortFilter = document.getElementById('sortFilter');

  let filtered = allListings.filter(l => !isExpired(l));

  const catVal = catFilter ? catFilter.value : '';
  if (catVal) filtered = filtered.filter(l => l.category === catVal);

  const sortVal = sortFilter ? sortFilter.value : 'newest';
  if (sortVal === 'newest') filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
  else if (sortVal === 'price-asc') filtered.sort((a, b) => a.price - b.price);
  else if (sortVal === 'price-desc') filtered.sort((a, b) => b.price - a.price);
  else if (sortVal === 'featured') filtered.sort((a, b) => (isCurrentlyFeatured(b) ? 1 : 0) - (isCurrentlyFeatured(a) ? 1 : 0));

  grid.innerHTML = filtered.length
    ? filtered.map(l => makeCard(l)).join('')
    : `<div class="no-results"><p>No listings found. <a href="#" onclick="showPage('submit');return false;" style="color:var(--green)">Submit the first →</a></p></div>`;
}

function filterListings() {
  renderAllListings();
}

// ---- PRICE FORMATTING ----
function formatPrice(listing) {
  const price = listing.price < 100
    ? `$${listing.price.toFixed(listing.price % 1 === 0 ? 0 : 2)}`
    : `$${listing.price.toLocaleString()}`;

  let suffix = '';
  if (listing.category === 'Member Stallions') suffix = ' / stud fee';
  else if (listing.price < 100) suffix = ' / bale or / mile';

  return { price, suffix };
}

// ---- MAKE LISTING CARD ----
function makeCard(listing) {
  const { price, suffix } = formatPrice(listing);
  const date = new Date(listing.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const featuredClass = isCurrentlyFeatured(listing) ? ' featured' : '';
  const foundingClass = listing.founding ? ' founding' : '';

  return `
    <div class="listing-card${featuredClass}${foundingClass}" onclick="openDetail(${listing.id})">
      <img class="card-image" src="${listing.image}" alt="${listing.title}" loading="lazy" onerror="this.style.display='none'">
      <div class="card-body">
        <div class="card-category">${listing.category}</div>
        <div class="card-title">${listing.title}</div>
        <div class="card-meta">${listing.location} &nbsp;·&nbsp; ${date}</div>
        <div class="card-price">${price}${suffix ? ` <small>${suffix}</small>` : ''}</div>
        <div class="card-desc">${listing.description}</div>
        <div class="card-footer">
          <span class="card-seller">${listing.seller}</span>
          <span class="card-date">${date}</span>
        </div>
      </div>
    </div>
  `;
}

// ---- DETAIL MODAL ----
async function openDetail(id) {
  // Find listing in current data
  const listing = allListings.find(l => l.id === id);
  if (!listing) return;

  const { price, suffix } = formatPrice(listing);
  const isStallion = listing.category === 'Member Stallions';

  const modal = document.getElementById('detailModal');
  const content = document.getElementById('modalContent');

  const stallionMetaItems = isStallion ? `
        <div class="modal-meta-item">
          <label>Breed / Registry</label>
          <span>${listing.breed || '—'}</span>
        </div>
        ${listing.registrationNumber ? `<div class="modal-meta-item"><label>Registration #</label><span>${listing.registrationNumber}</span></div>` : ''}
        <div class="modal-meta-item">
          <label>Color</label>
          <span>${listing.color || '—'}</span>
        </div>
        ${listing.height ? `<div class="modal-meta-item"><label>Height</label><span>${listing.height}</span></div>` : ''}
        ${listing.foalYear ? `<div class="modal-meta-item"><label>Foal Year</label><span>${listing.foalYear}</span></div>` : ''}
        ${listing.discipline ? `<div class="modal-meta-item"><label>Discipline</label><span>${listing.discipline}</span></div>` : ''}
  ` : '';

  const pedigreeTree = isStallion ? `
      <div class="modal-stallion-block">
        <h4>Pedigree</h4>
        <div class="pedigree-branches">
          ${pedBranch('Sire', listing.sire,
            [listing.sireSire, listing.sireDam],
            [[listing.sireSireSire, listing.sireSireDam], [listing.sireDamSire, listing.sireDamDam]])}
          ${pedBranch('Dam', listing.dam,
            [listing.damSire, listing.damDam],
            [[listing.damSireSire, listing.damSireDam], [listing.damDamSire, listing.damDamDam]])}
        </div>
      </div>
  ` : '';

  const stallionRecordBlocks = isStallion ? `
      ${listing.pedigree ? `<div class="modal-stallion-block"><h4>Pedigree Highlights</h4><p>${listing.pedigree}</p></div>` : ''}
      ${listing.progenyEarnings ? `<div class="modal-stallion-block"><h4>Progeny Earnings / Achievements</h4><p>${listing.progenyEarnings}</p></div>` : ''}
      ${listing.topProgeny ? `<div class="modal-stallion-block"><h4>Top Progeny</h4><p>${listing.topProgeny}</p></div>` : ''}
      ${listing.lifetimeEarnings ? `<div class="modal-stallion-block"><h4>Lifetime Earnings (Own Performance)</h4><p>${listing.lifetimeEarnings}</p></div>` : ''}
      ${listing.video ? `<div class="modal-stallion-block"><h4>Video</h4><p><a href="${listing.video}" target="_blank" rel="noopener">${listing.video}</a></p></div>` : ''}
      ${listing.documents ? `<div class="modal-stallion-block"><h4>Documents</h4><p><a href="${listing.documents}" target="_blank" rel="noopener">View documents →</a></p></div>` : ''}
  ` : '';

  const imagesHtml = listing.image2
    ? `<div class="modal-image-gallery">
         <img class="modal-image modal-image-half" src="${listing.image}" alt="${listing.title}" onerror="this.style.display='none'">
         <img class="modal-image modal-image-half" src="${listing.image2}" alt="${listing.title}" onerror="this.style.display='none'">
       </div>`
    : `<img class="modal-image" src="${listing.image}" alt="${listing.title}" onerror="this.style.display='none'">`;

  content.innerHTML = `
    ${imagesHtml}
    <div class="modal-body">
      ${isCurrentlyFeatured(listing) ? '<span style="display:inline-block;background:var(--green);color:#fff;font-size:11px;font-weight:700;padding:3px 12px;border-radius:20px;margin-bottom:12px;margin-right:6px;">Featured Listing</span>' : ''}
      ${listing.founding ? '<span style="display:inline-block;background:#d97706;color:#fff;font-size:11px;font-weight:700;padding:3px 12px;border-radius:20px;margin-bottom:12px;">Founding Partner</span>' : ''}
      <div class="modal-category">${listing.category}</div>
      <h2 class="modal-title">${listing.title}</h2>
      <div class="modal-price">${price}${suffix ? `<small>${suffix}</small>` : ''}</div>
      <p class="modal-desc">${listing.description}</p>
      <div class="modal-meta-grid">
        <div class="modal-meta-item">
          <label>Location</label>
          <span>${listing.location}</span>
        </div>
        <div class="modal-meta-item">
          <label>Seller</label>
          <span>${listing.seller}</span>
        </div>
        <div class="modal-meta-item">
          <label>Listed</label>
          <span>${new Date(listing.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
        </div>
        <div class="modal-meta-item">
          <label>Category</label>
          <span>${listing.category}</span>
        </div>
        ${stallionMetaItems}
      </div>
      ${pedigreeTree}
      ${stallionRecordBlocks}
      <div class="modal-contact">
        <h3>${isStallion ? 'Inquire About This Stallion' : 'Contact Seller'}</h3>
        <div class="modal-contact-item"><strong>Email:</strong> <a href="mailto:${listing.email}">${listing.email}</a></div>
        ${(!isStallion && listing.phone) ? `<div class="modal-contact-item"><strong>Phone:</strong> <a href="tel:${listing.phone.replace(/\D/g,'')}">${listing.phone}</a></div>` : ''}
        <p style="font-size:12px;color:var(--gray-500);margin-top:12px;">${isStallion ? 'Member Stallions are available by email inquiry only.' : 'Mention you saw this listing on TheHorseHQ.com'}</p>
      </div>
    </div>
  `;

  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal(e) {
  if (e && e.target !== e.currentTarget) return;
  document.getElementById('detailModal').classList.remove('open');
  document.body.style.overflow = '';
}

function closeSuccessModal(e) {
  if (e && e.target !== e.currentTarget) return;
  document.getElementById('successModal').classList.remove('open');
  document.body.style.overflow = '';
}

// ---- FORM: CATEGORY DROPDOWNS ----
function populateCategoryDropdowns() {
  const filterSelect = document.getElementById('categoryFilter');
  if (filterSelect) {
    const currentVal = filterSelect.value;
    filterSelect.innerHTML = `<option value="">All Categories</option>` +
      CATEGORIES.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
    if (currentVal) filterSelect.value = currentVal;
  }

  const submittableCategories = CATEGORIES.filter(c => c.name !== 'Member Stallions');
  document.querySelectorAll('.s-category').forEach(sel => {
    const currentVal = sel.value;
    sel.innerHTML = `<option value="">Select category…</option>` +
      submittableCategories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
    if (currentVal) sel.value = currentVal;
  });
}

// ---- FORM: SUBMIT MODE (Standard / Bundle) ----
function setSubmitMode(mode) {
  submitMode = mode;
  document.getElementById('modeStandardBtn').classList.toggle('active', mode === 'standard');
  document.getElementById('modeBundleBtn').classList.toggle('active', mode === 'bundle');
  document.getElementById('modeFreeBtn').classList.toggle('active', mode === 'free');

  if (mode !== 'bundle') {
    document.querySelectorAll('#listingSlots .listing-slot').forEach((slot, i) => {
      if (i > 0) slot.remove();
    });
  }

  const secondImageGroup = document.getElementById('secondImageGroup');
  if (secondImageGroup) secondImageGroup.style.display = mode === 'free' ? '' : 'none';

  updateSlotUI();
  updateFormTotal();
}

function updateFormTotal() {
  const el = document.getElementById('formTotal');
  if (submitMode === 'bundle') {
    el.innerHTML = `Total: <strong>$160</strong>`;
  } else if (submitMode === 'free') {
    el.innerHTML = `Total: <strong>Free</strong> <small>(9-day listing, 2 photos max)</small>`;
  } else {
    el.innerHTML = `Total: <strong>$50</strong>`;
  }
}

function slotTemplate(index) {
  return `
    <div class="listing-slot" data-slot="${index}">
      <div class="listing-slot-header">
        <h3>Listing ${index + 1}</h3>
        <button type="button" class="remove-slot-btn" onclick="removeListingSlot(this)">Remove</button>
      </div>

      <div class="form-group">
        <label>Listing Title *</label>
        <input type="text" class="s-title" placeholder="e.g. Flashy Kid — Registered AQHA Bay Roan Gelding" required>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Price ($) *</label>
          <input type="number" class="s-price" placeholder="18500" min="0" required>
        </div>
        <div class="form-group">
          <label>Category *</label>
          <select class="s-category" required></select>
        </div>
      </div>

      <div class="form-group">
        <label>Location *</label>
        <input type="text" class="s-location" placeholder="City, State" required>
      </div>

      <div class="form-group">
        <label>Description *</label>
        <textarea class="s-description" rows="4" placeholder="Describe your horse/item in detail." required></textarea>
      </div>

      <div class="form-group">
        <label>Photo URL</label>
        <input type="url" class="s-image" placeholder="https://example.com/horse.jpg">
      </div>
    </div>
  `;
}

function addListingSlot() {
  const container = document.getElementById('listingSlots');
  const slots = container.querySelectorAll('.listing-slot');
  if (slots.length >= MAX_BUNDLE_SLOTS) return;

  const wrapper = document.createElement('div');
  wrapper.innerHTML = slotTemplate(slots.length).trim();
  container.appendChild(wrapper.firstElementChild);

  populateCategoryDropdowns();
  updateSlotUI();
}

function removeListingSlot(btn) {
  btn.closest('.listing-slot').remove();
  updateSlotUI();
}

function updateSlotUI() {
  const slots = document.querySelectorAll('#listingSlots .listing-slot');
  slots.forEach((slot, i) => {
    slot.querySelector('h3').textContent = `Listing ${i + 1}`;
    slot.dataset.slot = i;
    const removeBtn = slot.querySelector('.remove-slot-btn');
    removeBtn.style.display = (submitMode === 'bundle' && slots.length > 1) ? '' : 'none';
  });

  const addBtn = document.getElementById('addSlotBtn');
  addBtn.style.display = (submitMode === 'bundle' && slots.length < MAX_BUNDLE_SLOTS) ? '' : 'none';
}

function resetSubmitForm() {
  document.getElementById('submitForm').reset();
  document.querySelectorAll('#listingSlots .listing-slot').forEach((slot, i) => {
    if (i > 0) slot.remove();
  });
  setSubmitMode('standard');
}

// ---- SUCCESS MODAL UPSELL TARGET ----
function populateUpsellTarget() {
  const group = document.getElementById('upsellTargetGroup');
  const select = document.getElementById('upsellTarget');

  if (lastSubmittedListingIds.length <= 1) {
    group.style.display = 'none';
    return;
  }

  group.style.display = 'block';
  select.innerHTML = lastSubmittedListingIds.map(id => {
    const l = allListings.find(x => x.id === id);
    return `<option value="${id}">${l.title}</option>`;
  }).join('');
}

function onUpsellTargetChange() {
  refreshUpsellButtonsForTarget();
}

function getUpsellTargetId() {
  if (lastSubmittedListingIds.length <= 1) return lastSubmittedListingIds[0];
  const select = document.getElementById('upsellTarget');
  return select ? Number(select.value) : lastSubmittedListingIds[0];
}

function refreshUpsellButtonsForTarget() {
  const listing = allListings.find(l => l.id === getUpsellTargetId());
  const boostBtn = document.getElementById('boostBtn');
  const featureBtn = document.getElementById('featureBtn');
  if (!listing || !boostBtn || !featureBtn) return;

  if (listing.boosted) {
    boostBtn.disabled = true;
    boostBtn.classList.add('upsell-btn-active');
    boostBtn.querySelector('.upsell-btn-title').textContent = 'Boosted';
    boostBtn.querySelector('.upsell-btn-desc').textContent = `Now at the top of ${listing.category}`;
  } else {
    boostBtn.disabled = false;
    boostBtn.classList.remove('upsell-btn-active');
    boostBtn.querySelector('.upsell-btn-title').textContent = 'Boost — $30';
    boostBtn.querySelector('.upsell-btn-desc').textContent = 'Jump to the top of your category';
  }

  if (isCurrentlyFeatured(listing)) {
    featureBtn.disabled = true;
    featureBtn.classList.add('upsell-btn-active');
    featureBtn.querySelector('.upsell-btn-title').textContent = 'Featured';
    featureBtn.querySelector('.upsell-btn-desc').textContent = 'Live on homepage for 7 days';
  } else {
    featureBtn.disabled = false;
    featureBtn.classList.remove('upsell-btn-active');
    featureBtn.querySelector('.upsell-btn-title').textContent = 'Get Featured — $200';
    featureBtn.querySelector('.upsell-btn-desc').textContent = 'Homepage placement for 7 days';
  }
}

function purchaseBoost() {
  const listing = allListings.find(l => l.id === getUpsellTargetId());
  if (!listing || listing.boosted) return;

  listing.boosted = true;
  listing.boostedAt = Date.now();
  persistListings();
  refreshUpsellButtonsForTarget();

  renderAllListings();
  if (currentCategory === listing.category) renderCategoryListings(currentCategory);

  window.open(STRIPE_LINKS.boost, '_blank', 'noopener');
}

function purchaseFeature() {
  const listing = allListings.find(l => l.id === getUpsellTargetId());
  if (!listing) return;

  const until = new Date();
  until.setDate(until.getDate() + 7);
  listing.featured = true;
  listing.featuredUntil = until.toISOString().split('T')[0];
  persistListings();
  refreshUpsellButtonsForTarget();

  renderFeatured();
  renderAllListings();

  window.open(STRIPE_LINKS.featured, '_blank', 'noopener');
}

// ---- SUBMIT ----
// ---- NETLIFY FORMS NOTIFICATION ----
function notifyNetlifyForm(formName, fields) {
  const body = new URLSearchParams({ 'form-name': formName, ...fields }).toString();
  fetch('/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body
  }).catch(() => {});
}

// ---- NEWSLETTER / NEW LISTINGS DIGEST ----
function subscribeDigest(e) {
  e.preventDefault();

  const emailInput = document.getElementById('digest-email');
  const email = emailInput.value.trim();
  const note = document.getElementById('digestNote');

  if (!email) return;

  notifyNetlifyForm('digest-signup', { email });

  note.textContent = "You're on the list — thanks!";
  document.getElementById('digestForm').reset();
}

function submitListing(e) {
  e.preventDefault();

  const sellerName = document.getElementById('s-name').value.trim();
  const sellerEmail = document.getElementById('s-email').value.trim();
  const sellerPhone = document.getElementById('s-phone').value.trim();

  if (!sellerName || !sellerEmail) {
    alert('Please fill in your name and email.');
    return;
  }

  const isFree = submitMode === 'free';

  let expiresAt = null;
  if (isFree) {
    const expiry = new Date();
    expiry.setDate(expiry.getDate() + 9);
    expiresAt = expiry.toISOString().split('T')[0];
  }

  const slots = [...document.querySelectorAll('#listingSlots .listing-slot')];
  const newListings = [];

  for (const slot of slots) {
    const title = slot.querySelector('.s-title').value.trim();
    const price = parseFloat(slot.querySelector('.s-price').value);
    const category = slot.querySelector('.s-category').value;
    const location = slot.querySelector('.s-location').value.trim();
    const description = slot.querySelector('.s-description').value.trim();
    const image = slot.querySelector('.s-image').value.trim();
    const image2Field = isFree ? slot.querySelector('.s-image-2') : null;
    const image2 = image2Field ? image2Field.value.trim() : '';

    if (!title || !price || !category || !location || !description) {
      alert('Please fill in all required fields for each listing.');
      return;
    }

    newListings.push({
      id: Date.now() + newListings.length,
      title,
      price,
      category,
      location,
      description,
      image: image || 'https://placehold.co/600x400/16a34a/ffffff?text=No+Photo',
      image2: image2 || null,
      featured: false,
      boosted: false,
      free: isFree,
      expiresAt,
      seller: sellerName,
      email: sellerEmail,
      phone: sellerPhone,
      date: new Date().toISOString().split('T')[0]
    });
  }

  // Add to local array, preserving slot order at the top
  [...newListings].reverse().forEach(l => allListings.unshift(l));
  lastSubmittedListingIds = newListings.map(l => l.id);
  persistListings();

  // Email the full submission to the site owner via Netlify Forms
  const listingsSummary = newListings.map((l, i) =>
    `Listing ${i + 1}: ${l.title} — $${l.price} (${l.category})\nLocation: ${l.location}\nDescription: ${l.description}\nPhoto 1: ${l.image}\nPhoto 2: ${l.image2 || '(none)'}${l.expiresAt ? `\nExpires: ${l.expiresAt}` : ''}`
  ).join('\n\n---\n\n');
  notifyNetlifyForm('listing-submission', {
    'seller-name': sellerName,
    'seller-email': sellerEmail,
    'seller-phone': sellerPhone,
    'mode': submitMode,
    'listings-summary': listingsSummary
  });

  // Capture before resetSubmitForm() reverts it to 'standard'
  const stripeLink = submitMode === 'bundle' ? STRIPE_LINKS.bundle : STRIPE_LINKS.standard;

  // Success modal copy
  const count = newListings.length;
  document.getElementById('successHeading').textContent = count > 1 ? `${count} Listings Submitted!` : 'Listing Submitted!';
  if (isFree) {
    document.getElementById('successMessage').textContent = `Your free listing is live for 9 days — no payment needed. Want it to stick around longer or get more visibility? You can Boost or get Featured below.`;
  } else {
    document.getElementById('successMessage').textContent = count > 1
      ? `Your ${count} listings are live. Complete payment in the Stripe tab that just opened to keep them active.`
      : `Your listing is live. Complete payment in the Stripe tab that just opened to keep it active.`;
  }

  populateUpsellTarget();
  refreshUpsellButtonsForTarget();

  // Reset form for next use
  resetSubmitForm();

  // Show success
  document.getElementById('successModal').classList.add('open');
  document.body.style.overflow = 'hidden';

  // Re-render
  renderFeatured();
  renderAllListings();
  renderCategories();

  if (!isFree) window.open(stripeLink, '_blank', 'noopener');
}

// ---- SUBMIT: MEMBER STALLION ----
function submitStallionListing(e) {
  e.preventDefault();

  const title = document.getElementById('st-title').value.trim();
  const sire = document.getElementById('st-sire').value.trim();
  const dam = document.getElementById('st-dam').value.trim();
  const sireSire = document.getElementById('st-sire-sire').value.trim();
  const sireDam = document.getElementById('st-sire-dam').value.trim();
  const damSire = document.getElementById('st-dam-sire').value.trim();
  const damDam = document.getElementById('st-dam-dam').value.trim();
  const sireSireSire = document.getElementById('st-ss-s').value.trim();
  const sireSireDam = document.getElementById('st-ss-d').value.trim();
  const sireDamSire = document.getElementById('st-sd-s').value.trim();
  const sireDamDam = document.getElementById('st-sd-d').value.trim();
  const damSireSire = document.getElementById('st-ds-s').value.trim();
  const damSireDam = document.getElementById('st-ds-d').value.trim();
  const damDamSire = document.getElementById('st-dd-s').value.trim();
  const damDamDam = document.getElementById('st-dd-d').value.trim();
  const breed = document.getElementById('st-breed').value.trim();
  const registrationNumber = document.getElementById('st-regnumber').value.trim();
  const color = document.getElementById('st-color').value.trim();
  const height = document.getElementById('st-height').value.trim();
  const foalYear = document.getElementById('st-foalyear').value.trim();
  const discipline = document.getElementById('st-discipline').value.trim();
  const price = parseFloat(document.getElementById('st-studfee').value);
  const location = document.getElementById('st-location').value.trim();
  const pedigree = document.getElementById('st-pedigree').value.trim();
  const progenyEarnings = document.getElementById('st-progeny').value.trim();
  const topProgeny = document.getElementById('st-topprogeny').value.trim();
  const lifetimeEarnings = document.getElementById('st-lifetime').value.trim();
  const description = document.getElementById('st-description').value.trim();
  const image = document.getElementById('st-image').value.trim();
  const video = document.getElementById('st-video').value.trim();
  const documents = document.getElementById('st-documents').value.trim();
  const seller = document.getElementById('st-name').value.trim();
  const email = document.getElementById('st-email').value.trim();
  const phone = document.getElementById('st-phone').value.trim();

  if (!title || !sire || !dam || !breed || !color || !price || !location || !description || !seller || !email) {
    alert('Please fill in all required fields.');
    return;
  }

  const newListing = {
    id: Date.now(),
    title,
    price,
    category: 'Member Stallions',
    location,
    description,
    image: image || 'https://placehold.co/600x400/16a34a/ffffff?text=No+Photo',
    featured: false,
    boosted: false,
    founding: false,
    seller,
    email,
    phone,
    date: new Date().toISOString().split('T')[0],
    sire,
    dam,
    sireSire,
    sireDam,
    damSire,
    damDam,
    sireSireSire,
    sireSireDam,
    sireDamSire,
    sireDamDam,
    damSireSire,
    damSireDam,
    damDamSire,
    damDamDam,
    breed,
    registrationNumber,
    color,
    height,
    foalYear,
    discipline,
    pedigree,
    progenyEarnings,
    topProgeny,
    lifetimeEarnings,
    video,
    documents
  };

  allListings.unshift(newListing);
  lastSubmittedListingIds = [newListing.id];
  persistListings();

  // Email the full stallion profile to the site owner via Netlify Forms
  notifyNetlifyForm('stallion-submission', {
    title,
    sire,
    dam,
    'sire-sire': sireSire,
    'sire-dam': sireDam,
    'dam-sire': damSire,
    'dam-dam': damDam,
    'sire-sire-sire': sireSireSire,
    'sire-sire-dam': sireSireDam,
    'sire-dam-sire': sireDamSire,
    'sire-dam-dam': sireDamDam,
    'dam-sire-sire': damSireSire,
    'dam-sire-dam': damSireDam,
    'dam-dam-sire': damDamSire,
    'dam-dam-dam': damDamDam,
    breed,
    'registration-number': registrationNumber,
    color,
    height,
    'foal-year': foalYear,
    discipline,
    'stud-fee': price,
    location,
    pedigree,
    'progeny-earnings': progenyEarnings,
    'top-progeny': topProgeny,
    'lifetime-earnings': lifetimeEarnings,
    description,
    'photo-url': image,
    'video-url': video,
    'documents-url': documents,
    'seller-name': seller,
    'seller-email': email,
    'seller-phone': phone
  });

  document.getElementById('successHeading').textContent = 'Stallion Profile Submitted!';
  document.getElementById('successMessage').textContent = 'Your stallion profile is live. Complete payment in the Stripe tab that just opened to keep it active for the full 12 months.';

  populateUpsellTarget();
  refreshUpsellButtonsForTarget();

  document.getElementById('submitStallionForm').reset();

  document.getElementById('successModal').classList.add('open');
  document.body.style.overflow = 'hidden';

  renderFeatured();
  renderAllListings();
  renderCategories();
  renderStallions();

  window.open(STRIPE_LINKS.stallion, '_blank', 'noopener');
}

// ---- KEYBOARD ----
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    closeModal();
    closeSuccessModal();
    closeCategoriesPanel();
  }
});
