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

## Brif: ti-forma → vi-forma (nakon analize snimki Instagrama, 25. 11. 2026.)

- **Ulaz:** dvije snimke zaslona profila @gymbeamhr (`brief/instagram/01_profil_vrh.png`,
  `02_mreza_objava.png`), dodane u brif kao `instagram_reference`.
- **Opažanje:** brend se obraća u množini – „Pratite nas za fitness inspiraciju” (bio),
  „Uživajte u besplatnoj dostavi s BOX NOW” (objava), web „ne čekajte posljednji trenutak”.
  Izvorni demonstracijski brif tražio je ti-formu, pa su prve verzije objava bile u ti-formi.
- **Odluka:** brif ispravljen na vi-formu; sustavski prompt više ne propisuje ti-formu nego
  oblik obraćanja preuzima iz analize; prompt analize sad izričito traži oblik obraćanja i
  „nesuglasja s brifom”. Dorade prve verzije sačuvane su u `dorade_v1_ti_forma.yaml`.
- **Ostala opažanja sa snimki:** feed čine gotovo isključivo reelsi sa stvarnim osobama
  (influenceri, kreatori, kuhinja/teretana), odjeća, unboxing i povremeni AI-stilizirani
  vizuali; istaknute priče: Zajednica, Novosti, Članci, Recepti, Outfiti. Statični karusel i
  story naše demonstracije zato su namjerno dopuna (edukacija za spremanje – tema „Članci”),
  a reels s osobama ostaje prijedlog za sljedeću verziju recepta.

## Dorade sadržaja iz `dorade.yaml` (2026-11-26 08:42)

- **objava 2, kadar 1, nadnaslov:** „KASNI TRENING DELIKATESA” → „Nakon kasnog treninga”
  - razlog: "Kasni trening delikatesa" je nespretan i negramatičan izraz.
- **objava 2, kadar 1, tekst:** „Koji je vaš izbor za kasni večernji snack koji neće narušiti vaše fit ciljeve?” → „Koji je vaš izbor za večernji snack? Napišite u komentar!”
  - razlog: "Koji neće narušiti vaše fit ciljeve" implicira učinak koji izvor ne navodi; dodan jasan poziv na komentar (cilj objave).
- **objava 2, opis:** „Završili ste kasni trening i otvarate kuhinjske ormariće. Što prvo birate – hrskavo slano ili kremasto slatko?

Vječna dilema nakon večernjeg treninga ne mora značiti kompromis s vašim fit ciljevima. Za vas smo pripremili dvije odlične opcije:

Ako ste u Timu Slano, tu je Proteinski čips. Priprema se ekspandiranjem vrućim zrakom i sadrži manje od 10 % masti, pa možete uživati u hrskanju bez brige.

Ako ipak glasate za Tim Slatko, vaš favorit je MoiMüv Proteinski namaz. Izvor je proteina i ne sadrži dodani šećer, a odlično se uklapa na palačinke, tost ili direktno na žlicu.

Nema krivog odgovora! Napišite nam u komentarima – jeste li Tim Slano ili Tim Slatko?” → „Završili ste kasni trening i otvarate kuhinjske ormariće. Što prvo birate – hrskavo slano ili kremasto slatko? 🤔

Ako ste u Timu Slano, tu je Proteinski čips. Priprema se ekspandiranjem vrućim zrakom i sadrži manje od 10 % masti, a u 100 g ima 21 g biljnih proteina.

Ako glasate za Tim Slatko, vaš je favorit MoiMüv Proteinski namaz. Izvor je proteina, ne sadrži dodani šećer i odlično ide na palačinke, tost ili ravno sa žlice.

Nema krivog odgovora! Napišite nam u komentar – Tim Slano ili Tim Slatko? 👇”
  - razlog: Uklonjeni izrazi koji impliciraju učinak ("ne mora značiti kompromis s vašim fit ciljevima", "uživati bez brige"); dodana doslovna činjenica iz izvora (21 g biljnih proteina na 100 g).
- **objava 2, hashtagovi:** „['#gymbeam', '#gymbeamhr', '#fitprehrana', '#proteinskicips', '#moimuv', '#fitnesshrvatska', '#zdravisnack', '#slanoilislatko']” → „['#gymbeam', '#gymbeamhr', '#fitprehrana', '#proteinskičips', '#moimuv', '#fitnesshrvatska', '#proteinskisnack', '#slanoilislatko']”
  - razlog: #zdravisnack implicira zdravstvenu tvrdnju (uklonjen i u verziji 1); #proteinskicips → #proteinskičips.
- **objava 3, kadar 1, story_naljepnica.opcije:** „['Pretspreman/na!', 'Jedva čekam!']” → „['Spreman/na sam!', 'Jedva čekam!']”
  - razlog: "Pretspreman/na" nije hrvatska riječ.
- **objava 3, kadar 3, stavke:** „[{'naslov': 'Proteini i snackovi', 'tekst': 'Proteinske pločice, keksi i napitci za svaki dan u prosincu.'}, {'naslov': 'Vitamini i dodaci', 'tekst': 'Podrška za zimske dane i predbožićnu užurbanost.'}, {'naslov': 'Ograničena serija', 'tekst': 'Količine su ograničene i novih više neće biti.'}]” → „[{'naslov': 'Proteini i snackovi', 'tekst': 'Proteinske pločice', 'keksi i napitci za svaki dan u prosincu.': None}, {'naslov': 'Vitamini i dodaci', 'tekst': 'Vitamini i dodaci prehrani koji su najkorisniji zimi.'}, {'naslov': 'Ograničena serija', 'tekst': 'Količine su ograničene i novih više neće biti.'}]”
  - razlog: "Podrška za zimske dane" parafrazira izvor u smjeru zdravstvene tvrdnje; vraćeno na doslovno "najkorisniji zimi".
- **objava 3, kadar 4, naslov:** „Osigurajte *vaš* kalendar” → „Osigurajte *svoj* kalendar”
  - razlog: Povratno-posvojna zamjenica "svoj" umjesto "vaš" (napomena AI kritičara, nije bila automatski primijenjena).
- **objava 3, kadar 4, story_naljepnica.tekst:** „Kupi kalendar” → „Kupite kalendar”
  - razlog: Ti-forma na naljepnici; provjera sada čita i tekst naljepnica.
- **objava 3, opis:** „Jingle Bells, Jingle Bells... Božić se brzo bliži, a Vi imate 24 razloga za veselje! 🎄✨

Predstavljamo Vam GymBeam Adventski kalendar koji iza svakog od 24 prozorčića skriva iznenađenje za svaki prosinac do Badnjaka. Unutra Vas čekaju naši najpopularniji proizvodi – od proteinskih pločica i hrskavih keksa do vitamina i dodataka prehrani koji će Vam dobro doći u predbožićnoj užurbanosti.

Ovo je ograničena serija i novih količina više neće biti. Ne dopustite da Vam prosinac počne bez Vašeg jutarnjeg fitness rituala!

Kliknite na poveznicu u Storyju i osigurajte svoj kalendar na vrijeme. 🎁” → „Jingle Bells, Jingle Bells… Božić se brzo bliži, a vi imate 24 razloga za veselje! 🎄✨

GymBeam Adventski kalendar iza svakog od 24 prozorčića skriva iznenađenje – za svaki dan do Badnjaka. Unutra vas čekaju naši najpopularniji proizvodi: proteinske pločice, keksi i druge poslastice, vitamini i dodaci prehrani te napitci koji će vam dobro doći u predbožićnoj užurbanosti.

Kalendara imamo samo ograničen broj i novih više neće biti, stoga ne čekajte posljednji trenutak.

Cijena: 81,95 € (na gymbeam.hr, 25. 11. 2026.)

Kliknite na poveznicu u storyju i osigurajte svoj kalendar na vrijeme. 🎁”
  - razlog: AI kritičar je prebacio obraćanje u veliko "Vi/Vam" (brif traži malo slovo); "iznenađenje za svaki prosinac" → "za svaki dan do Badnjaka"; dodana cijena s datumom iz izvora.

### Zašto je verzija 2 isprva ostala u ti-formi (popravak recepta, 26. 11. 2026.)
Nakon ispravka brifa prvo novo pokretanje izrade i dalje je pisalo u ti-formi. Uzrok je bio
u kodu, ne u modelu: faza izrade nije primala utvrđeni oblik obraćanja (ni brif), a primjeri u
`prompts/04_izrada.md` bili su u ti-formi. Popravljeno: izrada dobiva `oblik_obracanja` iz
analize i ton iz brifa, primjeri su u vi-formi, a `provjera.py` ima novu determinističku
provjeru (oblici 2. lica jednine su greška kad brend piše s „vi”, uključujući naljepnice).
Ta je provjera u istom pokretanju uhvatila gumb „Kupi na webshopu”, koji je AI kritičar zatim
ispravio u „Kupite na webshopu”.
