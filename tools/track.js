/* Anonymous first-party visit counter. One record per visit, sent to the shop's own Firebase.
   No cookies, no third party, no IP kept by us. Respects Do Not Track / Global Privacy Control.
   Visit ?notrack once on a device to exclude that device (owner, staff). */
(function(){
  try{
    var H=location.hostname;
    if(H!=='planetautohub.com'&&H!=='www.planetautohub.com')return;
    if(navigator.doNotTrack==='1'||navigator.globalPrivacyControl)return;
    var ls=window.localStorage;
    if(/[?&]notrack(&|=|$)/.test(location.search))ls.setItem('pah-off','1');
    if(ls.getItem('pah-off')==='1')return;
    if(/bot|crawl|spider|headless|lighthouse|preview|facebookexternalhit|slurp|monitor/i.test(navigator.userAgent||''))return;
    var day=new Date().toISOString().slice(0,10),cap=0;
    try{var c=(ls.getItem('pah-cap')||'').split('|');if(c[0]===day)cap=+c[1]||0;}catch(e){}
    if(cap>=40)return;
    function rnd(n){var a=new Uint8Array(n),s='',i;crypto.getRandomValues(a);for(i=0;i<n;i++)s+='abcdefghijklmnopqrstuvwxyz0123456789'[a[i]%36];return s;}
    var vid=ls.getItem('pah-vid'),nv=false;
    if(!vid){vid=rnd(16);nv=true;try{ls.setItem('pah-vid',vid);}catch(e){}}
    var sid=rnd(20),t0=Date.now(),vis=document.visibilityState!=='hidden',since=t0,acc=0,secs=[],clicks=[],depth=0,sent=0,last=0,ref='';
    try{if(document.referrer){var u=new URL(document.referrer);if(u.hostname!==H)ref=u.hostname.replace(/^www\./,'').slice(0,60);}}catch(e){}
    var q=new URLSearchParams(location.search),src=(q.get('utm_source')||q.get('src')||'').replace(/[^\w.-]/g,'').slice(0,30);
    var w=window.innerWidth||0,dev=w<640?'m':w<1024?'t':'d';
    function dur(){return Math.round((acc+(vis?Date.now()-since:0))/1000);}
    function sv(s){return{stringValue:String(s)};}
    function iv(n){return{integerValue:String(Math.max(0,Math.round(n)))};}
    function arr(a){return{arrayValue:{values:a.map(sv)}};}
    function send(force){
      var now=Date.now();
      if(sent>=8||(!force&&now-last<4000))return;
      last=now;sent++;
      try{
        var f={sid:sv(sid),vid:sv(vid),day:sv(day),ts:iv(t0),dur:iv(dur()),depth:iv(depth),dev:sv(dev),w:iv(w),
          lang:sv(document.documentElement.lang==='en'?'en':'fr'),vl:sv((navigator.language||'').slice(0,10)),
          tz:sv((Intl.DateTimeFormat().resolvedOptions().timeZone||'').slice(0,40)),ref:sv(ref),src:sv(src),
          nv:{booleanValue:nv},secs:arr(secs.slice(0,12)),clicks:arr(clicks.slice(0,30))};
        fetch('https://firestore.googleapis.com/v1/projects/'+PAH_T.p+'/databases/(default)/documents/stores/'+PAH_T.s+'/web_hits/'+sid+'?key='+PAH_T.k,
          {method:'PATCH',keepalive:true,headers:{'Content-Type':'application/json'},body:JSON.stringify({fields:f})}).catch(function(){});
        cap++;ls.setItem('pah-cap',day+'|'+cap);
      }catch(e){}
    }
    function hid(){if(vis){acc+=Date.now()-since;vis=false;}send(true);}
    document.addEventListener('visibilitychange',function(){if(document.visibilityState==='hidden')hid();else{vis=true;since=Date.now();}});
    addEventListener('pagehide',hid);
    function sd(){var h=document.documentElement,d=Math.round(((window.scrollY||0)+(window.innerHeight||0))/Math.max(1,h.scrollHeight)*100);if(d>depth)depth=Math.min(100,d);}
    addEventListener('scroll',sd,{passive:true});
    if(window.IntersectionObserver){
      var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting&&secs.indexOf(e.target.id)<0&&e.target.id)secs.push(e.target.id);});},{threshold:.15});
      [].forEach.call(document.querySelectorAll('main section[id]'),function(s){io.observe(s);});
    }
    function where(el){var s=el.closest('section[id]');return s?s.id:el.closest('header')?'header':el.classList.contains('dock')?'dock':'';}
    function click(e){
      var a=e.target.closest&&e.target.closest('a,summary,button');if(!a)return;
      var h=a.getAttribute('href')||'',k='',m=a.closest('details.mk'),mk=m&&m.querySelector('.mk-n');
      if(a.id==='lang')k='lang';
      else if(a.tagName==='SUMMARY')k='open:'+(mk?mk.textContent:'').slice(0,24);
      else if(h.indexOf('https://wa.me/')===0){var n=h.slice(14).split('?')[0];k=mk?'make:'+mk.textContent.slice(0,24):'wa'+(PAH_T.n[n]||'?')+'@'+where(a);}
      else if(h.indexOf('tel:')===0)k='call@'+where(a);
      else if(h.indexOf('google.com/maps')>0)k='maps';
      else if(/tiktok\.com/.test(h))k='tiktok';else if(/facebook\.com/.test(h))k='facebook';else if(/instagram\.com/.test(h))k='instagram';
      else if(h.charAt(0)==='#')k='nav:'+h.slice(1,16);
      if(!k)return;
      clicks.push(k);
      if(/^(wa|make|call)/.test(k))send(true);
    }
    document.addEventListener('click',click,true);
    setTimeout(function(){sd();send(true);},1500);
    setInterval(function(){if(vis)send(false);},30000);
  }catch(e){}
})();
