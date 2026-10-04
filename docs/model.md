# Het model in gewone taal

Dit document beschrijft wat de travel case is en hoe het model in elkaar zit,
zonder code. Het groeit mee met het model: verandert er iets aan de vorm, dan
verandert het hier ook. Alle getallen hieronder zijn **startwaarden van
parameters** (in `cad/params.py`), geen vaste maten.

## Wat het is

Een koker om een Pinecil V2 soldeerbout mee op reis te nemen, samen met vier
reservepunten en het inbussleuteltje voor de M2-boutjes van de punten. De koker
past op een printbed van 18 × 18 cm met 18 cm printhoogte, doordat hij in
stukken geprint wordt die rechtop staan.

## Wat erin gaat

| Voorwerp | Maat (vereenvoudigd) |
|---|---|
| Pinecil V2 met punt erop | 159 lang; handvat 103 lang, 17,4 breed × 14,4 hoog; daarna het dunne metalen puntje |
| 4 reservepunten | 90 lang, grootste diameter 11 |
| Inbussleutel | L-vorm: lange poot 46, haakse poot 16, dikte 1,46 |

De vormen zijn voorlopig eenvoudig (ellips, cilinders, balkjes). De exacte
vormen van bout en punten werken we later uit; dan veranderen alleen de
kanalen in het inzetstuk.

## Hoe het eruitziet

### Dwarsdoorsnede

De koker heeft als doorsnede een **afgerond trapezium**. De brede kant ligt
op tafel (de onderkant), de smalle kant is boven.

De indeling van binnen (layout **B**):

- **Onderste rij:** punt – bout – punt.
- **Bovenste rij:** twee punten, met daartussen een smal kanaal voor de lange
  poot van het inbussleuteltje.

Buitenmaat ongeveer **56 breed × 38 hoog**.

### Twee materialen, twee lagen

- **Inzetstuk** — PETG in een leuke kleur. Geen dunne koker maar een massief
  stuk met voor elk voorwerp een eigen **kanaal** in de lengterichting (0,4
  speling rondom, minstens 1,2 PETG tussen de kanalen). Niets rammelt.
- **Buitendeel** — zwart PLA, een schil om het inzetstuk heen. Zijwanden 1,6.
  Boven- en onderwand zijn dikker, omdat daar de goot voor het klittenband in
  zit (zie verder).

### Lengte en de twee helften

Totale lengte ongeveer **173 mm**. Van buiten naar binnen, aan elk uiteinde:
kopse kant (2) → kanaal voor het klittenband (band + speling) → eindwand van
het inzetstuk (1,6) → de ruimte voor de spullen (bout + 1 mm speling aan elke
kant).

Om open te kunnen wordt alles doorgesneden, maar **buitendeel en inzetstuk op
een andere plek**:

- Het **buitendeel** wordt precies in het midden doorgesneden: twee helften
  van ~86 mm.
- Het **inzetstuk** wordt verder richting helft A doorgesneden. Zo ontstaat
  een **overlap**: het inzetstuk van helft B steekt ~42 mm uit zijn
  buitenhelft en schuift in het buitendeel van helft A. Dat lijnt de helften
  uit bij het dichtdoen.

Elk inzetstuk wordt in zijn eigen buitenhelft vastgezet (gelijmd), met het
klittenband ertussen. Daarna is elke helft één geheel; alleen de overlap
schuift.

- **Helft A** — kort inzetstuk (~41 mm). Als je de koker opent steken bout,
  punten en sleutel er ver uit, zodat je ze makkelijk pakt.
- **Helft B — de "dop"** — lang inzetstuk (~124 mm). Op de kopse kant van
  deze helft zit het **logo**.

### Het inbussleuteltje

Het sleuteltje ligt helemaal achterin helft A. De haakse poot ligt dwars,
tegen de eindwand. Om daar ruimte voor te maken beginnen de twee bovenste
punten iets verder naar voren — precies de sleuteldikte plus speling en een
PETG-wandje (≈ 3,5 mm, wordt uitgerekend). De lange poot ligt in het smalle kanaal tussen
de bovenste punten en **steekt 8 mm uit het inzetstuk van helft A**, zodat je
hem kunt pakken. Hierdoor ligt ook vast waar het inzetstuk doorgesneden
wordt: precies 8 mm vóór het uiteinde van het sleuteltje.

### Het klittenband

Eén strook dubbelzijdig klittenband (haak aan de ene kant, lus aan de andere)
loopt als **gesloten lus in de lengte** om de koker:

- **Boven** ligt het in een goot, vlak met het oppervlak, en loopt het
  ononderbroken over de snede heen.
- Vlak voor elk uiteinde **buigt het naar binnen**, loopt tussen inzetstuk en
  buitendeel door, **achter de kopse kant langs** (achter de gaten van het
  logo, je ziet de band door het logo heen), en komt aan de onderkant weer
  naar buiten.
- **Onder** overlappen de twee uiteinden van de strook elkaar en plakken ze
  aan elkaar. Daar ligt dus **dubbel** klittenband en is de goot dieper.

Om te openen trek je de overlap aan de onderkant los. De band moet dan door
de koker kunnen schuiven, dus het kanaal is overal ruim en heeft **bochten in
plaats van hoeken** — dat werkt soepeler en spaart het klittenband.

**Hoe het kanaal gemaakt wordt:** in zijaanzicht nemen we twee afgeronde
blokken die bijna in elkaar passen. Het buitenste blok is precies zo groot
als de koker (zonder de kopse kanten); het binnenste is één banddikte kleiner
aan boven- en zijkanten en twee banddiktes aan de onderkant — daarom
*bijna* concentrisch. Het verschil tussen de twee blokken is een ring: de
weg die de band aflegt. Die ring, over de breedte van de band, halen we uit
het buitendeel én het inzetstuk weg. Zo ontstaan in één keer de goot boven,
de diepere goot onder, de bochten naar binnen en het kanaal achter de kopse
kanten.

Omdat de goot niet door de PLA-wand heen mag, is de bovenwand
1× banddikte + speling + 1,2 dik en de onderwand 2× banddikte + speling + 1,2.

Startwaarden voor het klittenband: 20 breed, 2 dik per laag, binnenbocht
straal 5.

### Het logo

Het Pinecil-logo (de PINE64-dennenappel) zit als **doorkijkgat** in de kopse
kant van de dop. Het staat **rechtop** als de koker op zijn brede kant ligt:
de top van de dennenappel wijst naar de smalle kant van het trapezium.

- Maximaal 19 mm groot (hoogte en breedte), rib-breedte 0,8 — zie de README
  voor hoe de ribben werken.
- Het logo moet binnen het **rechte stuk** van de band achter de kopse kant
  vallen, met wat marge, want de bocht van de band door het logo heen zien is
  lelijk. Het rechte stuk is nu ~21,7 hoog, dus 19 past; groter kan alleen
  met een kleinere bochtstraal.

## Printen

Elk deel wordt **rechtop** geprint (de as van de koker verticaal), het
langste deel is het inzetstuk van de dop met ~124 mm — ruim binnen 180 mm.
De dop print met de kopse kant op het bed, dus de logoribben zijn de eerste
laag: netjes, en er hoeft niets overbrugd te worden.

| Deel | Materiaal | Lengte ≈ |
|---|---|---|
| Buitendeel A | zwart PLA | 86 |
| Buitendeel B (dop, met logo) | zwart PLA | 86 |
| Inzetstuk A | PETG | 41 |
| Inzetstuk B | PETG | 124 |

## Montage

1. Leg het klittenband in de goten en het kanaal van beide buitenhelften.
2. Lijm elk inzetstuk in zijn buitenhelft; de band zit dan vast tussen de
   twee lagen maar kan nog schuiven.
3. Spullen in helft A, dop erover schuiven, klittenband onder dichtplakken.

## Nog open

- Exacte vorm van de kanalen voor bout en punten.
- Werkelijke maten van het klittenband (breedte, dikte).
- Of de bovenkant breder moet om de goot niet te smal te laten uitvallen.
- Lijmen of klemmen van het inzetstuk (nu: lijmen).
