(function(){
  var els=[].slice.call(document.querySelectorAll('[data-en]'));
  els.forEach(function(el){el.dataset.fr=el.textContent;});
  var links=[].slice.call(document.querySelectorAll('a[href^="https://wa.me/"]'));
  links.forEach(function(a){a.dataset.frHref=a.href;});
  var btn=document.getElementById('lang');
  function set(l){
    document.documentElement.lang=l;
    els.forEach(function(el){el.textContent=l==='en'?el.dataset.en:el.dataset.fr;});
    links.forEach(function(a){
      if(l==='fr'){a.href=a.dataset.frHref;return;}
      var u=new URL(a.dataset.frHref),m=u.searchParams.get('text')||'';
      var mk=m.match(/pour (.+?)\. Mod/);
      u.searchParams.set('text',mk?'Hello Planet Auto Hub, I am looking for a part for '+mk[1]+'. Model and year: ':m===MSG_FR?MSG_EN:'Hello Planet Auto Hub, I have a question: ');
      a.href=u.toString();
    });
    btn.textContent=l==='en'?'FR':'EN';
    document.title=l==='en'?'Planet Auto Hub · Auto parts in Dakar':'Planet Auto Hub · Pièces auto à Dakar';
    try{localStorage.setItem('pah-lang',l);}catch(e){}
  }
  btn.addEventListener('click',function(){set(document.documentElement.lang==='fr'?'en':'fr');});
  var saved=null;try{saved=localStorage.getItem('pah-lang');}catch(e){}
  if(saved==='en'||(!saved&&!/^fr/i.test(navigator.language||'fr')&&/^en/i.test(navigator.language||'')))set('en');
})();
