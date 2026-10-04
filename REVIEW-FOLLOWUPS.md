# Review follow-ups

Openstaande kleine punten uit de eindreview van het kokermodel (2026-10-04).
**Weggooien zodra alle punten zijn afgehandeld.** Vink af wat klaar is; een
punt dat we bewust laten zoals het is, krijgt een korte reden.

## Tests

- [ ] **Slide clearance echt testen** (spec-criterium 5). `tests/test_shell.py`
  checkt alleen "geen overlap" tussen inzetstuk A en buitendeel B. Omdat
  `SLIDE_CLEARANCE` == `GLUE_CLEARANCE` doet de extra snede in `cad/shell.py`
  nu niets, en als `SLIDE_CLEARANCE` kleiner wordt dan `GLUE_CLEARANCE` verbergt
  de lijmsnede dat. → afstandstest tussen de doorsneden in de overlapzone, en
  de overlapsnede zo maken dat hij ook bij een kleinere waarde klopt.
- [ ] **Bandtest zonder tautologie.** De eerste assert in
  `test_ring_is_thick_enough_everywhere_to_thread_the_band`
  (`tests/test_band.py`) vergelijkt waarden met zichzelf. De dubbele dikte aan
  de onderkant (criterium 10, "× lagen") is alleen door constructie
  gegarandeerd → echt meten.
- [ ] **Kanaalspeling meten** (criterium 3). Dat de spullen `ITEM_CLEARANCE`
  ruimte houden in hun kanalen wordt alleen als "geen overlap" getest
  (`tests/test_insert.py`). Klopt door constructie (`buffer(ITEM_CLEARANCE)`),
  dus laag risico.

## Docs

- [ ] **Recht bandstuk in `docs/model.md`**: daar staat "~21,7 hoog", het
  model geeft 21,31 (9,3…30,61). Met het logo van 19 mm + 2 × 1 mm marge blijft
  0,31 mm over, niet 0,7.
- [ ] **Printoriëntatie van de inzetstukken** vastleggen in `docs/model.md`
  (Printen) en de README. Opties: kopse kant omlaag (brug van ~20,6 mm over de
  bandsleuf) of snedekant omlaag (bruggen over de kanaaluiteinden, bout
  ~18 mm). Beide kan; kies en noteer.
- [ ] **README**: de regel "Requires `uv`." is weggevallen, en de testtijd
  staat op ~20 s terwijl het ~11 s is.

## Code

- [ ] **`logo_cutter` verhuizen** van `cad/build.py` (exportscript) naar een
  geometriemodule. Nu importeert `cad/shell.py` uit `cad/build.py` en moet
  `build.case_parts()` `cad.shell` lui importeren om een kringverwijzing te
  vermijden.
- [ ] **`_drop` in `cad/contents.py` luid laten falen**: als zelfs de
  bovengrens niet vrij is, geeft hij die stilletjes terug. Praktisch
  onbereikbaar, maar een `assert` maakt het zichtbaar.
