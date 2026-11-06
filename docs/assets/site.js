(()=>{'use strict';
const menu=document.getElementById('menuToggle'), nav=document.getElementById('siteNav');
if(menu&&nav){menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);});nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{menu.setAttribute('aria-expanded','false');nav.classList.remove('is-open');}));}
const status=document.getElementById('contactCopyStatus');
for(const btn of document.querySelectorAll('[data-copy-wechat]')){
  btn.addEventListener('click',async()=>{
    const id=btn.dataset.copyWechat||'AIPMAndy';let ok=false;
    try{if(navigator.clipboard&&navigator.clipboard.writeText){await navigator.clipboard.writeText(id);ok=true;}}catch{}
    if(!ok){const el=document.createElement('textarea');el.value=id;el.setAttribute('readonly','');el.style.position='fixed';el.style.opacity='0';document.body.append(el);el.select();try{ok=document.execCommand('copy')}catch{}el.remove();}
    if(status)status.textContent=ok?'已复制微信号 '+id+'。打开微信搜索即可添加。':'请手动复制微信号 '+id+'，在微信搜索添加。';
    btn.classList.toggle('copied',ok);
    window.setTimeout(()=>btn.classList.remove('copied'),1800);
  });
}
})();
