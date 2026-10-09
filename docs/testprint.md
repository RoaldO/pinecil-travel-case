# Testprint — plan om later op te pakken

Voordat de hele koker geprint wordt (vier onderdelen, uren printtijd), eerst
**testplakjes**: dunne plakjes (8–10 mm) uit de échte onderdelen, precies
op de plekken waar de pasvorm ertoe doet. Daar probeer je de echte punten,
bout, sleuteltje en magneetjes in, en daarna stel je de spelingen bij.

Het klittenband is hier niet voor nodig: alleen de **dikte** van de band
telt mee (in plakje 4), en die staat als aanname in het model.

## 1. Maken

```sh
make coupons
```

Dat geeft in `build/coupons/`:

- `*.stl` / `*.step` per plakje, al **rechtop gedraaid zoals het echte
  onderdeel print**: zelfde kant op het bed, zodat overhang en
  olifantenvoet kloppen. In de slicer dus niet meer draaien.
- `coupons.png` / `.svg`: van elk plakje de onder- (bed) en bovenkant.

`build/` staat niet in git: altijd opnieuw maken met `make coupons`, zeker
na een wijziging in `cad/params.py`.

## 2. Printen

| Plakje | Materiaal | Maat (mm) |
|---|---|---|
| 1-insert-a-collar | PETG | 34 × 50,5 × 10 |
| 2a-insert-a-face | PETG | 34 × 50,5 × 8 |
| 2b-shell-b-mouth | zwart PLA | 43,4 × 57,2 × 8 |
| 3-insert-b-face | PETG | 34 × 50,5 × 8 |
| 4a-shell-a-end | zwart PLA | 43,4 × 57,2 × 8 |
| 4b-insert-a-end | PETG | 34 × 50,5 × 8 |

Print met dezelfde instellingen als straks de echte onderdelen (laaghoogte,
lijnbreedte, temperatuur, filament): de spelingen gelden voor díe printer
en díe instellingen. Het model gaat uit van een 0,4-nozzle (één printlijn
≈ 0,45) en lagen van 0,2.

### Volgorde: in drie rondes, niet alles tegelijk

Een correctie in het ene plakje kan het andere veranderen; alles in één
keer printen kan dus zonde van de printtijd zijn. Wat raakt wat:

- `ITEM_CLEARANCE` (punt, bout, sleuteltje) bepaalt de maat van de
  kanalen, daarmee de hele indeling, de breedte van de inzetstukken en de
  vorm van de buitendelen → raakt **alle** plakjes.
- De printstand van de inzetstukken (zie hoofdstuk 4; de brug is inmiddels
  opgelost).
- `SLIDE_CLEARANCE` / `GLUE_CLEARANCE` raken alleen de buitendelen (2b, 4a).
- Magneetjes en trechter raken alleen de voorkanten (2a, 3).

Daarom, van grote invloed naar klein:

| Ronde | Plakjes | Waarom eerst |
|---|---|---|
| 1 | **1 + 4b** | pasvorm punten en bout (kan alles verschuiven) en of het grondvlak goed print (kan de printstand veranderen); 4b is klein en snel |
| 2 | **2a + 3** | voorkanten: magneetjes, trechter, sleuteltje, punt-einden |
| 3 | **2b + 4a** | buitendelen, pas als de vorm van de inzetstukken vastligt; de grootste plakjes |

Na elke ronde: parameters bijstellen, `make test`, `make coupons`, en alleen
opnieuw printen wat geraakt is.

## 3. Testen, per plakje

Noteer per test: past / te strak / te los, en zo mogelijk hoeveel.

### Plakje 1 — inzetstuk A bij de kraag

Snijdt door de trappen van het puntkanaal en het kanaal van de bout.

Alles gaat er **van boven** in (de kant die niet op het bed lag), net
zoals straks vanaf het snedevlak in inzetstuk A.

- [ ] **Punt**, met de witte ringen vooruit: de voet (ø 5,7) moet er
      soepel door, en de punt moet met zijn kraag blijven rusten op het
      zitvlak (de schouder). Niet klemmen, niet rammelen. Probeer alle
      vier gaten.
- [ ] **Bout**, met de basis vooruit, door het grote gat: de grafsteen moet
      er soepel door, met de platte kant (display, knopjes) naar de
      gleuf toe. Knopjes en boutje mogen nergens haken.
- [ ] Is het zitvlak van de kraag een nette schouder (geen
      olifantenvoet-randje, niet uitgezakt)?

### Plakje 2a + 2b — voorkant inzetstuk A in de mond van buitendeel B

- [ ] **2a in 2b schuiven** (2a met de bovenkant naar de mond): moet met
      de hand soepel schuiven zonder spel. Dit is straks de overlap van
      20 mm waarmee de koker open en dicht gaat.
- [ ] Helpen de afschuiningen (dun richeltje op 2a, afschuining binnen in
      de mond van 2b) om hem erin te krijgen?
- [ ] **Magneetjes** (ø 3 × 2) in de drie gaatjes van 2a: passen ze, met
      een drupje lijm? Steken ze niet uit?
- [ ] **Sleuteltje**: lange poot in het gaatje boven de bout; zie je het
      uitlijngroefje goed, ligt de haakse poot er recht boven?

### Plakje 3 — voorkant inzetstuk B

- [ ] **Magneetjes** in de drie gaatjes — **polariteit**: leg een los
      magneetje tegen het magneetje in 2a, en lijm het in 3 met dezelfde
      kant naar buiten als dat losse magneetje had. Dan trekken 2a en 3
      elkaar aan.
- [ ] Klikt 3 op 2a? Te zwak / prima / te sterk?
- [ ] **Trechter**: sleuteltje in 2a, de haakse poot een stukje
      verdraaid, en 3 er recht op drukken (de bovenkant van 3 naar 2a):
      draait de trechter de poot in het kuiltje? Tot hoeveel verdraaiing?
- [ ] Een punt met zijn werkende eind van boven in een van de kleine
      gaten (ø 6,3): past de huls (ø 5,5)?
- [ ] Bout met de punt-kant vooruit van boven in het grote gat: passen de
      gleuven voor het montageboutje (boven) en het voetje (onder)?

### Plakje 4a + 4b — uiteinde buitendeel A met het grondvlak van inzetstuk A

- [ ] **4b in 4a** met de afgeschuinde kant (bedkant) vooruit: moet er
      net in kunnen met ruimte voor lijm, niet klemmen en niet ruim
      rammelen. Zakt hij tot de eindstops (de PLA-blokjes naast de band)?
- [ ] **Onderkant van 4b**: vlak? Hoe zien de twee randen eruit waar de
      band om het inzetstuk buigt (korte overhang)? Zie hieronder.

## 4. Opgelost aandachtspunt: de brug in het grondvlak van de inzetstukken

Het klittenband loopt achter de kopse kant van de koker langs. Eerst liep
elk inzetstuk naast de band door tot de kopse kant, dus over de breedte van
de band (~20 mm) was het aan zijn buitenste uiteinde 2,3 mm korter. Omdat
de inzetstukken op dat uiteinde printen, werd dat een **brug van ~20 mm**
(ronde 1: lelijk).

**Opgelost (2026-10-09):** de stukken naast de band (de "bruggenhoofden",
tevens de eindstops) zijn nu van het **PLA-buitendeel**, vast aan de kopse
kant. Het inzetstuk eindigt overal op één vlak en print vlak op het bed —
geen brug, geen schuren of fillen meer nodig. De pasvorm verandert niet.
Wat overblijft: waar de band om de hoeken van het inzetstuk buigt
(straal 5), loopt de rand de eerste ~4 lagen steil schuin naar buiten —
een korte overhang aan twee randen.

Overwogen en niet gedaan: inzetstuk A andersom printen (dan worden de
trapjes in de puntkanalen overhangen, en voor B de trechter), of de brug
ondersteunen.

## 5. Bijstellen

Alle spelingen staan in `cad/params.py`. Waar zit het, en welke knop:

| Wat | Klacht | Parameter (nu) |
|---|---|---|
| punt in zijn kanaal, bout in zijn kanaal, gaatje sleuteltje | te strak / te los | `ITEM_CLEARANCE` (0,4, rondom) |
| ruimte rond knopjes en display van de bout | tikt / haakt | `IRON_CONTROL_CLEARANCE` (1,0 extra) |
| inzetstuk A in buitendeel B (de overlap) | schuift zwaar / spel | `SLIDE_CLEARANCE` (0,2) |
| inzetstuk in zijn eigen buitendeel (lijmen) | klemt / te ruim | `GLUE_CLEARANCE` (0,2) |
| magneetje in zijn gaatje | past niet / te los | `MAGNET_CLEARANCE` (0,1, ook extra diepte) |
| inloop overlap | haakt bij het dichtdoen | `SHELL_B_MOUTH_CHAMFER` (0,6), `INSERT_A_LEAD_IN` (0,3) |
| inzetstuk in buitendeel bij het lijmen | haakt, olifantenvoet | `INSERT_BED_CHAMFER` (0,6) |
| trechter | vangt de poot niet / te weinig | `KEY_FUNNEL_ANGLE` (20°), `KEY_FUNNEL_DEPTH` (6) |
| kuiltje van de haakse poot | klemt | `POCKET_CLEARANCE` (1,0) |

Let op: `ITEM_CLEARANCE` geldt voor **alle** voorwerpen tegelijk. Past de
punt wel maar de bout niet (of omgekeerd), dan moet die speling per
voorwerp worden opgesplitst — dat is een kleine aanpassing in de code.

Een maat van een voorwerp zelf die niet blijkt te kloppen (bijvoorbeeld
een diameter van de punt of de bout), pas je aan bij dat voorwerp in
`cad/params.py` (`TIP_*`, `IRON_*`), niet via de speling.

Daarna: `make test`, `make coupons`, en de volgende ronde (of de geraakte
plakjes opnieuw). Pas als alle plakjes passen de hele koker printen
(`make build`).

## 6. Resultaten

### Logoplaatje — PLA, 2026-10-09

Print netjes (wat stringing door vochtig weer), ribben stevig: met een
tangetje heen en weer gebogen zonder te breken. `RIB_WIDTH` 0,8 blijft.

### Ronde 1, poging 1 — plakje 1, PETG (nog niet gedroogd), 2026-10-09

Veel stringing (PETG te vroeg uit de droger), na afbramen getest:

- **Printnauwkeurigheid:** gat voor de bout gemeten **14,72**, model 14,70 —
  de printer print de gaten op maat.
- **Bout:** veel ruimte. Nagemeten: het plastic lijf is **13,78** breed, niet
  13,9 → `IRON_BODY_SECTION` aangepast (maat van het voorwerp, niet de
  speling). Speling blijft 0,4 per kant: in het echte inzetstuk glijdt de
  bout over ~64 mm, daar is wat meer ruimte nodig dan in een plakje van
  10 mm.
- **Punt:** kraag past mooi in het brede deel; de voet zit wat los →
  `TIP_BASE_CLEARANCE` 0,3 (boring ø 0,2 kleiner), kraag blijft 0,4.
- Volgende: plakje 1 opnieuw met gedroogde PETG.

### Ronde 1, poging 2 — plakje 1 + 4b, gedroogde PETG op 240 °C, 2026-10-09

- **Plakje 1: perfect.** Bout (13,78 met 0,4 per kant), voet van de punt
  (`TIP_BASE_CLEARANCE` 0,3) en kraag (0,4) passen. Deze spelingen blijven.
- **Plakje 4b: de brug is lelijk**, maar acceptabel. **Besluit:** de
  inzetstukken blijven op hun buitenste uiteinde printen; de brug wordt
  afgewerkt met filler en schuurpapier — er zit altijd klittenband voor, dus
  niemand ziet hem. **Let op:** het is de wand waar het klittenband langs
  schuift (kanaal maar 2,3 mm): **vlak** schuren en dun fillen, zodat het
  kanaal niet smaller wordt. Geldt ook voor inzetstuk B.
- Ronde 1 klaar → ronde 2 (plakje 2a + 3).

### Na ronde 1 — de brug weggewerkt, 2026-10-09

Idee van de eigenaar: de "bruggenhoofden" naast de band van PLA maken. De
stukken naast de band tussen kopse kant en inzetstuk horen nu bij het
buitendeel (eindstops); het inzetstuk print vlak. Het besluit hierboven
(schuren en fillen) vervalt. **4b opnieuw printen** (en 4a hoort er nu bij
in ronde 3: daarin zitten de eindstops).

### Ronde 2 — plakje 2a + 3, PETG 240 °C, 2026-10-09

- **Geen aanpassingen nodig.** Magneetjes zien er goed uit.
- **Uitlijngroefje:** breed en diep genoeg, maar pas goed zichtbaar met een
  **viltstift** erin → toegevoegd aan de montage.
- **Naad (seam):** stond overal op dezelfde plek en maakt daardoor een paar
  sneetjes in het werkstuk → in de slicer de naad **met de hand plaatsen**
  (seam painting, op een plek die niet telt) of op **willekeurig** zetten.
  Geldt voor alle onderdelen.
- Volgende: ronde 3 (2b + 4a, PLA) en 4b opnieuw (PETG, nu zonder brug).

### Printinstellingen PETG

| Instelling | Was | Nu | Waarom |
|---|---|---|---|
| spuittemperatuur (alle lagen) | 250 °C | **240 °C** | stringing; 250 is bovenin het bereik van PETG |
| naad (seam) | uitgelijnd | **met de hand / willekeurig** | een uitgelijnde naad gaf sneetjes in het werkstuk (ronde 2); geldt ook voor PLA |

Eén knop tegelijk. Na de print: breekt het plakje makkelijk tussen twee
lagen, dan is het te koud → 245 °C. Nog veel stringing → volgende knop is
de retractie. Wat hier uitkomt, gebruik je ook voor de echte inzetstukken.

**Uitslag (ronde 1, poging 2):** met gedroogde PETG op 240 °C is de
laaghechting geweldig en is de stringing weg. **240 °C blijft**, ook voor
de echte inzetstukken. De naad (seam) is niet perfect, maar even schuren is
genoeg: de buitenkant van de inzetstukken wordt tegen het PLA gelijmd.
