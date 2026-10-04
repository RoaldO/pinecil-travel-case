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

Buitenmaat ongeveer **60 breed × 38 hoog**.

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

- Het **inzetstuk** wordt zo doorgesneden dat de punten **11 mm uit
  inzetstuk A steken** (`TIP_GRIP`) — dan kun je ze pakken. De bout steekt
  nog verder uit.
- Het **buitendeel** wordt **20 mm eerder** doorgesneden (`OVERLAP`). Zo
  steekt inzetstuk A 20 mm uit zijn buitendeel en schuift het bij het
  dichtdoen in buitendeel B. Dat lijnt de helften uit.

| | Buitendeel | Inzetstuk |
|---|---|---|
| Helft A | ≈ 66 | ≈ 83,5 |
| Helft B — de "dop", met het **logo** | ≈ 107 | ≈ 85 |

Elk inzetstuk wordt in zijn eigen buitenhelft gelijmd. Het zakt daarbij
vanzelf tot de juiste diepte: naast de band loopt het inzetstuk door tot
tegen de kopse kant — dat is de **eindstop**. Daarna is elke helft één
geheel; alleen de overlap schuift.

Tussen de twee inzetstukken blijft als de koker dicht is een **spleetje van
0,5 mm** (`INSERT_SPLIT_GAP`): inzetstuk A is daarvoor iets ingekort. Zo
kunnen lijm- en printtoleranties nooit verhinderen dat de twee buitendelen
netjes op elkaar aansluiten — de buitendelen raken elkaar altijd eerst.

### Het inbussleuteltje

Een gewoon L-vormig inbussleuteltje. De **lange poot** steekt in een gaatje in
inzetstuk A, tussen de twee bovenste punten (~33 van de 46 mm zit erin). De
**haakse poot** blijft buiten inzetstuk A, net voorbij de uiteinden van de
punten: als de koker open is ligt hij **helemaal vrij** en is hij je grip om
het sleuteltje eruit te trekken.

De haakse poot (16 mm) past niet horizontaal — vanaf het midden is daar maar
~14 mm ruimte — dus hij wijst **schuin omlaag naar één kant** (15°), net over de
schouder van de bout heen. Hoek en kant zijn parameters. (Met een iets bredere
bovenkant kan hij ook horizontaal.)

In de voorkant van inzetstuk B zit een **open kuiltje** dat bij het dichtdoen
de uitstekende uiteinden van de punten en de haakse poot opvangt.

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

Is het klittenband breder dan de platte bovenkant, dan wordt de bovenkant
**vanzelf zo veel breder** dat de band ook aan zijn randen een volle laag
diep in de goot ligt — hij steekt nergens uit.

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
langste deel is buitendeel B met ~107 mm — ruim binnen 180 mm.
De dop print met de kopse kant op het bed, dus de logoribben zijn de eerste
laag: netjes, en er hoeft niets overbrugd te worden.

| Deel | Materiaal | Lengte ≈ |
|---|---|---|
| Buitendeel A | zwart PLA | 66 |
| Buitendeel B (dop, met logo) | zwart PLA | 107 |
| Inzetstuk A | PETG | 83,5 |
| Inzetstuk B | PETG | 85 |

## Montage

1. Lijm elk inzetstuk in zijn eigen buitenhelft; duw tot de eindstop.
2. Laat de lijm uitharden.
3. **Daarna pas** het klittenband doorvoeren: boven bij de sleuf naar binnen,
   achter de kopse kant langs, onder weer naar buiten — aan beide uiteinden.
   Zo komt er geen lijm aan het klittenband. Het kanaal heeft overal ruime
   bochten, zodat de band erdoor te duwen is.
4. Spullen in helft A, dop erover schuiven, klittenband onder dichtplakken.

## Nog open

- Exacte vorm van de kanalen voor bout en punten.
- Werkelijke maten van het klittenband (breedte, dikte).
