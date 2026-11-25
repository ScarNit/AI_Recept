# Ljudske dorade AI prijedloga

Recept predviđa ljudsku kontrolnu točku nakon plana (`--do plan`). Ovdje su zapisane sve
ručne izmjene, kako bi se postupak mogao ponoviti.

## 1. Plan, objava 1 – uklonjena nepotkrijepljena zdravstvena tvrdnja

- **AI prijedlog:** „Edukativni karusel koji korak po korak objašnjava razliku između koncentrata, izolata i hidrolizata sirutke u Just Whey proteinu. Posljednji slajdovi naglašavaju ulogu probavnih enzima DigeZyme® i bromelaina za ugodnu probavu bez nadutosti.”
- **Problem:** riječ „nadutost” ne pojavljuje se na stranici proizvoda
  (https://gymbeam.hr/protein-just-whey-gymbeam.html) – to je zdravstvena tvrdnja bez izvora,
  što krši pravilo brifa i EU pravila o zdravstvenim tvrdnjama.
- **Dorada:** „Edukativni karusel koji korak po korak objašnjava razliku između koncentrata, izolata i hidrolizata sirutke u Just Whey proteinu. Posljednji slajdovi naglašavaju ulogu probavnih enzima DigeZyme® i bromelaina.”
- **Kako je otkriveno:** pretraga ključnih tvrdnji plana u `01_izvori.json`
  (sve ostale činjenice plana pronađene su doslovno u izvorima).

## Dorade sadržaja iz `dorade.yaml` (2026-11-25 19:22)

- **objava 1, opis:** „Nisi siguran što tvoj protein zapravo sadrži i kako utječe na tvoju probavu? Vrijeme je da zaviriš ispod etikete!

Just Whey je naš protein sirutke dobiven iz mlijeka krava koje pasu travu, a kombinira čak tri izvora bjelančevina: koncentrat, izolat i hidrolizat. U jednoj mjerici od 30 g čeka te najmanje 22 g bjelančevina i 6,5 g BCAA, bez nepotrebnih zgušnjivača.

Zabrinut si zbog težine u želucu nakon shakera? Formula je obogaćena kompleksom probavnih enzima DigeZyme® i bromelainom za lakšu razgradnju.

Spremi ovaj vodič da ti se nađe pri ruci sljedeći put kad biraš protein, i pošalji ga prijatelju iz teretane koji treba ove informacije!

Cijene se kreću od 26.95 EUR za pakiranje od 500 g (cijena na gymbeam.hr, 25.11.2026.).” → „Nisi siguran što tvoj protein zapravo sadrži? Vrijeme je da zaviriš ispod etikete! 🔍

Just Whey je naš protein sirutke iz mlijeka krava koje pasu travu, a kombinira čak tri izvora bjelančevina: koncentrat, izolat i hidrolizat. U jednoj mjerici od 30 g čeka te najmanje 22 g bjelančevina i 6,5 g BCAA – bez punila i zgušnjivača.

Sastav nadopunjuje šest probavnih enzima: pet u kompleksu DigeZyme® te bromelain.

Spremi ovaj vodič da ti se nađe pri ruci sljedeći put kad biraš protein i pošalji ga prijatelju iz teretane! 💪

Pakiranje od 500 g: 26,95 € (cijena na gymbeam.hr, 25.11.2026.).”
  - razlog: AI opis je ponovno uveo implicitnu zdravstvenu tvrdnju ("težina u želucu", "lakša razgradnja", "kako utječe na probavu") koje nema na stranici proizvoda; zamijenjeno doslovnim sastavom iz izvora. Cijena u hrvatskom formatu.
- **objava 1, hashtagovi:** „['#gymbeam', '#gymbeamhr', '#justwhey', '#proteini', '#fitnesshrvatska', '#vjezbanje', '#ishrana']” → „['#gymbeam', '#gymbeamhr', '#justwhey', '#proteini', '#fitnesshrvatska', '#vjezbanje', '#prehrana']”
  - razlog: #ishrana nije hrvatski standard (srpski/bosanski) – zamijenjeno s #prehrana.
- **objava 1, kadar 2, nadnaslov:** „Tri izvora bjelančevina” → „Jedna mjerica od 30 g”
  - razlog: Nadnaslov "Tri izvora bjelančevina" ne odgovara velikoj brojci 22 g na tom kadru.
- **objava 1, kadar 5, nadnaslov:** „Lakša probava” → „Probavni enzimi”
  - razlog: "Lakša probava" je zdravstvena tvrdnja bez izvora.
- **objava 1, kadar 5, tekst:** „Just Whey je obogaćen kompleksom probavnih enzima DigeZyme® i bromelainom kako bi sastav bio prilagođen tvojoj probavi.” → „Sastav nadopunjuje šest probavnih enzima – pet u patentiranom kompleksu DigeZyme® te bromelain.”
  - razlog: "Prilagođen tvojoj probavi" je implicirani učinak; tekst sada doslovno prati izvor.
- **objava 3, opis:** „Spreman za najslađe odbrojavanje do Božića? 🎄

GymBeam Adventski kalendar donosi 24 dana čistog veselja i iznenađenja! Iza svakog prozorčića skriva se jedan od naših najpopularnijih proizvoda – od ukusnih proteinskih snackova poput keksa i pločica, do šejkera, vitamina i napitaka koji će ti olakšati predbožićnu užurbanost.

Privlačne dimenzije (45 × 32 × 22 cm) i bogat sadržaj čine ga savršenim darom za tebe ili tebi dragu osobu koja voli aktivan životni stil.

⚠️ Napomena: Radi se o ograničenoj seriji sezonskog proizvoda i novih komada više neće biti!

Cijena: 81,95 € (na gymbeam.hr, 25.11.2026.)

Klikni na stiker u Storyju i osiguraj svoj kalendar prije nego što se sve rasproda!” → „Spreman za najslađe odbrojavanje do Božića? 🎄

GymBeam Adventski kalendar skriva 24 iznenađenja! Iza prozorčića te čekaju naši najpopularniji proizvodi – proteinske pločice, keksi i druge poslastice, ali i šejker, vitamini i napitci.

Savršen dar za tebe ili dragu osobu koja voli aktivan životni stil. 🎁

⚠️ Kalendara ima samo ograničen broj, stoga ne čekaj posljednji trenutak.

Cijena: 81,95 € (na gymbeam.hr, 25.11.2026.)

Klikni na poveznicu u Storyju i osiguraj svoj kalendar!”
  - razlog: Uklonjena nespretna rečenica "Privlačne dimenzije…" i formulacija "novih komada više neće biti" zamijenjena doslovnijom ("samo ograničen broj") iz izvora.
- **objava 3, hashtagovi:** „['#gymbeam', '#adventskikalendar', '#gymbeamhrvatska', '#fitnesspoklon', '#zdravisnack', '#bozic2026']” → „['#gymbeam', '#gymbeamhr', '#adventskikalendar', '#fitnesspoklon', '#poklon', '#bozic2026']”
  - razlog: #zdravisnack implicira zdravstvenu tvrdnju; dodan #gymbeamhr radi dosljednosti.

Nakon ovih dorada ponovno su pokrenute determinističke provjere (`recept/provjera.py`): sve tri
objave prolaze bez grešaka i upozorenja. Riječi „želuc”, „lakša probava” i slične dodane su na
popis rizičnih izraza, a pravilo o probavi i hrvatskom formatu cijena dodano je u
`prompts/04_izrada.md`, tako da sljedeće pokretanje te greške hvata automatski.
