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
| Pinecil V2 met punt erop | 161,5 lang met de langste punt (gemeten 159 met een punt van 89,3); handvat 103,3 lang, "grafsteen" ≤ 14,6 breed × 17,5 hoog — zie *De bout* |
| 4 reservepunten | ≤ 92 lang (langste gemeten 89,3); voet getrapt, kraag ≤ ø 11, daarna ≤ ø 5,5 — zie *De punten* |
| Inbussleutel | L-vorm: lange poot 46, haakse poot 16, dikte 1,46 |

Het sleuteltje is voorlopig eenvoudig (cilinder en balkje). Punten en bout
zijn gemodelleerd (zie *De punten* en *De bout*); knopjes en details van de
bout volgen nog. Dan veranderen alleen de kanalen in het
inzetstuk.

### De punten

Elke punt is anders, dus als je de koker opent wil je zien welke welke is.
Daarom zit de **voet** (het eind met de witte ringetjes) diep in inzetstuk A
en steekt het werkende eind eruit.

De voet, gemeten vanaf dat uiteinde:

| Stuk | Lengte | Diameter |
|---|---|---|
| eerste deel | 24,1 | 5,4 |
| tweede deel | 9,7 | 5,7 |

Dan de **kraag**, gemeten vanaf zijn basis: het vlak dat bij de punt in de
bout tegen het handvat ligt.

| Van – tot (vanaf de basis van de kraag) | Diameter |
|---|---|
| 0 – 1,75 | 10,55 (zitvlak) |
| 1,75 – 2,3 | 11,0 (ring, het breedste deel) |
| 2,3 – 4,2 | taps van 11,0 naar 5,2 |
| 4,2 – 12,7 | 5,2 (hals) |

Het tapse stuk staat in het model als trapjes van 0,2 (`TAPER_STEP`), elk
op de grootste diameter: dat is ongeveer een printlaag, dus geprint is het
gewoon de kegel.

Het kanaal volgt die trappen: de voet met 0,3 speling rondom
(`TIP_BASE_CLEARANCE`, na testprint 1 strakker gemaakt), de kraag met 0,4
(ø 6,0 → 6,3 → 11,35 → 11,8).
Omdat een punt erin en eruit moet, wordt het kanaal **dieper in alleen maar
nauwer**, nooit weer breder. De punt rust met het zitvlak van zijn kraag
op de schouder van 6,5 naar 11,35. Die schouder ligt 0,4 dieper dan het
zitvlak in het model (ook in de lengte 0,4 speling), dus de punt zakt 0,4
door en er blijft 0,6 vrij onder de voet. Het brede
deel van het kanaal is minstens 6 mm diep (`TIP_COLLAR_MIN_DEPTH`); nu is het
ruim 44 mm, tot aan de snede van inzetstuk A.

Na de kraag is het breedste stuk de huls om het verwarmingselement:
**ø 5,5**. Alles daarna tot aan het werkende eind past daarbinnen, hoe de
vorm verder ook varieert. Daarom is de punt na de kraag in het model één
cilinder van ø 5,5, en houdt **inzetstuk B** hem vast
in één rechte boring van ø 6,3 (5,5 + speling) over de hele lengte. Gerekend
wordt met de langste punt plus marge: **92 mm**; kortere punten hebben
gewoon wat meer ruimte aan het eind van de boring.

In inzetstuk A blijft het kanaal na de kraag ø 11,8 tot aan de snede — het
mag naar de opening toe niet nauwer worden.

Inzetstuk A print je met de kopse kant op het
bed, dan liggen de schouders open naar boven en hoeft er niets te overhangen.

## Hoe het eruitziet

### De bout

De doorsnede van het handvat is een **grafsteen**: een halve cilinder
waarvan het hart precies de as van de punt is, met daarop een blok even
breed als die cilinder; de hoeken van het blok aan de kant van de cilinder
af zijn afgerond. De bout ligt met de **ronde kant naar beneden**: de platte
kant met het display en de twee knopjes wijst naar boven, zodat daar niets
op drukt.

De **basis** van het handvat zit diep in helft A, net als de voet van de
punten; de punt van de bout wijst naar helft B.

Het handvat is **103,3** lang en bestaat uit een **lijf van hard plastic**
over de hele lengte, met een **rubber handvat** eromheen:

| Deel | Waar (vanaf de basis) | Diameter ronding | Hoogte grafsteen | Afronding |
|---|---|---|---|---|
| plastic lijf (display, knopjes) | 0 – 103,3 | 13,78 (nagemeten bij de testprint; eerst 13,9) | 16,85 | R 2 |
| rubber handvat | 63,8 – 93,8 | 14,6 | 17,5 | R 4 |
| boutje op de platte kant | hart op 14,7 | kop ø 3,4 | steekt 1,1 uit | — |
| 2 knopjes op de platte kant | harten op 23,15 en 60,6 | ø 4,9 | steken 0,7 uit | — |
| display op de platte kant | 19 – 55 | 9,55 breed | vlak (steekt niet uit) | — |
| montageboutje (houdt de punt vast) op de platte kant | hart op 98,5 | kop ø 6 | steekt 2,8 uit | — |
| voetje onder de ronde kant | 98,4 – 102 | half vierkant 13,78 breed, 6,89 diep | — | R 1 |
| punt: kraag (zie *De punten*) | 103,3 – 116 | ≤ 11 | — | — |
| punt: huls tot het eind | 116 – 161,5 | ≤ 5,5 | — | — |

De punt in de bout is dezelfde als de reservepunten (zie *De punten*) en
wijst dezelfde kant op: de voet zit in het handvat, de basis van de kraag
(het zitvlak) direct tegen de neus. In B is het kanaal rond dat zitvlak
11,8: de ring van 11 ligt dieper in B en komt er bij het insteken langs. De lengte van de bout volgt daaruit, met de langste punt (92).

Alle delen hebben dezelfde as. Het plastic loopt **onder het rubber door**:
daar is de bout lijf en rubber samen. Het rubber is breder, onder dieper en
boven hoger, maar de scherpere bovenhoeken van het plastic (R 2 tegen R 4)
steken er 0,37 buiten — op die plekken is het plastic echt het ruimst.

**Het kanaal volgt de bout** (+ 0,4 speling), met één regel voor bout en
punten: een voorwerp schuift vanaf de snede in elk inzetstuk, dus op elke
diepte moet het kanaal ook passen voor alles wat er **dieper** ligt en er
onderweg doorheen komt. En ook in de lengte is er 0,4 speling: elke trap in
een kanaal ligt 0,4 dieper dan de schouder van het voorwerp erboven. Zonder
dat zat de bout precies klem tussen A (het boutje tegen het eind van zijn
gleuf) en B (de neus tegen de schouder naar de kraag), en zou de kleinste
printafwijking het sluiten tegenhouden. Het stuk met het rubber is overal het dikst. Maar
het **boutje** zit vlak bij de basis, die als eerste helft A in gaat: het
komt langs het hele kanaal in A, dus daar loopt een **gleufje** (3,4 + speling
breed) van het boutje tot aan de snede. In helft B komt het boutje nooit, dus
daar geen gleuf.

Hetzelfde geldt voor de **knopjes**: ook die liggen in helft A, dus ook voor
hen loopt een gleuf tot de snede. Rond de knopjes en het display
houdt het kanaal **1 mm extra** ruimte (`IRON_CONTROL_CLEARANCE`, bovenop de
0,4 speling): rammelt de bout een beetje, dan tikken knopjes en display nooit
tegen de wand. Die extra ruimte zit alleen in het kanaal, niet in de bout.
Het display steekt niet uit; het voegt dus alleen die extra ruimte toe (een
ondiepe, brede gleuf van 9,55 + 2 × 1 breed, ook tot de snede).

Het **montageboutje** zit op de neus, in helft **B**. Helft B schuift vanaf de
punt-kant over de bout, dus daar loopt zijn gleuf (6 + speling breed) van het
boutje tot aan de snede van B — en niet in A. Aan de voorkant van B loopt die
gleuf in elkaar over met het kuiltje van de haakse poot.

Het **voetje** zit daar tegenover, onder de ronde kant: zo blijft de bout
mooi liggen als hij op tafel ligt. Daar is de onderste helft een half
vierkant in plaats van een halve cirkel. Ook dat ligt in B, dus ook de
hoeken van het voetje lopen als gleufjes onder in het kanaal van B door tot
de snede.

### Dwarsdoorsnede

De koker heeft als doorsnede een **afgerond trapezium**. De brede kant ligt
op tafel (de onderkant), de smalle kant is boven.

De indeling van binnen (layout **B**):

- **Onderste rij:** punt – bout – punt. De bout staat met zijn ronde
  onderkant op dezelfde vloer als de punten, en is hoger dan zij.
- **Bovenste rij:** twee punten, met daartussen een smal kanaal voor de lange
  poot van het inbussleuteltje.

Buitenmaat ongeveer **57 breed × 43,5 hoog** (door de rechtopstaande bout
smaller en hoger dan eerst).

### Twee materialen, twee lagen

- **Inzetstuk** — PETG in een leuke kleur. Geen dunne koker maar een massief
  stuk met voor elk voorwerp een eigen **kanaal** in de lengterichting (0,4
  speling rondom, minstens 1,2 PETG tussen de kanalen). Niets rammelt.
- **Buitendeel** — zwart PLA, een schil om het inzetstuk heen. Zijwanden 1,6.
  Boven- en onderwand zijn dikker, omdat daar de goot voor het klittenband in
  zit (zie verder).

### Lengte en de twee helften

Totale lengte ongeveer **175 mm**. Van buiten naar binnen, aan elk uiteinde:
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
| Helft A | ≈ 68 | ≈ 85,5 |
| Helft B — de "dop", met het **logo** | ≈ 107,5 | ≈ 85,5 |

Elk inzetstuk wordt in zijn eigen buitenhelft gelijmd. Het zakt daarbij
vanzelf tot de juiste diepte: naast de band loopt het **buitendeel** (PLA)
door van de kopse kant tot het inzetstuk — dat zijn de **eindstops**, de
"bruggenhoofden" naast het bandkanaal. Het inzetstuk eindigt zelf overal op
één vlak, net voorbij het bandkanaal. Daarna is elke helft één
geheel; alleen de overlap schuift.

Tussen de twee inzetstukken blijft als de koker dicht is een **spleetje van
0,5 mm** (`INSERT_SPLIT_GAP`): inzetstuk A is daarvoor iets ingekort. Zo
kunnen lijm- en printtoleranties nooit verhinderen dat de twee buitendelen
netjes op elkaar aansluiten — de buitendelen raken elkaar altijd eerst.

**Afschuiningen om in elkaar te schuiven** (allemaal 45°, als plakjes van
0,2 gemodelleerd):

- Beide inzetstukken hebben op het vlak waarop ze geprint worden — hun
  buitenste uiteinde, dat bij het lijmen als eerste in het eigen buitendeel
  gaat — een afschuining van **0,6** rondom (`INSERT_BED_CHAMFER`). Die vangt
  meteen de "olifantenvoet" van de eerste laag op.
- Inzetstuk A heeft op zijn snedevlak alleen een **dun richeltje van 0,3**
  (`INSERT_A_LEAD_IN`): de magneetjes zitten daar 1,2 van de rand, en zo
  blijft er 0,9 over.
- De rest van de inloop zit in **buitendeel B**: de binnenrand van zijn mond
  heeft een afschuining van **0,6** (`SHELL_B_MOUTH_CHAMFER`). Die print
  zonder overhang (buitendeel B print met de kopse kant op het bed, de mond
  boven). Onder de klittenbandgoot blijft aan de rand 0,6 PLA over.

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
de haakse poot opvangt. De uitstekende uiteinden van de punten gaan elk in hun
eigen boring van ø 6,3. Het kuiltje loopt daarbij over de boring van de
rechterbovenpunt heen; die twee vormen aan de voorkant één opening.

Het sleuteltje draait vrij om zijn lange poot, dus vóór het sluiten moet de
haakse poot in de goede stand staan. Daarvoor zit in de **voorkant van
inzetstuk A** een ondiep **uitlijngroefje** (0,8 breed, 0,6 diep), vanaf het
gat van het sleuteltje precies in de richting van de haakse poot en even
lang: kijk je van voren op A, dan ligt de poot goed als hij boven het groefje
ligt. Het groefje loopt deels door de boring van de punt rechtsboven; het is
zichtbaar vlak bij het gat en aan het eind, en dat is genoeg referentie.

Staat de poot toch wat scheef, dan vangt een **trechter** aan de mond van het
kuiltje hem op. Omdat het sleuteltje om zijn lange poot draait, is de
trechter geen gewone verwijding maar **draait hij mee om die as**: aan de
voorkant van B neemt het kuiltje de poot op tot **20° verdraaid** naar elke
kant, en over **6 mm** diepte loopt dat terug naar 0°, daarna is het het
gewone kuiltje. Bij het dichtschuiven draait de trechter de poot zo vanzelf
recht. De poot komt pas ~11 mm voor het dichtgaan in het kuiltje, dus die
6 mm is er ruim.

De trechter mag aan de voorkant tot vlak bij de buitenkant van inzetstuk B
komen, maar er blijft altijd een wandje van **twee printlijnen** (0,9,
`KEY_FUNNEL_WALL`) staan: verder dan dat kan de poot toch nauwelijks staan
(de rand van buitendeel B schuift er eerst langs), en sterkte is daar geen
punt — dat wandje wordt tegen het PLA van buitendeel B gelijmd. (Eerst was
het één printlijn, maar daar trok de naad steeds een gat in, wat je ook met
de naadinstellingen deed — testprint 2026-10-10.)

Waar kuiltje en trechter dicht langs andere kanalen lopen (de bout, de gleuf
van het montageboutje, de punt rechtsboven), zouden dunne, scherpe spitsjes
PETG blijven staan die lelijk printen. Die worden **weggeschaafd**: naast het
kuiltje blijft niets staan dat smaller is dan twee printlijnen (0,9). Het
buitenwandje telt daarbij niet mee. Hij loopt ook over de boring van de punt
rechtsboven heen; die punt wordt dieper in B nog gewoon vastgehouden.

In het model bestaat de trechter uit plakjes van 0,2 (een printlaag), elk op
de grootste hoek. Inzetstuk B print met zijn achterkant op het bed, dan loopt
de trechter naar boven open en hangt er niets over.

### Magneetjes

Naast het klittenband wat kleine magneetjes, zodat de koker **dichtklikt**.
Niet als valbescherming — daarvoor blijft het klittenband — alleen zodat hij
uit zichzelf dicht blijft.

**Veilig voor bout en punten?** Ja. Een vaste magneet doet niets met de
elektronica (geen magnetische opslag; de bewegingssensor is een
accelerometer). Heeft een Pinecil een hall-sensor voor de slaapstand, dan kan
een magneet hem in slaap zetten — in een koker, uit, maakt dat niet uit.
Neodymium-magneten verliezen boven ~80 °C blijvend kracht en PLA wordt
rond 60 °C zacht: de bout gaat er alleen afgekoeld in.

**Waar ze kunnen.** De wand van het buitendeel (1,6) is te dun; de logische
plek zijn de twee **snedevlakken van de inzetstukken** (voorkant A en voorkant
B, bij dichte koker 0,5 mm uit elkaar). Een magneetje moet op dezelfde plek
in beide vlakken passen, er een paar mm in kunnen zakken zonder een kanaal te
raken, met 1,2 PETG rondom. Eerste verkenning voor ø 3 × 2 (2 mm diep in
elk vlak, gaatje 0,2 ruimer), nog vóór de trechter:

| Plek | Ruimte | Afstand tot de haakse poot bij het langsschuiven |
|---|---|---|
| links, tussen punt linksboven, punt linksonder en de bout | ruim (ø 4 past ook) | ~12 mm |
| rechts, op dezelfde hoogte | krap, door het kuiltje van de haakse poot | **~3,3 mm** |
| boven in het midden, tussen de bovenste punten | krap | **~3,5 mm** |

Drie in een driehoek trekken de helften recht naar elkaar toe; twee (links
en rechts) is genoeg om te klikken. ø 2 × 3 past overal makkelijk, ø 4 alleen
links. De punten liggen overal ≥ ~4 mm van een magneetje.

**Het probleem: het sleuteltje.** Het sleuteltje is van staal en draait vrij
om zijn lange poot. Bij dichte of open koker is er niets aan de hand: de
magneetjes in A liggen ~12 mm voor de haakse poot. Maar tijdens het
**dichtschuiven** schuift de voorkant van B — met zijn magneetjes — langs de
plek van de haakse poot, rechts en boven op maar ~3,3–3,5 mm. Dat is te
dichtbij: net voordat de poot het kuiltje in gaat kan hij een paar graden naar
het magneetje draaien en achter de rand van het kuiltje haken, en dan heeft
het sleuteltje bij het sluiten "een eigen wil".

Overwogen:

1. **Magneten alleen in A, stalen tegenstukjes in B.** Staal trekt staal niet
   aan, dus B trekt niet aan het sleuteltje; de magneten in A blijven ~12 mm
   van de poot. Iets minder trekkracht dan magneet op magneet, genoeg om te
   klikken.
2. **Alleen plekken ver van de poot.** Nu is dat alleen links — één magneet
   trekt de koker scheef dicht.
3. **Een trechter aan de mond van het kuiltje in B**, zodat een iets
   gedraaide poot vanzelf het kuiltje in geleid wordt. **Gekozen en gemaakt** (zie *Het inbussleuteltje*), omdat dit
   een probleem oplost dat er óók zonder magneten al is: het sleuteltje draait
   vrij om zijn lange poot, dus ook nu moet je de haakse poot bij het sluiten
   eerst netjes uitlijnen met het kuiltje — mild irritant. De trechter doet
   dat voor je, wat de oorzaak van het draaien ook is (magneet, schudden in de
   tas, of gewoon hoe je hem erin legde). Te combineren met 1 of 2.

**Hoe het nu is.** Na de trechter verdween de plek rechts, en alleen links
(twee magneetjes) trok de koker uit het midden dicht — niet overtuigend.
Daarom is de koker onderaan **iets breder** gemaakt, zodat er drie
magneetjes in een driehoek passen:

- **twee in de onderhoeken**, op de vloer, net buiten de onderste punten;
- **één midden in de top**, tussen de bovenste punten, recht boven het
  sleuteltje.

De plekken worden uit de indeling berekend (ze schuiven mee als die
verandert), en het inzetstuk wordt vanzelf zo breed als nodig: de
magneetgaatjes tellen mee bij het passen van het trapezium. Dat maakt de
koker **4,5 mm breder** (57,2 i.p.v. 52,7). Het kost zoveel omdat de
punten in de voorkant van A in een boring van ø 11,8 zitten (voor de kraag)
en het magneetje daar met 1,2 PETG ernaast moet.

De top-magneet zit dicht bij de **wortel** van de haakse poot (~3,5 mm),
maar een trekkracht vlak bij de as van het sleuteltje heeft geen hefboom om
het te laten draaien. Wat het sleuteltje draait is trekkracht op het
**uiteinde** van de poot, en de buitenste helft van de poot ligt ~10 mm van
het magneetje. Wat er toch draait vangt de trechter op.

- Magneetje ø 3 × 2 (`MAGNET_DIAMETER`, `MAGNET_THICKNESS`), gaatje 0,1
  ruimer en 0,1 dieper (`MAGNET_CLEARANCE`): hij steekt nooit uit en er is
  ruimte voor een drupje lijm.
- Per plek een gaatje in de voorkant van A en recht tegenover in die van B;
  bij dichte koker zitten ze ~0,7 mm uit elkaar.
- Beide inzetstukken printen met de voorkant boven, dus de gaatjes liggen
  open naar boven.
- **Let op de polariteit** bij het inlijmen: in A en B tegengestelde polen
  naar elkaar toe. Handig: leg een losse magneet tegen degene die je inlijmt,
  en lijm die in de andere helft met dezelfde kant naar buiten.
- Een test bewaakt 1,2 PETG rondom elk gaatje (ook tot trechter en
  uitlijngroefje) en ≥ 8 mm tot de buitenste helft van de haakse poot
  (`MAGNET_KEY_DISTANCE`).

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

- Maximaal 19 mm groot (hoogte en breedte), rib-breedte 0,8 (getest in PLA
  met het logoplaatje: print netjes, ribben stevig — blijft zo) — zie de README
  voor hoe de ribben werken.
- Het logo moet binnen het **rechte stuk** van de band achter de kopse kant
  vallen, met wat marge, want de bocht van de band door het logo heen zien is
  lelijk. Het rechte stuk is nu ~26,8 hoog (door de hogere koker), dus 19
  past ruim (~5,8 marge over); groter kan, tot ~24,8; nog groter alleen
  met een kleinere bochtstraal.

## Printen

Elk deel wordt **rechtop** geprint (de as van de koker verticaal), het
langste deel is buitendeel B met ~107,5 mm — ruim binnen 180 mm.
De dop print met de kopse kant op het bed, dus de logoribben zijn de eerste
laag: netjes, en er hoeft niets overbrugd te worden.

**Naad (seam):** in de slicer met de hand plaatsen (op een plek die er
niet toe doet) of op willekeurig — een uitgelijnde naad maakt sneetjes in
het werkstuk (testprint ronde 2). Geldt voor alle onderdelen.

De **inzetstukken printen allebei op hun buitenste uiteinde** (de kant die
bij het lijmen als eerste in het eigen buitendeel gaat, met de afschuining
voor het bed). Dan lopen alle kanalen naar boven toe wijder (geen overhang
aan de trappen van de punten), en de trechter en de magneetgaatjes liggen
open naar boven. Dat vlak is **helemaal vlak, zonder brug**: eerst liep het
inzetstuk naast de band door tot de kopse kant, waardoor het over de
bandsleuf een brug van ~20 mm moest printen (testplakje 4b: lelijk). Nu zijn
die stukken naast de band van het PLA-buitendeel (de eindstops), en zakt het
hele PETG-deel vlak op het bed. Aan de pasvorm verandert niets. Alleen waar
de band om de hoeken van het inzetstuk buigt (straal 5), loopt de rand de
eerste ~4 lagen steil schuin naar buiten: een korte overhang, geen brug.

| Deel | Materiaal | Lengte ≈ |
|---|---|---|
| Buitendeel A | zwart PLA | 68 |
| Buitendeel B (dop, met logo) | zwart PLA | 107,5 |
| Inzetstuk A | PETG | 85,5 |
| Inzetstuk B | PETG | 85,5 |

### Testprints

Voordat de hele koker geprint wordt, eerst **testplakjes** (`make coupons`,
in `build/coupons/`): dunne plakjes (8–10 mm) uit de échte onderdelen, op de
plekken waar de pasvorm ertoe doet, al in printstand gedraaid. Probeer er de
echte punten, bout, sleuteltje en magneetjes in, en stel daarna de
spelingen in `cad/params.py` bij. Het volledige stappenplan (printen, wat te
testen, de brug in het grondvlak, welke parameter bij welke klacht):
[`testprint.md`](testprint.md).

| Plakje | Uit | Test |
|---|---|---|
| 1 | inzetstuk A bij de kraag | boringen ø 5,7 → zitvlak → ring van de punten; grafsteen van de bout met de gleuven van display, knopje en boutje |
| 2a + 2b | voorkant inzetstuk A + mond buitendeel B | 2a schuift in 2b: schuifspeling en inloop; magneetjes, gaatje + uitlijngroefje van het sleuteltje |
| 3 | voorkant inzetstuk B | klikt op 2a (magneetjes); trechter met het echte sleuteltje; boringen van de punt-einden; gleuven van montageboutje en voetje |
| 4a + 4b | uiteinde buitendeel A + grondvlak inzetstuk A | 4b in 4a: lijmspeling, afschuining, eindstops van PLA, kanaal klittenband; 4b print vlak (geen brug) |

## Montage

1. Lijm de magneetjes in de voorkant van beide inzetstukken (let op de
   polariteit, zie *Magneetjes*).
2. Trek het **uitlijngroefje** in de voorkant van inzetstuk A na met een
   **viltstift**: zonder kleur is het nauwelijks te zien.
3. Lijm elk inzetstuk in zijn eigen buitenhelft; duw tot de eindstops.
4. Laat de lijm uitharden.
5. **Daarna pas** het klittenband doorvoeren: boven bij de sleuf naar binnen,
   achter de kopse kant langs, onder weer naar buiten — aan beide uiteinden.
   Zo komt er geen lijm aan het klittenband. Het kanaal heeft overal ruime
   bochten, zodat de band erdoor te duwen is.
6. Spullen in helft A, dop erover schuiven, klittenband onder dichtplakken.

## Nog open

- Werkelijke maten van het klittenband (breedte, dikte).
