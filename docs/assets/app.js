/* Faceless YouTube creator toolkit — zero network calls, no dependencies. */
(()=>{'use strict';
const data=window.YT_DATA||{guides:[],ideas:[],cases:[],plan:[]};
const STORE='andy-faceless-yt-v1';
const $=id=>document.getElementById(id);
const el=(tag,klass,text)=>{const n=document.createElement(tag);if(klass)n.className=klass;if(text!==undefined)n.textContent=String(text);return n;};
const load=()=>{try{const s=JSON.parse(localStorage.getItem(STORE)||'{}');return (s&&typeof s==='object'&&!Array.isArray(s))?s:{};}catch{return {};}};
let state=load();
const save=()=>{try{localStorage.setItem(STORE,JSON.stringify(state));}catch{document.querySelector('#importMessage').textContent='此浏览器无法保存进度，可导出备份。';}};
const guideDone=id=>Boolean(state['g:'+id]);
function renderGuides(){
const root=$('guideCards');root.replaceChildren();
const query=$('guideSearch').value.trim().toLowerCase(),stage=$('stageFilter').value;
const filtered=data.guides.filter(g=>(stage==='all'||g.stage===stage)&&[g.title,g.overview,g.stage,...g.steps].join(' ').toLowerCase().includes(query));
for(const g of filtered){
const card=el('article','guide-card');const top=el('div','guide-card-top');top.append(el('span','step-num',String(g.index+1).padStart(2,'0')),el('span','step-stage',g.stage));
card.append(top);const heading=el('h3');const a=el('a','card-link',g.title);a.href='guides/'+encodeURIComponent(g.id)+'/';heading.append(a);card.append(heading);
card.append(el('p','guide-intro',g.overview));
const footer=el('div','guide-card-footer'), link=el('a','read-link','打开步骤 ↗');link.href=a.href;
const label=el('label','done-label'),check=el('input');check.type='checkbox';check.checked=guideDone(g.id);check.setAttribute('aria-label','完成：'+g.title);
check.addEventListener('change',()=>{state['g:'+g.id]=check.checked;save();updateGuideProgress();});
label.append(check,el('span',null,'我已完成'));footer.append(label,link);card.append(footer);root.append(card);
}
$('guideEmpty').hidden=filtered.length!==0;updateGuideProgress();
}
function updateGuideProgress(){let n=data.guides.filter(g=>guideDone(g.id)).length;$('progressText').textContent=`已完成 ${n} / ${data.guides.length}`;$('progressBar').style.width=(data.guides.length?100*n/data.guides.length:0)+'%';}
function initGuides(){const stages=[...new Set(data.guides.map(x=>x.stage))];for(const stage of stages){const opt=el('option',null,stage);opt.value=stage;$('stageFilter').append(opt);}['guideSearch','stageFilter'].forEach(id=>$(id).addEventListener(id==='guideSearch'?'input':'change',renderGuides));renderGuides();}
const dims=[{id:'demand',label:'真实用户需求',weight:35,help:'是否有搜索、评论或已验证的问题？'},{id:'proof',label:'原创演示与证据',weight:25,help:'你是否能亲自录屏做出完整结果？'},{id:'money',label:'商业价值',weight:20,help:'观众得到价值后是否有明确下一步？'},{id:'effort',label:'制作可行性',weight:10,help:'用现有工具一周内能不能完成？'},{id:'edge',label:'差异化',weight:10,help:'相比现有视频你能多交付什么？'}];
function initScore(){const root=$('scoringRows');for(const d of dims){const wrap=el('div','score-input-row'),head=el('div','score-input-head');head.append(el('strong',null,d.label),el('span',null,'权重 '+d.weight+'%'));wrap.append(head,el('p','input-help',d.help));const select=el('select','field score-select');select.id='score-'+d.id;select.setAttribute('aria-label',d.label);for(let i=1;i<=5;i++){const o=el('option',null,`${i} / 5`);o.value=i;if(i===3)o.selected=true;select.append(o);}wrap.append(select);root.append(wrap);} $('calculateScore').addEventListener('click',()=>{
const title=$('topicName').value.trim()||'未命名选题';let total=0;const detail=[];for(const d of dims){const v=Number($('score-'+d.id).value);total+=d.weight*v/5;detail.push(`${d.label} ${v}/5`);}total=Math.round(total);
$('totalScore').textContent=total;$('scoreVerdict').textContent=total>=80?'优先进入制作':total>=65?'值得再补证据':'暂不建议投入大制作';$('scoreAdvice').textContent=total>=80?'先按 6–10 分钟脚本拍一条原创视频，上线后再根据真实反馈判断。':total>=65?'先补一个真实案例、可录的画面或观众需求来源，再进入拍摄。':'先验证问题是否有人关心，不建议直接外包剪辑或制作。';
window.lastScore=`选题：${title}\n评分：${total}/100\n${detail.join('\n')}\n建议：${$('scoreVerdict').textContent}\n说明：主观评分不代表预测播放量。`;});
$('copyTopic').addEventListener('click',async()=>{if(!window.lastScore){$('calculateScore').click();}try{await navigator.clipboard.writeText(window.lastScore);$('copyTopic').textContent='已复制';setTimeout(()=>$('copyTopic').textContent='复制评估结果',1200);}catch{$('copyTopic').textContent='浏览器不支持复制，请手动选择';}});}
let activePhase='启动';
function renderPlan(){const root=$('dailyPlan');root.replaceChildren();const filtered=data.plan.filter(x=>x.phase===activePhase);let done=0;for(const p of filtered){const row=el('label','day-row'),cb=el('input');cb.type='checkbox';cb.checked=Boolean(state['d:'+p.day]);if(cb.checked)done++;const text=el('div','day-info');text.append(el('strong',null,p.task),el('small',null,p.done_criteria));row.append(el('span','day-number',`D${String(p.day).padStart(2,'0')}`),text,cb);cb.addEventListener('change',()=>{state['d:'+p.day]=cb.checked;save();renderPlan();});root.append(row);} $('planDone').textContent=done;$('planTotal').textContent=filtered.length;$('planPhaseTitle').textContent=activePhase;}
function initPlan(){document.querySelectorAll('[data-phase]').forEach(b=>b.addEventListener('click',()=>{activePhase=b.dataset.phase;document.querySelectorAll('[data-phase]').forEach(x=>x.classList.toggle('selected',x===b));renderPlan();}));renderPlan();}
function initCases(){const root=$('caseCards');for(const c of data.cases){const card=el('article','case-card');card.append(el('p','case-format',c.format),el('h3',null,c.name),el('p',null,c.observed));const learn=el('div','case-learn');learn.append(el('strong',null,'可学习：'),el('span',null,c.reusable));card.append(learn);const caveat=el('p','case-limit','证据边界：'+c.limits);card.append(caveat);const source=el('a','read-link','打开原始来源 ↗');source.href=c.primary_source;source.target='_blank';source.rel='noopener noreferrer';card.append(source);root.append(card);}}
function initIdeas(){const root=$('ideaRows');data.ideas.forEach((v,i)=>{const row=el('article','idea-row');row.append(el('span','idea-num',String(i+1).padStart(2,'0')));const body=el('div');body.append(el('h3',null,v.title),el('p',null,`${v.viewer} · 演示：${v.proof} · 关联：${v.asset}`));row.append(body,el('span','idea-tag',v.pillar));root.append(row);});}
function initBackup(){$('exportProgress').addEventListener('click',()=>{const payload={schema:1,exportedAt:new Date().toISOString(),data:state};const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=el('a');a.href=url;a.download='faceless-youtube-progress.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('importProgress').addEventListener('change',async e=>{const f=e.target.files?.[0];if(!f)return;if(f.size>1024*256){$('importMessage').textContent='文件太大（上限 256 KB）';return;}try{const o=JSON.parse(await f.text());if(o.schema!==1||!o.data||typeof o.data!=='object'||Array.isArray(o.data))throw Error('格式不对');const allowed=new Set([...data.guides.map(g=>'g:'+g.id),...data.plan.map(p=>'d:'+p.day)]);const clean={};for(const [k,v] of Object.entries(o.data)){if(allowed.has(k)&&typeof v==='boolean')clean[k]=v;}state=clean;save();renderGuides();renderPlan();$('importMessage').textContent='进度已恢复';}catch{$('importMessage').textContent='导入失败，请使用本站导出的 JSON 文件';}e.target.value='';});}

function num(id){const raw=$(id).value.trim();if(raw==='')return null;const x=Number(raw);return Number.isFinite(x)&&x>=0?x:null;}
function initClinic(){
const form=$('clinicForm');if(!form)return;
$('clinicFormat').addEventListener('change',()=>{const isShort=$('clinicFormat').value==='short';for(const id of ['clinicImpressions','clinicCtr']){$(id).disabled=isShort;$(id).value='';}});
form.addEventListener('submit',event=>{event.preventDefault();
const short=$('clinicFormat').value==='short',impressions=num('clinicImpressions'),ctr=num('clinicCtr'),ret=num('clinicRetention'),clicks=num('clinicClicks'),leads=num('clinicLeads');
const items=[];
if(!short){if(impressions===null)items.push('缺少展示量：先回 Studio 查看覆盖/流量来源。');else if(impressions<500)items.push('展示样本尚少，先核对公开状态、受众问题与来源，不要断言“被限流”。');else if(ctr===null)items.push('有展示但没填 CTR：优先补数据，再判断封面和标题。');else items.push('CTR 要与同类视频、相近流量来源比较；不能用固定百分比宣判好坏。');}
else items.push('Shorts 不使用长视频的展示点击率标准；核对“选择观看”、留存与相关长视频入口。');
if(ret===null)items.push('前 30 秒留存缺失：若 Studio 可提供，回看开场是否兑现标题。');else items.push('检查留存曲线的掉点位置和实际画面，不凭单个留存百分比判定原因。');
if(clicks!==null&&clicks>=20&&leads===0)items.push('已有资源点击但没有有效咨询，先确认免费资源和服务是否匹配这类观众。');
else if(leads!==null&&leads>0)items.push('出现有效咨询：记录实际问题、来源和是否成交，不把“咨询”直接计为收入。');
else items.push('免费资源与询盘数据尚不能说明商业问题，先补来源追踪。');
$('clinicHeadline').textContent='下一轮：验证最早掉落的环节';const ul=el('ul','diagnosis-list');for(const t of items)ul.append(el('li',null,t));$('clinicFeedback').replaceChildren(ul);});
}
function initEconomy(){
const form=$('economyForm');if(!form)return;
form.addEventListener('submit',e=>{e.preventDefault();const ids=['econViews','econClick','econLead','econClose','econPrice','econVariable','econFixed'];const v=ids.map(num);
if(v.some(x=>x===null)){ $('econHeadline').textContent='请填写所有假设';$('econEquation').textContent='所有字段必须是非负数，百分比在 0–100 之间。';return; }
const [views,clickRate,leadRate,closeRate,price,perOrder,fixed]=v;if([clickRate,leadRate,closeRate].some(x=>x>100)){$('econHeadline').textContent='百分比不正确';return;}
const clicks=views*clickRate/100,leads=clicks*leadRate/100,orders=leads*closeRate/100;const gross=orders*price,cost=fixed+orders*perOrder,net=gross-cost;
const fx=x=>new Intl.NumberFormat('zh-CN',{maximumFractionDigits:2}).format(x);
$('econHeadline').textContent='该情景的数学结果';
const text=el('div');text.append(el('p',null,`${fx(views)} 次观看 → ${fx(clicks)} 次资源点击 → ${fx(leads)} 次合格咨询 → ${fx(orders)} 笔期望订单`),el('p',null,`模拟实收：¥${fx(gross)}；模拟成本：¥${fx(cost)}`));const n=el('p');n.append('模拟差额：',el('strong',null,`¥${fx(net)}`));text.append(n);$('econEquation').replaceChildren(text);
$('econNote').textContent='期望订单可以为小数，表示模型平均值，不是实际订单数量。不同视频客群、外链位置与交付成本可能大幅改变结果。';});
}

function initContact(){
  const buttons=document.querySelectorAll('[data-copy-wechat]');
  for(const button of buttons){
    const original=button.textContent;
    button.addEventListener('click',async()=>{
      const id=button.getAttribute('data-copy-wechat')||'AIPMAndy';
      let copied=false;
      try{
        if(navigator.clipboard&&navigator.clipboard.writeText){
          await navigator.clipboard.writeText(id);copied=true;
        }
      }catch{}
      if(!copied){
        const input=document.createElement('textarea');
        input.value=id;input.setAttribute('readonly','');input.style.position='fixed';input.style.opacity='0';
        document.body.append(input);input.select();
        try{copied=document.execCommand('copy')}catch{}
        input.remove();
      }
      button.textContent=copied?'已复制：'+id:'微信号：'+id+'（请手动复制）';
      const status=$('contactCopyStatus');
      if(status)status.textContent=copied?'微信号已复制。在微信搜索 AIPMAndy 添加即可。':'自动复制不可用，请手动复制微信号 AIPMAndy。';
      setTimeout(()=>{button.textContent=original;},2200);
    });
  }
}

function bootstrap(){if(!data.guides.length){document.body.append(el('p',null,'内容尚未构建，请运行 python scripts/build.py'));return;}initGuides();initScore();initClinic();initEconomy();initPlan();initCases();initIdeas();initBackup();initContact();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bootstrap);else bootstrap();
})();
