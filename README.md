# Planet Auto Hub website

Public catalog site for Planet Auto Hub (Dakar). Static page, French first with an English toggle.
No forms, no cookies, no ads, no third-party scripts. Anonymous first-party visit counting (tools/track.js) writes one record per visit to the shop's own Firebase (collection stores/pah/web_hits), read in Jaay → Website. Visit `?notrack` once on a device to exclude it. Customers contact the shop on WhatsApp.

- `index.html` and `assets/` are the site (served by GitHub Pages from the `main` branch root at https://planetautohub.com (the `CNAME` file sets the domain)).
- `tools/build.py` rebuilds `index.html` from `tools/style.css`, `tools/app.js` and `tools/vehicles.json`. Run it from the `tools` folder.
- Car makers' names and logos belong to their respective owners.
