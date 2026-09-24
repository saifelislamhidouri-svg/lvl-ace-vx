/* =====================================================
   LVL UP — Dashboard JS
   ===================================================== */
const API = {
  snapshot:  '/api/snapshot',
  logs:      '/api/logs',
  add:       '/api/accounts/add',
  remove:    '/api/accounts/remove',
  start:     '/api/accounts/start',
  stop:      '/api/accounts/stop',
  startAll:  '/api/start_all',
  stopAll:   '/api/stop_all',
};

let lastSnapshot = null;
let logsFilter = '';

async function jpost(url, data){
  const r = await fetch(url,{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(data||{})
  });
  if(r.status===401){location.href='/login';return null;}
  return r.json();
}
async function jget(url){
  const r = await fetch(url);
  if(r.status===401){location.href='/login';return null;}
  return r.json();
}

function toast(msg, type='info'){
  const t=document.createElement('div');
  t.className='toast '+(type==='ok'?'ok':type==='err'?'err':'');
  t.textContent=msg;
  document.body.appendChild(t);
  setTimeout(()=>t.remove(),2200);
}

function fmtUptime(s){
  if(!s||s<0)return '0s';
  const h=Math.floor(s/3600),m=Math.floor((s%3600)/60),ss=s%60;
  if(h)return `${h}h ${m}m`;
  if(m)return `${m}m ${ss}s`;
  return `${ss}s`;
}

const STATUS_LABEL = {
  idle:'⏸ خامل', online:'🟢 متصل', matching:'⚔️ في المباراة',
  logging_in:'🔄 تسجيل', error:'❌ خطأ', stopped:'⏹ متوقف'
};

function renderAccounts(snap){
  const list=document.getElementById('accounts-list');
  const filterSelect=document.getElementById('logs-filter');

  if(!snap.accounts || snap.accounts.length===0){
    list.innerHTML='<div class="empty">لا توجد حسابات — اضغط <b>إضافة حسابات</b></div>';
    document.getElementById('acc-counter').textContent='0';
    return;
  }
  document.getElementById('acc-counter').textContent=snap.accounts.length;

  // populate filter dropdown
  const existingUids=new Set([...filterSelect.options].map(o=>o.value));
  for(const a of snap.accounts){
    if(!existingUids.has(a.uid)){
      const opt=document.createElement('option');
      opt.value=a.uid;
      opt.textContent=`${a.name||a.uid}`;
      filterSelect.appendChild(opt);
    }
  }

  list.innerHTML='';
  snap.accounts.forEach((a,idx)=>{
    const card=document.createElement('div');
    card.className='account-card';
    const initial=(a.name||a.uid).substring(0,2).toUpperCase();
    const isLeader = idx===0;
    const statusClass='status-'+a.status;
    const statusText=STATUS_LABEL[a.status]||a.status;

    card.innerHTML=`
      <div class="acc-avatar">${initial}</div>
      <div class="acc-info">
        <div class="acc-name">
          ${isLeader?'<span class="crown" title="القائد">👑</span>':''}
          <span>${a.name||('Guest_'+a.uid.slice(-4))}</span>
        </div>
        <div class="acc-uid">UID: ${a.uid}</div>
        <div class="acc-meta">
          <span class="meta-chip lvl">⭐ Lv ${a.level}</span>
          <span class="meta-chip gain">📈 +${a.levels_gained}</span>
          <span class="meta-chip">❤️ ${a.likes}</span>
          ${a.online?'<span class="meta-chip" style="background:rgba(34,197,94,.2);color:#86efac">🔌 ONLINE</span>':''}
          ${a.uptime?`<span class="meta-chip">⏱ ${fmtUptime(a.uptime)}</span>`:''}
        </div>
        <div class="progress-wrap"><div class="progress-bar" style="width:${a.progress_pct||0}%"></div></div>
        <span class="status-pill ${statusClass}">${statusText}${a.status_detail?' — '+a.status_detail:''}</span>
      </div>
      <div class="acc-actions">
        ${(a.status==='online'||a.status==='matching'||a.status==='logging_in')
          ?`<button class="mini-btn stop" onclick="stopOne('${a.uid}')">⏹ إيقاف</button>`
          :`<button class="mini-btn go" onclick="startOne('${a.uid}')">▶️ تشغيل</button>`}
        <button class="mini-btn del" onclick="removeOne('${a.uid}')">🗑 حذف</button>
      </div>
    `;
    list.appendChild(card);
  });
}

function renderStats(snap){
  document.getElementById('stat-total').textContent=snap.total;
  document.getElementById('stat-running').textContent=snap.running;
  document.getElementById('stat-levels').textContent=snap.total_levels_gained;
  document.getElementById('stat-engine').textContent=
    snap.running>0?'⚡ يعمل':'💤 خامل';
}

function renderLogs(items){
  const box=document.getElementById('logs-box');
  if(!items || items.length===0){
    box.innerHTML='<div class="log-line muted">[لا توجد سجلات بعد...]</div>';
    return;
  }
  box.innerHTML=items.map(x=>{
    return `<div class="log-line"><span class="uid">[${x.uid}]</span>${escapeHtml(x.text)}</div>`;
  }).join('');
  box.scrollTop=box.scrollHeight;
}
function escapeHtml(s){
  return (s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

async function refreshAll(){
  const snap=await jget(API.snapshot);
  if(!snap)return;
  lastSnapshot=snap;
  renderStats(snap);
  renderAccounts(snap);
  const logUrl = logsFilter
    ? `${API.logs}?limit=120&uid=${encodeURIComponent(logsFilter)}`
    : `${API.logs}?limit=120`;
  const lg=await jget(logUrl);
  if(lg) renderLogs(lg.logs);
}

function refreshNow(){refreshAll();toast('🔄 تم التحديث','ok')}

/* ========== ACTIONS ========== */
async function startOne(uid){
  const r=await jpost(API.start,{uid});
  if(r&&r.ok){toast('▶️ بدء '+uid,'ok');refreshAll()}
  else toast('فشل البدء','err')
}
async function stopOne(uid){
  const r=await jpost(API.stop,{uid});
  if(r&&r.ok){toast('⏹ إيقاف '+uid,'ok');refreshAll()}
}
async function removeOne(uid){
  if(!confirm('حذف الحساب '+uid+' ؟'))return;
  const r=await jpost(API.remove,{uid});
  if(r&&r.ok){toast('🗑 تم الحذف','ok');refreshAll()}
}
async function startAll(){
  const r=await jpost(API.startAll,{});
  if(r&&r.ok){toast(`▶️ تم تشغيل ${r.started} حساب`,'ok');refreshAll()}
}
async function stopAll(){
  if(!confirm('إيقاف كل الحسابات؟'))return;
  const r=await jpost(API.stopAll,{});
  if(r&&r.ok){toast(`⏹ تم إيقاف ${r.stopped} حساب`,'ok');refreshAll()}
}

/* ========== MODAL ========== */
function openAddModal(){document.getElementById('add-modal').classList.add('open')}
function closeAddModal(){
  document.getElementById('add-modal').classList.remove('open');
  document.getElementById('add-input').value='';
}
async function submitAdd(){
  const text=document.getElementById('add-input').value.trim();
  if(!text){toast('اكتب الحسابات أولاً','err');return}
  const r=await jpost(API.add,{text});
  if(r&&r.ok){
    toast(`✅ تم إضافة ${r.added} حساب`+(r.failed.length?` (${r.failed.length} فشل)`:''),'ok');
    closeAddModal();
    refreshAll();
  } else {
    toast('فشل الإضافة','err');
  }
}

function clearLogsView(){
  document.getElementById('logs-box').innerHTML='<div class="log-line muted">[تم المسح من الواجهة - السجلات الفعلية محفوظة]</div>';
}

document.getElementById('logs-filter').addEventListener('change',e=>{
  logsFilter=e.target.value;
  refreshAll();
});

/* close modal on bg click */
document.getElementById('add-modal').addEventListener('click',e=>{
  if(e.target.id==='add-modal')closeAddModal();
});

/* init */
refreshAll();
setInterval(refreshAll,3000);
