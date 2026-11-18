#!/usr/bin/env python3
"""Builds site/index.html for Planet Auto Hub. Static, no forms, no tracking. French first, English toggle."""
import json, html, urllib.parse, os, collections

W1, W2 = '221787567676', '221787537676'
P1, P2 = '+221 78 756 76 76', '+221 78 753 76 76'
e = html.escape

def wa(num, fr, en=None):
    return f'https://wa.me/{num}?text={urllib.parse.quote(fr)}'

MSG = 'Bonjour Planet Auto Hub, je cherche une pièce. Véhicule (marque, modèle, année) : '
MSG_EN = 'Hello Planet Auto Hub, I am looking for a part. Vehicle (make, model, year): '

def t(fr, en, tag='span', cls='', attrs=''):
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c} {attrs} data-en="{e(en, quote=True)}">{e(fr, quote=False)}</{tag}>'

I = {  # 24px, 1.5 stroke
 'chat': 'M4 19.5 5.3 15A8 8 0 1 1 9 18.7L4 19.5z',
 'engine': 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zM12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M5.6 18.4l1.8-1.8M16.6 7.4l1.8-1.8',
 'drop': 'M12 3.5s6 6.2 6 10.5a6 6 0 0 1-12 0c0-4.3 6-10.5 6-10.5z',
 'disc': 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z',
 'battery': 'M4 8h16v11H4zM7 8V5.5h3V8M14 8V5.5h3V8M7 13.5h3M15.5 12v3M14 13.5h3',
 'box': 'M12 3 4 7v10l8 4 8-4V7l-8-4zM4 7l8 4 8-4M12 11v10',
 'globe': 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.500 5.6 12 3z',
 'check': 'M12 3 5 6v5.5c0 4.300 2.900 7.700 7 9.500 4.100-1.800 7-5.200 7-9.500V6l-7-3zM9 12l2.200 2.200L15.200 10',
 'pulse': 'M3 12h4l2.500-6 4 12 2.500-6h5',
 'truck': 'M3 6.500h11v9.500H3zM14 10h4l3 3v3h-7zM7 18.500a1.500 1.500 0 1 0 0-3 1.500 1.500 0 0 0 0 3zM17.500 18.500a1.500 1.500 0 1 0 0-3 1.500 1.500 0 0 0 0 3z',
 'wrench': 'M14.500 6.200a4 4 0 0 0-5.300 5.300L3.500 17.200l3.300 3.300 5.700-5.700a4 4 0 0 0 5.300-5.300l-2.600 2.600-2.300-.700-.700-2.300 2.300-2.900z',
 'fleet': 'M4 20V5.500h9V20M13 10h7v10M7 9h3M7 12.500h3M7 16h3M16 13.500h1.500M16 17h1.500M3 20h18',
 'pin': 'M12 21s6.500-5.800 6.500-11a6.500 6.500 0 0 0-13 0c0 5.200 6.500 11 6.500 11zM12 7.500a2.500 2.500 0 1 0 0 5 2.500 2.500 0 0 0 0-5z',
 'phone': 'M6 3.500h3l1.500 4-2 1.500a11 11 0 0 0 6.500 6.500l1.500-2 4 1.500v3a2 2 0 0 1-2.200 2A17 17 0 0 1 4 5.700 2 2 0 0 1 6 3.500z',
}
def ic(n): return f'<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="{I[n]}"/></svg>'

def wbtn(num, label_fr, label_en, msg=MSG, cls='btn pri'):
    return f'<a class="{cls}" href="{wa(num, msg)}" target="_blank" rel="noopener">{ic("chat")}{t(label_fr, label_en)}</a>'

def duo(msg=MSG):
    return ('<div class="cta">' + wbtn(W1, 'WhatsApp · Ligne 1', 'WhatsApp · Line 1', msg) + wbtn(W2, 'WhatsApp · Ligne 2', 'WhatsApp · Line 2', msg, 'btn') + '</div>')

CATS = [
 ('engine', 'Moteur et entretien', 'Engine and maintenance', 'Filtres, courroies, allumage, capteurs, refroidissement, embrayage.', 'Filters, belts, ignition, sensors, cooling, clutch.'),
 ('drop', 'Lubrifiants et fluides', 'Lubricants and fluids', 'Huiles moteur, huiles de boîte, liquide de refroidissement, AdBlue.', 'Engine oils, transmission fluids, coolant, AdBlue.'),
 ('disc', 'Freinage et suspension', 'Brakes and suspension', 'Plaquettes, disques, amortisseurs, rotules, direction, cardans.', 'Pads, discs, shock absorbers, ball joints, steering, CV axles.'),
 ('battery', 'Électricité et batteries', 'Electrical and batteries', 'Batteries, démarreurs, alternateurs, ampoules, commodos, capteurs.', 'Batteries, starters, alternators, bulbs, switches, sensors.'),
 ('box', 'Climatisation et accessoires', 'A/C and accessories', 'Compresseurs, condenseurs, produits d\'entretien, accessoires.', 'Compressors, condensers, care products, accessories.'),
 ('globe', 'Commandes spéciales', 'Special orders', 'Pièce introuvable à Dakar ? Nous la cherchons chez nos fournisseurs à l\'étranger.', 'Part not available in Dakar? We source it from our suppliers abroad.'),
]
SERV = [
 ('check', 'Vérification de compatibilité', 'Fitment check', 'Nous confirmons la pièce avec le numéro de châssis (VIN), la référence d\'origine ou une photo.', 'We confirm the part using the chassis number (VIN), the OEM reference or a photo.'),
 ('pulse', 'Diagnostic', 'Diagnostics', 'Lecture des codes défaut et test de batterie pour identifier la bonne pièce.', 'Fault-code reading and battery testing to identify the right part.'),
 ('wrench', 'Montage et réparation', 'Fitting and repairs', 'Réalisés par nos garages partenaires. Nous vous mettons en relation.', 'Carried out by our partner garages. We put you in touch.'),
 ('truck', 'Livraison', 'Delivery', 'Livraison à Dakar et expédition vers les régions. Demandez les conditions sur WhatsApp.', 'Delivery in Dakar and shipping to the regions. Ask for terms on WhatsApp.'),
 ('globe', 'Commande spéciale', 'Special-order sourcing', 'Pièces d\'origine ou adaptables rares, commandées auprès de fournisseurs internationaux.', 'Rare OEM or aftermarket parts, ordered from international suppliers.'),
 ('fleet', 'Garages et flottes', 'Garages and fleets', 'Commandes régulières, listes de pièces par véhicule, tarifs professionnels.', 'Repeat orders, parts lists per vehicle, trade pricing.'),
]
STEPS = [
 ('Votre véhicule', 'Your vehicle', 'Marque, modèle, année, moteur. Le numéro de châssis si possible.', 'Make, model, year, engine. The chassis number if you can.'),
 ('La pièce', 'The part', 'Nom, photo de l\'ancienne pièce, référence, ou simplement la panne.', 'Name, photo of the old part, reference, or just the symptom.'),
 ('Vos options', 'Your options', 'Origine, qualité équivalente ou économique, selon votre budget.', 'Genuine, OEM-quality or value, to match your budget.'),
 ('Retrait ou livraison', 'Pickup or delivery', 'Confirmez, puis passez à la boutique ou faites-vous livrer.', 'Confirm, then collect at the shop or have it delivered.'),
]
GROUPS = [
 ('Japon', 'Japan', ['Toyota', 'Lexus', 'Nissan', 'Infiniti', 'Mitsubishi', 'Honda', 'Acura', 'Mazda', 'Isuzu', 'Suzuki', 'Subaru']),
 ('France', 'France', ['Peugeot', 'Renault', 'Dacia', 'Citroën']),
 ('Allemagne', 'Germany', ['Mercedes-Benz', 'BMW', 'Audi', 'Volkswagen', 'Opel']),
 ('Corée', 'Korea', ['Hyundai', 'Kia']),
 ('États-Unis', 'USA', ['Ford', 'Chevrolet', 'GMC', 'Jeep', 'Dodge', 'Chrysler', 'Cadillac']),
 ('Royaume-Uni et Italie', 'UK and Italy', ['Land Rover', 'Fiat']),
 ('Chine et Inde', 'China and India', ['Great Wall', 'Haval', 'Changan', 'Geely', 'BYD', 'JAC', 'Dongfeng', 'Foton', 'DFSK', 'Mahindra']),
]
KNOWN = sorted({m for g in GROUPS for m in g[2]}, key=len, reverse=True)
models = collections.defaultdict(list)
for v in json.load(open('vehicles.json'))['veh']:
    v = v.replace('GWM ', 'Great Wall ')
    mk = next((k for k in KNOWN if v.startswith(k + ' ')), None)
    if mk and v[len(mk) + 1:] not in models[mk]: models[mk].append(v[len(mk) + 1:])
slug = lambda m: m.lower().replace(' ', '-').replace('ë', 'e')

def make_card(m):
    f = f'assets/makes/{slug(m)}.webp'
    logo = f'<img src="{f}" alt="" width="96" height="64" loading="lazy" decoding="async">' if os.path.exists('../' + f) else f'<span class="mk-t" aria-hidden="true">{e(m)}</span>'
    ml = models.get(m, [])
    body = (f'<p class="models">{e(", ".join(ml))}</p>' if ml else '') + f'<a class="lnk" href="{wa(W1, "Bonjour Planet Auto Hub, je cherche une pièce pour " + m + ". Modèle et année : ")}" target="_blank" rel="noopener">{t("Demander une pièce " + m, "Ask for a " + m + " part")}</a>'
    return f'<details class="mk"><summary><span class="mk-l">{logo}</span><span class="mk-n">{e(m)}</span><span class="mk-c">{len(ml) or ""}</span></summary><div class="mk-b">{body}</div></details>'

css = open('style.css').read()
js = open('app.js').read()
out = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; font-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>Planet Auto Hub · Pièces auto à Dakar</title>
<meta name="description" content="Pièces auto neuves à Dakar : filtres, freinage, suspension, batteries, lubrifiants. Compatibilité vérifiée avec votre numéro de châssis. Écrivez-nous sur WhatsApp.">
<meta property="og:title" content="Planet Auto Hub · Pièces auto à Dakar">
<meta property="og:description" content="Pièces neuves, compatibilité vérifiée, commande sur WhatsApp. Rond-Point Liberté 6, Dakar.">
<meta property="og:image" content="assets/og.jpg">
<meta property="og:type" content="website">
<meta name="theme-color" content="#3D469C">
<link rel="icon" href="assets/icon.png">
<link rel="apple-touch-icon" href="assets/icon.png">
<link rel="preload" href="assets/montserrat.woff2" as="font" type="font/woff2" crossorigin>
<style>{css}</style>
</head>
<body>
<a class="skip" href="#main">{t("Aller au contenu", "Skip to content")}</a>
<header class="top"><div class="w bar">
  <a class="logo" href="#top" aria-label="Planet Auto Hub"><img src="assets/logo.webp" alt="Planet Auto Hub" width="122" height="64"></a>
  <nav class="nav" aria-label="Sections">
    <a href="#pieces">{t("Pièces", "Parts")}</a><a href="#vehicules">{t("Véhicules", "Vehicles")}</a><a href="#services">{t("Services", "Services")}</a><a href="#contact">{t("Contact", "Contact")}</a>
  </nav>
  <button class="lang" type="button" id="lang" aria-label="English / Français">EN</button>
  <a class="btn pri hd" href="{wa(W1, MSG)}" target="_blank" rel="noopener">{ic("chat")}<span>WhatsApp</span></a>
</div></header>

<main id="main">
<section class="hero" id="top"><div class="w">
  <p class="eye">{t("Pièces auto neuves · Dakar", "New auto parts · Dakar")}</p>
  {t("La bonne pièce pour votre véhicule, du premier coup.", "The right part for your vehicle, the first time.", "h1")}
  {t("Dites-nous ce que vous conduisez et ce qu'il vous faut. Nous vérifions la compatibilité, puis nous vous proposons des options selon votre budget.", "Tell us what you drive and what you need. We check fitment, then offer options to match your budget.", "p", "lead")}
  {duo()}
  <ul class="facts">
    <li><b>{t("Compatibilité vérifiée", "Fitment verified")}</b>{t("par numéro de châssis ou référence", "by chassis number or reference")}</li>
    <li><b>{t("3 niveaux de qualité", "3 quality levels")}</b>{t("origine, équivalent, économique", "genuine, OEM-quality, value")}</li>
    <li><b>{t("Rond-Point Liberté 6", "Rond-Point Liberté 6")}</b>{t("retrait en boutique ou livraison", "shop pickup or delivery")}</li>
  </ul>
</div></section>

<section id="pieces"><div class="w">
  {t("Ce que nous vendons", "What we sell", "h2")}
  {t("Des pièces neuves pour l'entretien courant et la réparation. Pas de prix en ligne : chaque pièce dépend du véhicule, demandez-nous un devis.", "New parts for routine service and repair. No prices online: every part depends on the vehicle, so ask us for a quote.", "p", "sub")}
  <div class="grid g3">{''.join(f'<article class="cell">{ic(i)}{t(a, b, "h3")}{t(c, d, "p")}</article>' for i, a, b, c, d in CATS)}</div>
  <div class="tiers">
    <div>{t("Origine", "Genuine", "h3")}{t("Pièce de marque constructeur, dans son emballage d'origine.", "Manufacturer-branded part in original packaging.", "p")}</div>
    <div>{t("Qualité équivalente", "OEM-quality", "h3")}{t("Fabricants reconnus : Bosch, Valeo, KYB, Monroe, TRW, Delphi.", "Established makers: Bosch, Valeo, KYB, Monroe, TRW, Delphi.", "p")}</div>
    <div>{t("Économique", "Value", "h3")}{t("Une alternative moins chère, choisie pour un montage correct.", "A lower-cost alternative, selected for correct fitment.", "p")}</div>
  </div>
  {duo('Bonjour Planet Auto Hub, je voudrais un devis. Pièce : … Véhicule (marque, modèle, année) : ')}
</div></section>

<section id="vehicules" class="alt"><div class="w">
  {t("Véhicules pris en charge", "Vehicles we support", "h2")}
  {t("Touchez une marque pour voir les modèles courants. Votre modèle n'est pas dans la liste ? Demandez quand même : nous commandons aussi sur demande.", "Tap a make to see common models. Model not listed? Ask anyway: we also order on request.", "p", "sub")}
  {''.join(f'<div class="grp">{t(fr, en, "h3")}<div class="grid mks">{"".join(make_card(m) for m in ms)}</div></div>' for fr, en, ms in GROUPS)}
  <p class="note">{t("Les marques et logos appartiennent à leurs propriétaires respectifs. Planet Auto Hub est un revendeur de pièces indépendant.", "Brand names and logos belong to their respective owners. Planet Auto Hub is an independent parts retailer.")}</p>
</div></section>

<section id="services"><div class="w">
  {t("Services", "Services", "h2")}
  {t("Plus qu'un comptoir : nous vous aidons à identifier la pièce, à la recevoir et à la faire monter.", "More than a counter: we help you identify the part, receive it and get it fitted.", "p", "sub")}
  <div class="grid g3">{''.join(f'<article class="cell">{ic(i)}{t(a, b, "h3")}{t(c, d, "p")}</article>' for i, a, b, c, d in SERV)}</div>
  {duo('Bonjour Planet Auto Hub, j\'ai une question sur vos services : ')}
</div></section>

<section id="commander" class="alt"><div class="w">
  {t("Comment commander", "How to order", "h2")}
  <ol class="steps">{''.join(f'<li><span class="n">{k}</span><div>{t(a, b, "h3")}{t(c, d, "p")}</div></li>' for k, (a, b, c, d) in enumerate(STEPS, 1))}</ol>
  <p class="tip">{t("Conseil : envoyez une photo de la carte grise ou du numéro de châssis, et de l'ancienne pièce. La réponse est plus rapide et plus sûre.", "Tip: send a photo of the registration card or chassis number, and of the old part. The answer is faster and more reliable.")}</p>
</div></section>

<section id="contact"><div class="w">
  {t("Contact", "Contact", "h2")}
  {t("Le plus rapide : un message WhatsApp. Nous répondons avec la disponibilité et le prix.", "Fastest way: a WhatsApp message. We reply with availability and price.", "p", "sub")}
  <div class="contact">
    <div class="lines">
      <a class="line" href="{wa(W1, MSG)}" target="_blank" rel="noopener">{ic("chat")}<span><b>{t("WhatsApp · Ligne 1", "WhatsApp · Line 1")}</b><span class="num">{P1}</span></span></a>
      <a class="line" href="{wa(W2, MSG)}" target="_blank" rel="noopener">{ic("chat")}<span><b>{t("WhatsApp · Ligne 2", "WhatsApp · Line 2")}</b><span class="num">{P2}</span></span></a>
      <p class="calls">{ic("phone")}<span>{t("Appeler :", "Call:")} <a href="tel:+{W1}">{P1}</a> · <a href="tel:+{W2}">{P2}</a></span></p>
    </div>
    <address>
      <p>{ic("pin")}<span><b>Planet Auto Hub</b><br>Rond-Point Liberté 6<br>Dakar, Sénégal</span></p>
      <a class="lnk" href="https://www.google.com/maps/search/?api=1&amp;query=Planet+Auto+Hub+Dakar&amp;query_place_id=ChIJU5wBx7hzwQ4RvJ6JFwpzVng" target="_blank" rel="noopener">{t("Ouvrir dans Google Maps", "Open in Google Maps")}</a>
      <dl class="hrs">
        <dt>{t("Lundi à jeudi", "Monday to Thursday")}</dt><dd>9h00 – 20h00</dd>
        <dt>{t("Vendredi", "Friday")}</dt><dd>9h00 – 13h30 · 14h30 – 20h00</dd>
        <dt>{t("Samedi", "Saturday")}</dt><dd>9h00 – 20h00</dd>
        <dt>{t("Dimanche", "Sunday")}</dt><dd>{t("Fermé", "Closed")}</dd>
      </dl>
      <p class="soc">TikTok : <a class="lnk" href="https://www.tiktok.com/@planetautohub" target="_blank" rel="noopener">@planetautohub</a><br>Facebook : <a class="lnk" href="https://www.facebook.com/share/1E5kXyKUvn/" target="_blank" rel="noopener">Planet Auto Hub</a><br>Instagram : <a class="lnk" href="https://www.instagram.com/planetautohub" target="_blank" rel="noopener">@planetautohub</a></p>
    </address>
  </div>
</div></section>
</main>

<footer><div class="w">
  <p><b>PLANET AUTO-HUB SUARL</b> · Rond-Point Liberté 6, Dakar, Sénégal · RCCM SN DKR 2025 B 40566 · NINEA 012552396</p>
  <p>{t("Ce site ne collecte aucune donnée personnelle : pas de formulaire, pas de cookie, pas de mesure d'audience. Vos messages WhatsApp sont traités dans WhatsApp, selon ses propres règles.", "This site collects no personal data: no forms, no cookies, no analytics. Your WhatsApp messages are handled within WhatsApp, under its own terms.")}</p>
  <p>© 2026 Planet Auto Hub</p>
</div></footer>

<a class="dock" href="{wa(W1, MSG)}" target="_blank" rel="noopener">{ic("chat")}{t("Écrire sur WhatsApp", "Message us on WhatsApp")}</a>
<script>const MSG_FR={json.dumps(MSG, ensure_ascii=False)},MSG_EN={json.dumps(MSG_EN)};{js}</script>
</body>
</html>
'''
open('../index.html', 'w', encoding='utf-8').write(out)
pass
print('built', len(out) // 1024, 'KB; makes with logo:', sum(os.path.exists(f'../assets/makes/{slug(m)}.webp') for g in GROUPS for m in g[2]), 'of', sum(len(g[2]) for g in GROUPS))
