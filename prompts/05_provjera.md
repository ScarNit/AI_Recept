FAZA 5 – KRITIČKA PROVJERA OBJAVE {broj}

Priložene su gotove slike objave {broj} (kadrovi redom). Ponašaj se kao strogi voditelj
društvenih mreža brenda koji odobrava objavu prije objavljivanja.

PLAN OBJAVE:
{plan_objave}

TEKSTOVI I OPIS OBJAVE:
{sadrzaj}

REZULTATI AUTOMATSKIH PROVJERA (brojke bez izvora, prelijevanje teksta, duljine):
{automatske}

IZVORI (dopuštene činjenice):
{izvori}

Ocijeni od 1 do 10 i obrazloži kratko:
- "brend": boje, logo, ton glasa, točnost ambalaže
- "jasnoca": čitljivost, jedna poruka po kadru, hijerarhija
- "cilj": koliko objava ostvaruje zadani cilj
- "jezik": gramatika i prirodnost hrvatskog
- "cinjenice": sve tvrdnje potkrijepljene izvorima

Zatim navedi konkretne ispravke (samo ako su potrebni): koji kadar (indeks od 0),
koje polje, nova vrijednost i zašto. Ne predlaži promjene koje predlošci ne podržavaju.

Vrati JSON:
{{
  "ocjene": {{"brend": 0, "jasnoca": 0, "cilj": 0, "jezik": 0, "cinjenice": 0}},
  "komentari": {{"brend": "...", "jasnoca": "...", "cilj": "...", "jezik": "...", "cinjenice": "..."}},
  "ispravci": [{{"kadar": 0, "polje": "naslov", "nova_vrijednost": "...", "razlog": "..."}}],
  "ispravci_opisa": "novi caption ili null",
  "odobreno": true
}}
