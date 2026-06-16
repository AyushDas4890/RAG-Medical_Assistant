/* Healthcare Knowledge Navigator — frontend logic
   Single origin: every call uses a RELATIVE path ('/api/...') -> no "unable to fetch". */

const $ = (id) => document.getElementById(id);
let lastSources = [];
let topicsCache = [];
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const finePointer = window.matchMedia("(hover:hover) and (pointer:fine)").matches;

/* ---------- health ---------- */
async function checkHealth() {
  try {
    const r = await fetch("/api/health");
    const h = await r.json();
    let txt, cls;
    if (!h.has_key) { txt = "no API key — add it to backend/.env"; cls = "dot-red"; }
    else if (!h.num_chunks) { txt = "no data — run python ingest.py"; cls = "dot-amber"; }
    else { txt = `online · ${h.num_chunks} chunks · ${h.chat_model}`; cls = "dot-green"; }
    setStatus(txt, cls);
  } catch {
    setStatus("server offline — start uvicorn", "dot-red");
  }
}
function setStatus(txt, cls) {
  for (const [d, s] of [["dotLanding", "statusLanding"], ["dot", "status"]]) {
    const dot = $(d), st = $(s);
    if (dot) dot.className = "dot " + cls;
    if (st) st.textContent = txt;
  }
}

/* ---------- specialised topics (auto from the index) ---------- */
function topicLabel(t){
  return ((t.title || t.source || "").split(" — ")[0] || "").trim() || t.source;
}
function topicEmoji(s){
  s=(s||"").toLowerCase();
  if(/diabet|metformin|glycaem|insulin/.test(s)) return "💊";
  if(/hyperten|blood pressure/.test(s)) return "🩺";
  if(/fibrill|anticoag|stroke|cardio|heart|warfarin/.test(s)) return "🫀";
  if(/headache|migraine/.test(s)) return "🤕";
  if(/cancer|onco|tumour|tumor/.test(s)) return "🎗️";
  if(/infect|antibiotic|sepsis|covid/.test(s)) return "🦠";
  if(/asthma|copd|respir|lung/.test(s)) return "🫁";
  if(/depress|anxiety|mental/.test(s)) return "🧠";
  return "📄";
}
function topicChipsHTML(){
  return topicsCache.map(t=>{
    const label=topicLabel(t);
    const lvl=t.evidence_level?`Level ${t.evidence_level}`:"";
    const q=`Summarise the key recommendations on ${label}.`;
    return `<button class="topic-chip" data-magnetic data-q="${esc(q).replace(/"/g,'&quot;')}"
      title="${esc(t.source)}${t.year?' · '+esc(String(t.year)):''}${lvl?' · '+lvl:''}">
      <span class="te">${topicEmoji(label+' '+t.source)}</span>${esc(label)}</button>`;
  }).join("");
}
async function loadTopics(){
  try{
    const r=await fetch("/api/topics");
    const d=await r.json();
    topicsCache=d.topics||[];
  }catch{ topicsCache=[]; }
  const wrap=$("topicsWrap"), box=$("topics"), hint=$("topicsHint");
  if(!wrap) return;
  if(!topicsCache.length){ wrap.hidden=true; return; }
  wrap.hidden=false;
  box.innerHTML=topicChipsHTML();
  hint.textContent=`${topicsCache.length} topic${topicsCache.length>1?"s":""} indexed · ask about these for grounded, cited answers`;
  box.querySelectorAll(".topic-chip").forEach(b=>{
    b.addEventListener("click",()=>{ openApp(); ask(b.dataset.q); });
    addMagnetic(b);
  });
}

/* ---------- view switching ---------- */
function openApp() {
  $("landing").classList.add("hidden");
  $("app").classList.remove("hidden");
  if (!$("messages").children.length) renderEmptyState();
  $("chatInput").focus();
}
function renderEmptyState() {
  const chips = topicsCache.length
    ? `<div class="empty-topics">${topicChipsHTML()}</div>`
    : "";
  $("messages").innerHTML =
    `<div class="empty-state"><div class="big">🩺</div>
     <div>Ask a clinical question to begin.</div>
     <div style="font-size:13px">Answers are grounded only in the indexed sources, with citations you can inspect.</div>
     ${chips ? `<div style="font-size:12px;margin-top:6px;color:var(--muted)">I currently specialise in:</div>${chips}` : ""}
     </div>`;
  $("messages").querySelectorAll(".topic-chip").forEach(b=>{
    b.addEventListener("click",()=>ask(b.dataset.q)); addMagnetic(b);
  });
}

/* ---------- escaping + tiny markdown ---------- */
function esc(s){return s.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}
function formatAnswer(text){
  let h = esc(text);
  h = h.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  h = h.replace(/\[(\d+)\]/g, (_, n)=>`<span class="cite" data-n="${n}">${n}</span>`);
  h = h.split(/\n{2,}/).map(p=>`<p>${p.replace(/\n/g,"<br>")}</p>`).join("");
  return h;
}

/* ---------- messages ---------- */
function addUser(q){
  const el=document.createElement("div");
  el.className="msg user";
  el.innerHTML=`<div class="who">YOU</div><div class="bubble">${esc(q)}</div>`;
  $("messages").appendChild(el); scrollDown();
}
function addTyping(){
  const el=document.createElement("div");
  el.className="msg ai"; el.id="typing";
  el.innerHTML=`<div class="who">MEDNAV AI</div>
    <div class="bubble"><div class="typing"><i></i><i></i><i></i></div></div>`;
  $("messages").appendChild(el); scrollDown();
}
function removeTyping(){ const t=$("typing"); if(t) t.remove(); }
function addAI(html, isError){
  const el=document.createElement("div");
  el.className="msg ai";
  el.innerHTML=`<div class="who">MEDNAV AI</div>
    <div class="bubble${isError?" error":""}">${html}</div>`;
  $("messages").appendChild(el);
  el.querySelectorAll(".cite").forEach(c=>{
    c.addEventListener("click",()=>openSource(+c.dataset.n));
    hookCursor(c);
  });
  scrollDown();
}
function scrollDown(){ const m=$("messages"); m.scrollTop=m.scrollHeight; }

/* ---------- ask ---------- */
async function ask(q){
  q=(q||"").trim(); if(!q) return;
  if($("messages").querySelector(".empty-state")) $("messages").innerHTML="";
  addUser(q);
  $("chatInput").value="";
  $("sendBtn").disabled=true;
  addTyping();
  try{
    const r=await fetch("/api/chat",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({question:q})
    });
    const data=await r.json();
    removeTyping();
    if(!r.ok || data.error){
      addAI(`⚠️ ${esc(data.error || ("Server error "+r.status))}`, true);
    }else{
      addAI(formatAnswer(data.answer||"(empty answer)"));
      lastSources=data.sources||[];
      renderEvidence(data);
    }
  }catch(err){
    removeTyping();
    addAI(`⚠️ Could not reach the server (${esc(err.message)}). Is uvicorn running?`, true);
  }finally{
    $("sendBtn").disabled=false;
    $("chatInput").focus();
  }
}

/* ---------- evidence panel ---------- */
function renderEvidence(data){
  const conf=data.confidence||{score:0,label:"—",color:"grey"};
  $("evidenceEmpty").classList.add("hidden");
  $("confWrap").style.display="block";
  const colorMap={green:"#10B981",amber:"#F59E0B",orange:"#FB923C",red:"#EF4444",grey:"#64748b"};
  const col=colorMap[conf.color]||colorMap.grey;
  $("confFill").style.width=conf.score+"%";
  $("confFill").style.background=`linear-gradient(90deg,${col}aa,${col})`;
  const badge=$("confBadge");
  badge.textContent=`${conf.score}%  ·  ${conf.label}`;
  badge.style.color=col;

  const box=$("sources"); box.innerHTML="";
  (data.sources||[]).forEach(s=>{
    const lvl=s.evidence_level?`<span class="lvl lvl-${esc(s.evidence_level)}">Level ${esc(s.evidence_level)}</span>`:"";
    const el=document.createElement("div");
    el.className="src-card";
    el.innerHTML=`
      <div class="src-top"><span class="src-n">[${s.n}]</span>
        <span class="src-score">match ${Math.round(s.score*100)}%</span></div>
      <div class="src-title">${esc(s.source)}${s.title?" — "+esc(s.title):""}</div>
      <div class="src-meta">${lvl}${s.year?`<span>📅 ${esc(String(s.year))}</span>`:""}</div>
      <div class="src-snip">${esc(s.snippet||"")}</div>`;
    el.addEventListener("click",()=>openSource(s.n));
    addTilt(el); hookCursor(el);
    box.appendChild(el);
  });
}

/* ---------- citation modal ---------- */
function openSource(n){
  const s=lastSources.find(x=>x.n===n); if(!s) return;
  const lvl=s.evidence_level?`<span class="lvl lvl-${esc(s.evidence_level)}">Level ${esc(s.evidence_level)}</span>`:"";
  const link=s.url?`<a href="${esc(s.url)}" target="_blank" rel="noopener">📖 Open source</a>`:"";
  $("modalBody").innerHTML=`
    <h3>[${s.n}] ${esc(s.source)}</h3>
    <div class="modal-meta">${lvl}${s.title?`<span>${esc(s.title)}</span>`:""}
      ${s.year?`<span>📅 ${esc(String(s.year))}</span>`:""}
      <span>match ${Math.round(s.score*100)}%</span></div>
    <div class="modal-quote">${esc(s.snippet||"")}</div>
    <div class="modal-actions">${link}
      <button id="copyCite">📋 Copy citation</button></div>`;
  $("modal").classList.remove("hidden");
  const c=$("copyCite");
  if(c){ hookCursor(c); c.addEventListener("click",()=>{
    navigator.clipboard.writeText(`${s.source}${s.title?", "+s.title:""}${s.year?" ("+s.year+")":""}. ${s.url||""}`.trim());
    c.textContent="✓ Copied";
  });}
}
function closeModal(){ $("modal").classList.add("hidden"); }

/* ---------- evidence toggle ---------- */
function toggleEvidence(){
  $("evidence").classList.toggle("hidden");
  document.querySelector(".workspace").classList.toggle("no-evidence",
    $("evidence").classList.contains("hidden"));
}

/* =====================================================================
   MOTION LAYER — custom cursor, magnetic buttons, 3D tilt, scroll reveal
   ===================================================================== */

/* custom cursor */
const ring=$("cursorRing"), dot=$("cursorDot");
let mx=innerWidth/2, my=innerHeight/2, rx=mx, ry=my;
if(finePointer && !reduceMotion){
  addEventListener("mousemove",e=>{
    mx=e.clientX; my=e.clientY;
    dot.style.transform=`translate(${mx}px,${my}px) translate(-50%,-50%)`;
  });
  (function loop(){ rx+=(mx-rx)*.18; ry+=(my-ry)*.18;
    ring.style.transform=`translate(${rx}px,${ry}px) translate(-50%,-50%)`;
    requestAnimationFrame(loop); })();
}
function hookCursor(el){
  if(!finePointer||reduceMotion) return;
  el.addEventListener("mouseenter",()=>ring.classList.add("hovering"));
  el.addEventListener("mouseleave",()=>ring.classList.remove("hovering"));
}

/* magnetic pull on [data-magnetic] */
function addMagnetic(el){
  if(!finePointer||reduceMotion) return;
  hookCursor(el);
  const strength=0.35;
  el.addEventListener("mousemove",e=>{
    const r=el.getBoundingClientRect();
    const x=e.clientX-(r.left+r.width/2);
    const y=e.clientY-(r.top+r.height/2);
    el.style.transform=`translate(${x*strength}px,${y*strength}px)`;
  });
  el.addEventListener("mouseleave",()=>{ el.style.transform=""; });
}

/* 3D tilt on cards */
function addTilt(el){
  if(!finePointer||reduceMotion) return;
  el.addEventListener("mousemove",e=>{
    const r=el.getBoundingClientRect();
    const px=(e.clientX-r.left)/r.width-0.5;
    const py=(e.clientY-r.top)/r.height-0.5;
    el.style.transform=`perspective(700px) rotateY(${px*8}deg) rotateX(${-py*8}deg) translateY(-3px)`;
  });
  el.addEventListener("mouseleave",()=>{ el.style.transform=""; });
}

/* scroll reveal — also reveals immediately on load for above-the-fold */
function initReveal(){
  const els=[...document.querySelectorAll("[data-reveal]")];
  if(reduceMotion){ els.forEach(e=>e.classList.add("in")); return; }
  const io=new IntersectionObserver((entries)=>{
    entries.forEach((en,i)=>{ if(en.isIntersecting){
      setTimeout(()=>en.target.classList.add("in"), i*70);
      io.unobserve(en.target);
    }});
  },{threshold:0.12});
  els.forEach(e=>io.observe(e));
  // safety: guarantee visibility even if observer is slow
  setTimeout(()=>els.forEach(e=>e.classList.add("in")), 600);
}

/* background parallax to mouse */
function initParallax(){
  if(!finePointer||reduceMotion) return;
  const blobs=[...document.querySelectorAll(".blob")];
  addEventListener("mousemove",e=>{
    const cx=(e.clientX/innerWidth-0.5), cy=(e.clientY/innerHeight-0.5);
    blobs.forEach(b=>{
      const d=parseFloat(b.dataset.depth||"0.05")*120;
      b.style.marginLeft=(cx*d)+"px"; b.style.marginTop=(cy*d)+"px";
    });
  });
}

/* duplicate marquee content for a seamless loop */
function initMarquee(){
  const t=$("marqueeTrack"); if(t) t.innerHTML+=t.innerHTML;
}

/* ---------- wire up ---------- */
$("landingForm").addEventListener("submit",e=>{e.preventDefault();
  const q=$("landingInput").value; openApp(); ask(q);});
$("quickstarts").addEventListener("click",e=>{
  const b=e.target.closest("button"); if(!b) return; openApp(); ask(b.dataset.q);});
$("chatForm").addEventListener("submit",e=>{e.preventDefault(); ask($("chatInput").value);});
$("homeBtn").addEventListener("click",()=>{
  $("app").classList.add("hidden"); $("landing").classList.remove("hidden"); checkHealth(); loadTopics();});
$("evidenceToggle").addEventListener("click",toggleEvidence);
$("modalX").addEventListener("click",closeModal);
$("modal").addEventListener("click",e=>{if(e.target===$("modal"))closeModal();});
document.addEventListener("keydown",e=>{
  if(e.key==="Escape")closeModal();
  if((e.ctrlKey||e.metaKey)&&e.key==="/"){e.preventDefault();toggleEvidence();}
});
document.querySelectorAll("[data-magnetic]").forEach(addMagnetic);

initReveal(); initParallax(); initMarquee();
checkHealth(); loadTopics();
setInterval(checkHealth, 15000);
