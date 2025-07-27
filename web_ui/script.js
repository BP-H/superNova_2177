const api = path => fetch(path).then(r => r.json());

async function loadData() {
  try {
    const meta = await api('/universe');
    document.getElementById('universe-meta').textContent = JSON.stringify(meta, null, 2);
  } catch (e) {
    document.getElementById('universe-meta').textContent = 'Failed to load metadata';
  }

  try {
    const proposals = await api('/proposals');
    const list = document.getElementById('proposals');
    list.innerHTML = '';
    proposals.forEach(p => {
      const li = document.createElement('li');
      li.textContent = `${p.id}: ${p.description} [${p.status}]`;
      list.appendChild(li);
    });
  } catch (e) {
    document.getElementById('proposals').textContent = 'Failed to load proposals';
  }
}

async function createUniverse() {
  const name = document.getElementById('universe-name').value;
  await fetch('/create_universe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
  loadData();
}

async function submitProposal() {
  const text = document.getElementById('proposal-text').value;
  await fetch('/propose', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  loadData();
}

async function submitVote() {
  const id = document.getElementById('vote-id').value;
  const vote = document.getElementById('vote-value').value;
  await fetch('/vote', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, vote })
  });
  loadData();
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('service-worker.js');
  });
}

loadData();
