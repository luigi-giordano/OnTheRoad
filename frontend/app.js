/* =========================================================
   OnTheRoad — app.js
   Logica client-side: dati, auth, nav, footer, utilities
   ========================================================= */
"use strict";

/* ─────────────────────────────────────────────────────────
   HELPERS
───────────────────────────────────────────────────────── */

function escapeHtml(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatKm(km) {
  if (km == null || km === "") return "—";
  return Number(km).toLocaleString("it-IT") + "\u202fkm";
}

function toast(msg, type = "default") {
  let el = document.getElementById("__toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "__toast";
    el.className = "toast";
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = "toast" + (type === "error" ? " toast-error" : "");
  requestAnimationFrame(() =>
    requestAnimationFrame(() => el.classList.add("show"))
  );
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove("show"), 3000);
}

function requireAuth() {
  if (!Auth.current()) {
    location.href =
      "login.html?next=" + encodeURIComponent(location.pathname + location.search);
    return false;
  }
  return true;
}

/* ─────────────────────────────────────────────────────────
   ICONS — SVG inline Feather-style
───────────────────────────────────────────────────────── */

const ICONS = {
  cal: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
  road: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>`,
  pin: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
  clock: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  bed: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="vertical-align:-2px;flex-shrink:0"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>`,
};

/* ─────────────────────────────────────────────────────────
   SAMPLE ITINERARIES
───────────────────────────────────────────────────────── */

const SAMPLE_ITINERARIES = [
  /* ── 1. NORVEGIA ─────────────────────────────────── */
  {
    id: "norvegia-fiordi",
    title: "Norvegia — La Rotta dei Fiordi",
    country: "Norvegia",
    duration: "12 giorni",
    days: 12,
    distance: 3100,
    difficulty: "Avanzata",
    season: "Giugno – Agosto",
    price: 109,
    cover:
      "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=900&q=80",
    summary:
      "Da Bergen al Trollstigen passando per i fiordi più selvaggi della Norvegia: Hardangerfjord, Nærøyfjord e Geirangerfjord. Strade tortuose, traghetti obbligatori e panorami che fanno dimenticare le salite.",
    stops: [
      {
        name: "Bergen",
        km: 0,
        hours: "",
        nights: 2,
        transport: ["Volo + Moto"],
        notes:
          "Punto di partenza ideale. Passeggia tra le case di legno di Bryggen (Patrimonio UNESCO) e fai rifornimento — le stazioni di servizio si rarefanno sulle strade dei fiordi.",
        photos: [
          "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Hardangerfjord",
        km: 190,
        hours: "3h 30m",
        nights: 1,
        transport: ["Moto", "Traghetto Utne–Kvanndal"],
        notes:
          "Il fjord più lungo d'Europa dopo il Sognefjord. Il traghetto Utne–Kvanndal (20 min) taglia la rotta e regala viste impossibili da fare su strada.",
        photos: [
          "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Flåm e Nærøyfjord",
        km: 160,
        hours: "2h 45m",
        nights: 1,
        transport: ["Moto", "Traghetto Flåm–Gudvangen"],
        notes:
          "Il Nærøyfjord è Patrimonio UNESCO. Il traghetto Flåm–Gudvangen è uno dei più belli del mondo — prenotalo con almeno 3 settimane di anticipo in estate.",
        photos: [
          "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Geirangerfjord",
        km: 280,
        hours: "4h 30m",
        nights: 2,
        transport: ["Moto", "Traghetto"],
        notes:
          "Il fjord più fotografato della Norvegia. La strada Ørnesvingen (il Volo dell'Aquila) sale 11 tornanti con vista diretta sull'acqua a 620m sotto.",
        photos: [
          "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Ålesund",
        km: 120,
        hours: "2h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Città art nouveau ricostruita dopo l'incendio del 1904. Panorama dal monte Aksla al tramonto (418 gradini — vale ogni passo). Ottima base per la notte.",
        photos: [],
      },
      {
        name: "Trollstigen",
        km: 150,
        hours: "3h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "La 'Scala del Troll': 11 tornanti al 9% di pendenza con cascata inclusa. Aperta solo da maggio a ottobre. Fermati al belvedere prima di scendere — vedrai tutto il serpentone.",
        photos: [
          "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Trondheim",
        km: 240,
        hours: "4h",
        nights: 2,
        transport: ["Moto"],
        notes:
          "Ultima tappa con la cattedrale di Nidaros e il quartiere di Bakklandet. Da qui volo di ritorno o navigazione verso la Danimarca.",
        photos: [],
      },
    ],
    documents: [
      "Carta d'identità o passaporto valido (UE sufficiente)",
      "Patente di guida A",
      "Carta verde assicurativa moto",
      "Carta di credito — i pedaggi autostradali si pagano in contanti o contactless",
    ],
    vaccinations: ["Nessuna obbligatoria per la Norvegia"],
    tips: [
      "Prenota i traghetti con almeno 3 settimane di anticipo in luglio-agosto",
      "Le stazioni Esso e Circle K accettano carte internazionali — porta contante solo per le zone remote",
      "Il meteo cambia in 20 minuti: impermeabile sempre in borsa accessibile",
      "In estate sopra il Circolo Polare la notte non esiste — porta una mascherina per dormire",
      "Benzina cara: fai il pieno ogni volta che ne hai l'occasione",
    ],
  },

  /* ── 2. MAROCCO ──────────────────────────────────── */
  {
    id: "marocco-atlante-sahara",
    title: "Marocco — Atlante, Dunes e Medine",
    country: "Marocco",
    duration: "10 giorni",
    days: 10,
    distance: 2200,
    difficulty: "Media",
    season: "Marzo – Maggio, Settembre – Ottobre",
    price: 89,
    cover:
      "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=900&q=80",
    summary:
      "Dall'Atlantico alle dune di Erg Chebbi attraversando i passi dell'Alto Atlante. Un viaggio che mescola medine imperiali, kasbah di terra rossa e tramonti nel deserto che sembrano rubati a un film.",
    stops: [
      {
        name: "Casablanca",
        km: 0,
        hours: "",
        nights: 1,
        transport: ["Volo + Moto a noleggio"],
        notes:
          "Solo tappa logistica. Ritira la moto, fai la spesa di acqua e snack. La moschea di Hassan II vale la visita la sera — è la terza più grande del mondo e si affaccia sull'Oceano.",
        photos: [],
      },
      {
        name: "Fès",
        km: 310,
        hours: "4h",
        nights: 2,
        transport: ["Moto"],
        notes:
          "La medina di Fès el-Bali è Patrimonio UNESCO. Parcheggia la moto all'esterno delle mura — dentro sono i viottoli più stretti che tu abbia mai visto. Le concerie di pelle (tannerie) si vedono meglio dall'alto dei negozi.",
        photos: [
          "https://images.unsplash.com/photo-1539650116574-75c0c6d73f6e?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Ifrane e Midelt",
        km: 230,
        hours: "3h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Ifrane sembra una cartolina svizzera nel bel mezzo del Marocco — costruita dai Francesi negli anni '30. Midelt è l'ultima città 'normale' prima del deserto: fa il pieno e porta acqua extra.",
        photos: [],
      },
      {
        name: "Erg Chebbi — le dune di Merzouga",
        km: 310,
        hours: "4h",
        nights: 2,
        transport: ["Moto", "Dromedario"],
        notes:
          "Le dune di Erg Chebbi arrivano a 150 m di altezza. Lascia la moto all'hotel e fai l'ultima parte su dromedario o in quad. Dormita in bivacco nel deserto: obbligatoria.",
        photos: [
          "https://images.unsplash.com/photo-1509316785289-025f5b846b35?auto=format&fit=crop&w=600&q=75",
          "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Todra Gorge e Vallée des Roses",
        km: 190,
        hours: "3h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Le gole del Todra: pareti di roccia alte 300m che si stringono fino a 10m. Spettacolo naturale incredibile, strade perfette per la moto. La Vallée des Roses fiorisce in aprile.",
        photos: [
          "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Ouarzazate — la Hollywood africana",
        km: 220,
        hours: "3h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Qui hanno girato il Gladiatore, Il Trono di Spade e la Mummia. Fermati agli Atlas Studios. La kasbah di Aït-Ben-Haddou (10 km) è Patrimonio UNESCO — vale la deviazione.",
        photos: [],
      },
      {
        name: "Marrakech",
        km: 230,
        hours: "3h",
        nights: 2,
        transport: ["Moto"],
        notes:
          "Parcheggia la moto in un garage custodito (chiedi all'hotel). Jemaa el-Fna la sera è un palcoscenico a cielo aperto: acrobati, incantatori di serpenti, cucina di strada. I souq per il giorno dopo.",
        photos: [
          "https://images.unsplash.com/photo-1573843981267-be1ce0e3cf93?auto=format&fit=crop&w=600&q=75",
        ],
      },
    ],
    documents: [
      "Passaporto con almeno 6 mesi di validità residua",
      "Patente di guida internazionale (obbligatoria)",
      "Carta verde assicurativa moto valida per il Marocco",
      "Documento di circolazione della moto",
    ],
    vaccinations: [
      "Epatite A (consigliata)",
      "Tetano (richiamo se scaduto da più di 10 anni)",
      "Febbre tifoidea (consigliata per chi mangia ai mercati locali)",
    ],
    tips: [
      "Non portare la moto nella medina — solo le moto locali ci passano ed è stressante",
      "Cambia in banca o ATM Attijariwafa: i tassi aeroportuali sono pessimi",
      "In inverno le strade dell'Atlante possono avere neve — controlla le condizioni prima",
      "Il carburante non è disponibile ovunque nel deserto: fai sempre il pieno al massimo",
      "Tratta il prezzo nei souq: il primo prezzo è sempre il doppio del reale",
    ],
  },

  /* ── 3. ALBANIA ──────────────────────────────────── */
  {
    id: "albania-loop",
    title: "Albania Loop — Costa e Montagne",
    country: "Albania",
    duration: "9 giorni",
    days: 9,
    distance: 1900,
    difficulty: "Facile",
    season: "Maggio – Settembre",
    price: 59,
    cover:
      "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80",
    summary:
      "L'Albania è il segreto meglio tenuto d'Europa in moto. Coste cristalline, città ottomane, montagne che sembrano Dolomiti e prezzi da anni '90. Ho percorso la riviera con 300cc senza alcun problema.",
    stops: [
      {
        name: "Tirana",
        km: 0,
        hours: "",
        nights: 1,
        transport: ["Volo + Moto"],
        notes:
          "Tirana è cambiata moltissimo nell'ultimo decennio. Prendi un gelato in Blloku e cena a base di tavë kosi — il piatto nazionale. Prezzi bassissimi, cibo ottimo.",
        photos: [],
      },
      {
        name: "Berat — la città delle mille finestre",
        km: 120,
        hours: "2h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Patrimonio UNESCO. Le case ottomane con le finestre ad arco bianche si arrampicano sulla collina. La rocca in cima al colle apre alle 7 — arrivaci all'alba per evitare le comitive.",
        photos: [
          "https://images.unsplash.com/photo-1555993539-1732b0258235?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Saranda",
        km: 220,
        hours: "3h 30m",
        nights: 2,
        transport: ["Moto", "Traghetto per Corfù (opzionale)"],
        notes:
          "La 'piccola Corfù' albanese. Il traghetto da Saranda per Corfù dura 20 minuti e costa circa €20. Di sera il lungomare con i bar aperti fino alle 3 è imperdibile.",
        photos: [
          "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Riviera Albanese — Himarë",
        km: 100,
        hours: "2h",
        nights: 2,
        transport: ["Moto"],
        notes:
          "La SH8 da Saranda a Vlorë è una delle strade costiere più belle d'Europa. Fermate obbligatorie: Gjipe, Dhërmi, Palasë. Himarë è il centro base ideale con spiagge a 5 minuti.",
        photos: [
          "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=75",
          "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Gjirokastër",
        km: 90,
        hours: "1h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Altra città Patrimonio UNESCO. Il castello ottomano con dentro un aereo americano abbattuto (storia vera) e la città 'di pietra' sopra il vallone. Dormita in una guesthouse storica.",
        photos: [
          "https://images.unsplash.com/photo-1555993539-1732b0258235?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Tirana (rientro via Passo di Llogarasë)",
        km: 250,
        hours: "4h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Rientro via il passo di Llogarasë a 1027m con vista mare da entrambi i lati. Poi le montagne interne del Tomor. Strade in buone condizioni per il 90% del percorso.",
        photos: [],
      },
    ],
    documents: [
      "Carta d'identità valida (UE sufficiente per 90 giorni)",
      "Patente di guida A",
      "Carta verde assicurativa moto (l'Albania richiede la Green Card)",
      "Documento di circolazione della moto",
    ],
    vaccinations: [
      "Epatite A (consigliata)",
      "Tetano (richiamo)",
    ],
    tips: [
      "SIM locale: Telekom Albania ~€5 con 10 GB — ottima per la navigazione offline",
      "Le strade della riviera sono ottime, quelle interne a volte a buche — guida con calma",
      "ATM: usa Raiffeisen o Credins Bank — commissioni più basse",
      "Cibo straordinariamente economico: 20€ bastano per una cena completa con vino per due",
      "Attenzione al gasolio — la moto ha bisogno di benzina, non di gasolio: stazioni ovunque sulla costa",
    ],
  },

  /* ── 4. DOLOMITI ─────────────────────────────────── */
  {
    id: "dolomiti-tirolo",
    title: "Dolomiti e Stelvio",
    country: "Italia / Austria",
    duration: "7 giorni",
    days: 7,
    distance: 1250,
    difficulty: "Media",
    season: "Giugno – Settembre",
    price: 69,
    cover:
      "https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=900&q=80",
    summary:
      "Sette giorni di passi alpini tra i più belli d'Europa: Pordoi, Gardena, Stelvio e il Gran Paradiso. Tornanti, neve (anche in luglio sopra i 2500 m) e rifugi dove il capriolo è sempre in menù.",
    stops: [
      {
        name: "Bolzano",
        km: 0,
        hours: "",
        nights: 1,
        transport: ["Treno/Auto + Moto"],
        notes:
          "Base logistica con ottima rete di servizi. Visita l'Ötzi al museo della città — è il reperto umano meglio conservato del mondo. I mercati del centro sono perfetti per fare scorta di speck.",
        photos: [],
      },
      {
        name: "Passo Pordoi e Passo Gardena",
        km: 180,
        hours: "4h (soste incluse)",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Il Pordoi a 2239m: 33 tornanti e vista sulle Dolomiti da mozzare il fiato. Il Gardena a 2121m ti porta nel cuore della Val Gardena. Non aver fretta — i belvedere sono troppo belli.",
        photos: [
          "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=600&q=75",
          "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Cortina d'Ampezzo",
        km: 90,
        hours: "2h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "La 'Regina delle Dolomiti'. Pernotta fuori centro per risparmiare — in luglio/agosto i prezzi in centro sono assurdi. Domani si sale al Passo Tre Croci prima delle folle.",
        photos: [
          "https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Passo Stelvio — il tetto d'Europa",
        km: 250,
        hours: "5h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Il Passo Stelvio a 2757m con 48 tornanti è il passo asfaltato più alto d'Europa. Attenzione al meteo: può nevicare anche in agosto. Giacca impermeabile obbligatoria — anche in piena estate.",
        photos: [
          "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Aosta e Valle del Gran Paradiso",
        km: 220,
        hours: "3h 30m",
        nights: 2,
        transport: ["Moto"],
        notes:
          "La Valle d'Aosta con il Parco Nazionale del Gran Paradiso. Fermata a Cogne per uno strudel (sì, sono valdostani di cuore) e poi su verso Valsavarenche — se hai fortuna vedi gli stambecchi.",
        photos: [],
      },
    ],
    documents: [
      "Carta d'identità o passaporto (UE sufficiente per Austria/Italia)",
      "Patente di guida A",
      "Carta verde assicurativa moto",
      "Vignetta autostradale Austria — €10 per 10 giorni, obbligatoria anche in moto",
    ],
    vaccinations: ["Nessuna obbligatoria"],
    tips: [
      "I passi chiudono spesso a maggio per neve — controlla pass-report.at prima di partire",
      "In luglio/agosto i passi più noti sono affollati: parti prima delle 8 per evitare le code",
      "Benzina: sull'Autobahn austriaca i prezzi sono più alti — fai il pieno in Italia",
      "Il meteo alpino cambia in 20 minuti: kit impermeabile sempre accessibile, non in fondo alla borsa",
      "Hotel a Cortina: prenota con almeno 3 settimane di anticipo in estate",
    ],
  },

  /* ── 5. BALCANI ──────────────────────────────────── */
  {
    id: "balcani-occidentali",
    title: "Balcani Occidentali — Plitvice, Kotor, Sarajevo",
    country: "Slovenia / Croazia / Bosnia / Montenegro",
    duration: "14 giorni",
    days: 14,
    distance: 3200,
    difficulty: "Media",
    season: "Maggio – Settembre",
    price: 119,
    cover:
      "https://images.unsplash.com/photo-1467269204594-9661b134dd2b?auto=format&fit=crop&w=900&q=80",
    summary:
      "Un arco attraverso quattro paesi: dalle Alpi Giulie ai canyon del Montenegro, dai laghi di Plitvice al caffè bosniaco di Sarajevo. L'itinerario che fa capire quanto è piccola l'Europa e quanto è varia.",
    stops: [
      {
        name: "Trieste → Ljubljana",
        km: 120,
        hours: "2h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Ljubljana è la capitale europea più sottovalutata. Il castello, il mercato di Pogačar e i ponti di Plečnik valgono almeno mezza giornata. Musei gratuiti il primo domenica del mese.",
        photos: [],
      },
      {
        name: "Lago di Bled e Bohinj",
        km: 80,
        hours: "1h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Il lago di Bled con l'isolotto e il castello è una delle cartoline più famose d'Europa. Meno conosciuto ma più selvaggio: il lago di Bohinj, 25 km a ovest. Fai Bled alle 7 di mattina prima delle carovane.",
        photos: [
          "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Laghi di Plitvice",
        km: 300,
        hours: "4h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "16 laghi collegati da cascate, tutto Patrimonio UNESCO. Entra all'apertura (8:00) — a mezzogiorno il parco è al limite della capienza. Il biglietto online si acquista settimane prima in estate.",
        photos: [
          "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Spalato (Split)",
        km: 230,
        hours: "3h",
        nights: 2,
        transport: ["Moto", "Traghetto per Hvar (opzionale)"],
        notes:
          "Il Palazzo di Diocleziano: 1700 anni e ancora ci vivono dentro. Split è viva, autentica, piena di storia. Base ideale per la gita in traghetto a Hvar (50 min).",
        photos: [
          "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Mostar",
        km: 230,
        hours: "3h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Il Stari Most — il Vecchio Ponte ottomano ricostruito — è uno dei simboli di resilienza dei Balcani. Entra nella città vecchia di sera, quando i tour operator se ne sono andati.",
        photos: [
          "https://images.unsplash.com/photo-1573843981267-be1ce0e3cf93?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Bocche di Kotor (Montenegro)",
        km: 220,
        hours: "3h",
        nights: 2,
        transport: ["Moto"],
        notes:
          "Le Bocche di Kotor — il fiordo più meridionale d'Europa. La strada panoramica sopra la baia è una delle più belle del Mediterraneo. Le mura medievali di Kotor si scalano in 30 minuti.",
        photos: [
          "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Sarajevo",
        km: 280,
        hours: "4h",
        nights: 2,
        transport: ["Moto"],
        notes:
          "La città dove è iniziato il Novecento. La Baščaršija, il Tunnel della speranza e il caffè bosniaco al mattino: Sarajevo è una delle esperienze umane più forti di questo itinerario.",
        photos: [],
      },
      {
        name: "Zagabria (rientro)",
        km: 410,
        hours: "5h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Rientro via l'autostrada A1 croata. Zagabria merita una passeggiata serale nella città alta (Gornji Grad) prima del volo.",
        photos: [],
      },
    ],
    documents: [
      "Carta d'identità o passaporto valido",
      "Carta verde assicurativa moto — obbligatoria per Bosnia e Montenegro",
      "Patente di guida A",
      "Vignetta Slovenia — €15 settimanale, obbligatoria",
    ],
    vaccinations: [
      "Epatite A (consigliata)",
      "Tetano (richiamo)",
    ],
    tips: [
      "Plitvice: biglietti online obbligatori in luglio/agosto — acquista almeno 2 settimane prima",
      "In Bosnia le strade sono buone ma i dossi rallentatori in paese sono altissimi — rallenta",
      "Montenegro: radar fissi sulla A1 — rispetta i limiti, le multe sono salate",
      "Bosnia non è UE: hai bisogno del green card assicurativo specifico (non la carta verde italiana standard)",
      "Cambio euro → marco bosniaco: solo in banca o ATM, non ai bordi strada",
    ],
  },

  /* ── 6. CORSICA ──────────────────────────────────── */
  {
    id: "corsica",
    title: "Corsica — L'Isola Selvaggia",
    country: "Francia (Corsica)",
    duration: "6 giorni",
    days: 6,
    distance: 920,
    difficulty: "Facile",
    season: "Maggio – Ottobre",
    price: 49,
    cover:
      "https://images.unsplash.com/photo-1583422409516-2895a77efded?auto=format&fit=crop&w=900&q=80",
    summary:
      "Un'isola che ha tutto: mare caraibico a nord, macchia mediterranea che profuma a venti metri, foreste di castagni e strade che ogni motociclista vorrebbe vedere almeno una volta. La D81 e la D84 non si dimenticano.",
    stops: [
      {
        name: "Bastia",
        km: 0,
        hours: "",
        nights: 1,
        transport: ["Traghetto da Livorno/Genova + Moto"],
        notes:
          "Porta nord della Corsica. Traghetto da Livorno con Corsica Ferries (5-6h) o Genova (10h notturno). Prenota la cabina: dormire sul traghetto è il modo migliore per arrivare riposati.",
        photos: [],
      },
      {
        name: "Cap Corse",
        km: 130,
        hours: "3h (soste incluse)",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Il dito che punta verso la Liguria. La D80 gira tutto il promontorio con vedute su entrambi i lati. Fermata a Nonza per la spiaggia di ciottoli neri (unica in Europa).",
        photos: [
          "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Calvi e la Balagne",
        km: 150,
        hours: "2h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "La Balagne è la 'Toscana corsa': ulivi, borghi di pietra e panorami sul Golfo di Calvi. La cittadella genovese di Calvi domina la baia — spettacolo al tramonto.",
        photos: [
          "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Porto e le Calanche",
        km: 100,
        hours: "2h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Le Calanches di Piana sono Patrimonio UNESCO: rocce di granito rosso che precipitano nel mare. La D81 qui è stretta, panoramica e richiede attenzione. Porto è piccola ma perfetta per la notte.",
        photos: [
          "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Ajaccio",
        km: 90,
        hours: "1h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "La capitale e città natale di Napoleone. Passeggia in rue Fesch, visita la cattedrale e pranza in uno dei brasserie del mercato. La sera: lungomare con vista golfo.",
        photos: [],
      },
      {
        name: "Bonifacio",
        km: 130,
        hours: "2h",
        nights: 1,
        transport: ["Moto", "Traghetto per Sardegna (opzionale)"],
        notes:
          "La città costruita sull'orlo di una falesia bianca che precipita nel mare — l'immagine più iconica della Corsica. Da qui traghetto per la Sardegna (45 min) o rientro a Bastia/Porto Vecchio.",
        photos: [
          "https://images.unsplash.com/photo-1583422409516-2895a77efded?auto=format&fit=crop&w=600&q=75",
        ],
      },
    ],
    documents: [
      "Carta d'identità o passaporto (Francia, UE)",
      "Patente di guida A",
      "Documento assicurativo moto",
    ],
    vaccinations: ["Nessuna obbligatoria"],
    tips: [
      "Traghetto: prenota con 4-6 settimane di anticipo in estate — le stive per le moto si esauriscono presto",
      "Benzina cara come nel resto della Francia — fai pieno prima di imbarcarti",
      "Le strade nel Niolo (interno) sono strette: passano due auto, non due TIR",
      "Vento forte: non raro sul Golfo di Ajaccio — attenzione alle raffiche laterali",
      "Ristoranti: il charcuterie corso (lonzu, coppa, figatellu) va ordinato sempre",
    ],
  },

  /* ── 7. TURCHIA ──────────────────────────────────── */
  {
    id: "turchia-costa-egea",
    title: "Turchia — Costa Egea e Via Licia",
    country: "Turchia",
    duration: "11 giorni",
    days: 11,
    distance: 2500,
    difficulty: "Avanzata",
    season: "Aprile – Giugno, Settembre – Ottobre",
    price: 99,
    cover:
      "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=900&q=80",
    summary:
      "Dall'Egeo alla Via Licia seguendo la costa più bella del Mediterraneo orientale. Rovine greche, calette turchesi, hammam e il tè alla turca ogni mattina. L'itinerario più logisticamente impegnativo — ma anche il più indimenticabile.",
    stops: [
      {
        name: "Istanbul",
        km: 0,
        hours: "",
        nights: 2,
        transport: ["Volo + Moto a noleggio"],
        notes:
          "Almeno 2 giorni: Sultanahmet (Hagia Sophia, Topkapi, Gran Bazaar), poi traversata in traghetto sul Bosforo verso Üsküdar. Noleggio moto: porta la patente internazionale — obbligatoria.",
        photos: [
          "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Çanakkale e Troia",
        km: 320,
        hours: "4h 30m",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Passando per la costa del Mar di Marmara. Troia è piccola ma immaginare Achille e Ettore qui ha il suo fascino. Çanakkale ha buoni ristoranti di pesce sul lungomare.",
        photos: [],
      },
      {
        name: "Efeso (Selçuk)",
        km: 430,
        hours: "6h",
        nights: 2,
        transport: ["Moto"],
        notes:
          "Efeso è uno dei siti archeologi più impressionanti del Mediterraneo — 10 km di strada romana tra templi, biblioteche e terme. Alloggia a Selçuk, non a Kuşadası (troppo turistico).",
        photos: [
          "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Bodrum",
        km: 230,
        hours: "3h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Il Castello di San Pietro (oggi museo sottomarino), il porto bianco e le barche gulet. Bodrum è cara e turistica — usala come tappa, non come base.",
        photos: [],
      },
      {
        name: "Fethiye e Ölüdeniz",
        km: 240,
        hours: "3h 30m",
        nights: 2,
        transport: ["Moto", "Barca"],
        notes:
          "La Laguna Blu di Ölüdeniz — probabilmente la spiaggia più bella della Turchia. Da Fethiye si noleggia una barca per la gita delle 12 Isole: un giorno in mare tra baie cristalline.",
        photos: [
          "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=75",
        ],
      },
      {
        name: "Kaş",
        km: 150,
        hours: "2h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Kaş è un gioiello: strade strette, bar sul porto, gente che parla 10 lingue. Visita le tombe lyciane nel mezzo del paese — sono letteralmente nei giardini delle case.",
        photos: [],
      },
      {
        name: "Antalya",
        km: 220,
        hours: "3h",
        nights: 1,
        transport: ["Moto"],
        notes:
          "Fine del tratto Licio. La città vecchia Kaleiçi con le mura romane e le case ottomane è nel mezzo di una città moderna da 2 milioni di abitanti. Da qui volo di ritorno.",
        photos: [],
      },
    ],
    documents: [
      "Passaporto con almeno 6 mesi di validità residua",
      "e-Visa obbligatoria per gli italiani — richiedi su evisa.gov.tr almeno 3 giorni prima",
      "Patente internazionale (obbligatoria per il noleggio)",
      "Assicurazione moto valida in Turchia o polizza locale",
    ],
    vaccinations: [
      "Epatite A (consigliata)",
      "Tetano (richiamo)",
      "Epatite B (consigliata per soggiorni lunghi)",
    ],
    tips: [
      "e-Visa: fai richiesta almeno 3 giorni prima — si ottiene in 24-48h e costa ~€30",
      "Lira turca: usa ATM Garanti o İş Bankası per tassi migliori",
      "Benzina molto economica rispetto all'Europa",
      "Estate: luglio-agosto sulla costa Egea fa 40°C — primavera e autunno sono ideali",
      "SIM turca Turkcell o Vodafone 10 GB a ~€15 — imprescindibile per mappe offline",
    ],
  },
];

/* ─────────────────────────────────────────────────────────
   ITINERARIES MODULE
───────────────────────────────────────────────────────── */

const Itineraries = (() => {
  const LS_KEY = "otr_user_itineraries";

  function _loadUser() {
    try {
      return JSON.parse(localStorage.getItem(LS_KEY) || "[]");
    } catch {
      return [];
    }
  }

  return {
    all() {
      return [...SAMPLE_ITINERARIES, ..._loadUser()];
    },
    byId(id) {
      return this.all().find((it) => it.id === id) || null;
    },
    userItinerariesByEmail(email) {
      return _loadUser().filter((it) => it.authorEmail === email);
    },
    saveUserItinerary(itin) {
      const list = _loadUser();
      list.push(itin);
      localStorage.setItem(LS_KEY, JSON.stringify(list));
    },
  };
})();

/* ─────────────────────────────────────────────────────────
   AUTH MODULE
───────────────────────────────────────────────────────── */

const Auth = (() => {
  const USERS_KEY = "otr_users";
  const SESSION_KEY = "otr_session";

  function _loadUsers() {
    try {
      return JSON.parse(localStorage.getItem(USERS_KEY) || "[]");
    } catch {
      return [];
    }
  }

  function _saveUsers(users) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
  }

  return {
    current() {
      try {
        const email = localStorage.getItem(SESSION_KEY);
        if (!email) return null;
        return _loadUsers().find((u) => u.email === email) || null;
      } catch {
        return null;
      }
    },
    login({ email, password }) {
      const users = _loadUsers();
      const user = users.find(
        (u) => u.email === email && u.password === password
      );
      if (!user) throw new Error("Email o password non corretti.");
      localStorage.setItem(SESSION_KEY, email);
      return user;
    },
    register({ name, email, password }) {
      const users = _loadUsers();
      if (users.find((u) => u.email === email))
        throw new Error("Questa email è già registrata.");
      if (password.length < 6)
        throw new Error("La password deve essere di almeno 6 caratteri.");
      const user = { name, email, password };
      users.push(user);
      _saveUsers(users);
      localStorage.setItem(SESSION_KEY, email);
      return user;
    },
    logout() {
      localStorage.removeItem(SESSION_KEY);
    },
  };
})();

/* ─────────────────────────────────────────────────────────
   NAV
───────────────────────────────────────────────────────── */

function renderNav(active) {
  const user = Auth.current();

  const links = [
    { id: "home",      href: "index.html",     label: "Home" },
    { id: "itinerari", href: "itinerari.html",  label: "Itinerari" },
    { id: "offerte",   href: "offerte.html",    label: "Offerte" },
    { id: "chi-siamo", href: "chi-siamo.html",  label: "Chi siamo" },
    { id: "faq",       href: "faq.html",        label: "FAQ" },
  ];

  const navLinksHtml = links
    .map(
      (l) =>
        `<a href="${l.href}"${active === l.id ? ' class="is-active"' : ""}>${l.label}</a>`
    )
    .join("");

  const ctaHtml = user
    ? `<span class="muted" style="font-size:.88rem; white-space:nowrap;">Ciao, ${escapeHtml(user.name)}</span>
       <a href="profilo.html" class="btn btn-outline btn-sm">Profilo</a>
       <button class="btn btn-ghost btn-sm" id="navLogout">Esci</button>`
    : `<a href="login.html" class="btn btn-ghost btn-sm">Accedi</a>
       <a href="registrati.html" class="btn btn-primary btn-sm">Registrati</a>`;

  const hamburger = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>`;

  const nav = document.createElement("nav");
  nav.className = "nav";
  nav.setAttribute("aria-label", "Navigazione principale");
  nav.innerHTML = `
    <div class="container nav-inner">
      <a href="index.html" class="brand" aria-label="OnTheRoad — torna alla home">
        <span class="brand-dot"></span> OnTheRoad
      </a>
      <div class="nav-links" id="navLinks" role="list">
        ${navLinksHtml}
      </div>
      <div class="nav-cta">${ctaHtml}</div>
      <button class="menu-toggle" id="menuToggle" aria-label="Apri menu" aria-expanded="false" aria-controls="navLinks">
        ${hamburger}
      </button>
    </div>`;

  document.body.prepend(nav);

  // Mobile toggle
  document.getElementById("menuToggle").addEventListener("click", function () {
    const links = document.getElementById("navLinks");
    const isOpen = links.classList.toggle("is-open");
    this.setAttribute("aria-expanded", String(isOpen));
  });

  // Logout button
  const logoutBtn = document.getElementById("navLogout");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      Auth.logout();
      toast("Disconnesso.");
      setTimeout(() => (location.href = "index.html"), 500);
    });
  }
}

/* ─────────────────────────────────────────────────────────
   FOOTER
───────────────────────────────────────────────────────── */

function renderFooter() {
  const year = new Date().getFullYear();
  const footer = document.createElement("footer");
  footer.className = "footer";
  footer.innerHTML = `
    <div class="container">
      <div class="footer-grid">
        <div>
          <a href="index.html" class="brand" style="display:inline-flex; margin-bottom:12px;">
            <span class="brand-dot"></span> OnTheRoad
          </a>
          <p style="margin-top:14px; max-width:260px; font-size:.92rem;">
            Itinerari in moto raccontati da chi ci è stato davvero.
            Niente blog patinati, solo strade vere.
          </p>
        </div>
        <div>
          <h4>Esplora</h4>
          <ul>
            <li><a href="itinerari.html">Tutti gli itinerari</a></li>
            <li><a href="offerte.html">Pacchetti know-how</a></li>
            <li><a href="registrati.html">Carica il tuo viaggio</a></li>
          </ul>
        </div>
        <div>
          <h4>Progetto</h4>
          <ul>
            <li><a href="chi-siamo.html">Chi siamo</a></li>
            <li><a href="faq.html">FAQ</a></li>
            <li><a href="chi-siamo.html#contattami">Contattaci</a></li>
          </ul>
        </div>
        <div>
          <h4>Account</h4>
          <ul>
            <li><a href="registrati.html">Crea account gratis</a></li>
            <li><a href="login.html">Accedi</a></li>
            <li><a href="profilo.html">La tua area</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© ${year} OnTheRoad — Tutti i diritti riservati.</span>
        <span>Fatto con passione da Mattia — base Bergamo 🧡</span>
      </div>
    </div>`;
  document.body.appendChild(footer);
}
