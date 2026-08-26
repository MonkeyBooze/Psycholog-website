"""Jedno źródło prawdy dla danych, które wcześniej były wpisane na sztywno w kilkunastu
szablonach i zdążyły się rozjechać: ceny, adresy, godziny otwarcia i treści FAQ.

Wszystko, co pojawia się na stronie więcej niż raz, ma być tutaj, inaczej wraca problem
z audytu, gdzie diagnoza ADHD kosztowała 400 zł na jednej podstronie i 500 zł na drugiej.

>>> DO POTWIERDZENIA PRZEZ WŁAŚCICIELA <<<
  - ceny: konsultacja / terapia / online (poniżej wartości z dotychczasowego cennika)
  - godziny otwarcia (w serwisie były trzy różne warianty)
  - liczba spotkań w diagnozie ADHD (2 czy 3)
  - ceny i zakres usług logopedycznych
"""

import json

SITE_URL = "https://spektrumumyslu.pl"
SITE_NAME = "Spektrum Umysłu"

PHONE_DISPLAY = "+48 606 841 722"
PHONE_SHORT = "606 841 722"
PHONE_E164 = "+48606841722"
EMAIL = "jakub.lewandowski@spektrumumyslu.pl"

ZNANYLEKARZ_URL = (
    "https://www.znanylekarz.pl/placowki/"
    "spektrum-umyslu-gabinety-psychoedukacji-logopedii-i-terapii"
)

# Widoczna na stronie odznaka z ZnanyLekarz. Świadomie NIE trafia do danych strukturalnych, # oznaczanie cudzych opinii jako własnych łamie wytyczne Google dla fragmentów z opiniami.
# >>> DO AKTUALIZACJI RĘCZNEJ, gdy liczba opinii wyraźnie urośnie <<<
REVIEWS = {"rating": "5,0", "count": 28, "url": ZNANYLEKARZ_URL}

# Godziny są takie same dla obu gabinetów. Format dni jak w schema.org.
OPENING_HOURS = {
    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "opens": "09:00",
    "closes": "20:00",
    "display": "codziennie w godzinach 9:00-20:00",
}

LOCATIONS = [
    {
        "slug": "opole",
        "city": "Opole",
        "locative": "Opolu",          # „gabinet w Opolu"
        "street": "ul. Bronisława Koraszewskiego 8/16",
        "postal_code": "45-011",
        "lat": "50.6682",
        "lng": "17.9260",
        "path": "/opole/",
        "maps_url": "https://maps.google.com/?q=Spektrum+Umyslu+Opole",
        "title": "Psycholog Opole, diagnoza ADHD i autyzmu | Spektrum Umysłu",
        "description": (
            "Gabinet psychologiczny w Opolu, ul. Koraszewskiego 8/16. Diagnoza ADHD (DIVA-5), "
            "autyzmu (ADOS-2), TUS, terapia. Tel. 606 841 722"
        ),
        "heading": "Psycholog Opole, gabinet przy ul. Koraszewskiego",
        "intro": (
            "Nasz opolski gabinet mieści się w ścisłym centrum miasta, przy ulicy Bronisława "
            "Koraszewskiego, kilka minut pieszo od Rynku i od placu Wolności. To główna lokalizacja "
            "Spektrum Umysłu, prowadzimy tu pełen zakres usług: diagnozę ADHD i spektrum autyzmu, "
            "terapię indywidualną, konsultacje oraz grupy TUS."
        ),
        "who": (
            "Do gabinetu w Opolu trafiają najczęściej osoby dorosłe, które przez lata podejrzewały "
            "u siebie ADHD lub cechy ze spektrum autyzmu i chcą to wreszcie sprawdzić rzetelnym "
            "narzędziem, a także rodzice szukający diagnozy dla dziecka i osoby w kryzysie, "
            "potrzebujące szybkiego terminu na konsultację."
        ),
        "practical": (
            "Gabinet jest przystosowany do spokojnej rozmowy, a wizyty planujemy tak, żeby osoby wchodzące i wychodzące nie mijały się "
            "w drzwiach. Ma to znaczenie zwłaszcza dla osób w spektrum, dla których przypadkowy "
            "kontakt bywa obciążający."
        ),
        "unavailable_services": [],
        "nearby": ["Brzeg", "Kędzierzyn-Koźle", "Krapkowice", "Namysłów",
                   "Strzelce Opolskie", "Ozimek", "Prószków"],
    },
    {
        "slug": "nysa",
        "city": "Nysa",
        "locative": "Nysie",
        "street": "ul. Celna 5",
        "postal_code": "48-300",
        "lat": "50.4736",
        "lng": "17.3330",
        "path": "/nysa/",
        "maps_url": "https://maps.google.com/?q=Spektrum+Umyslu+Nysa",
        "title": "Psycholog Nysa, diagnoza ADHD i autyzmu | Spektrum Umysłu",
        "description": (
            "Gabinet psychologiczny w Nysie, ul. Celna 5. Diagnoza ADHD (DIVA-5), autyzmu "
            "(ADOS-2), TUS, terapia i konsultacje. Tel. 606 841 722"
        ),
        "heading": "Psycholog Nysa, gabinet przy ul. Celnej",
        "intro": (
            "Gabinet w Nysie działa przy ulicy Celnej 5, w centrum miasta. Powstał dlatego, "
            "że mieszkańcy powiatu nyskiego po diagnozę ADHD czy badanie ADOS-2 musieli wcześniej "
            "jeździć do Opola albo do Wrocławia, a przy procesie złożonym z trzech spotkań "
            "dojazd potrafi przesądzić o tym, czy ktoś w ogóle podejmie diagnozę."
        ),
        "who": (
            "W Nysie przyjmujemy dzieci, młodzież i dorosłych. Największa część zgłoszeń dotyczy "
            "diagnozy spektrum autyzmu u dzieci oraz diagnozy ADHD u dorosłych, którzy rozpoznali "
            "u siebie objawy dopiero po diagnozie własnego dziecka. Prowadzimy tu również grupy TUS "
            "i terapię indywidualną."
        ),
        "practical": (
            "W mniejszym mieście łatwiej o krótki termin, w Nysie pierwsze spotkanie proponujemy "
            "zwykle szybciej niż w Opolu. Jeśli w jednej lokalizacji terminy są zajęte, sprawdzamy "
            "dostępność w drugiej; zespół i standard postępowania są takie same."
        ),
        # TUS prowadzimy wyłącznie w Opolu, więc nie pokazujemy go na stronie Nysy.
        "unavailable_services": ["tus"],
        "nearby": ["Otmuchów", "Paczków", "Głuchołazy", "Prudnik",
                   "Grodków", "Ziębice", "Korfantów"],
        "extra_note": (
            "Osoby z powiatu nyskiego, dla których nawet dojazd do Nysy jest kłopotem, mogą "
            "skorzystać z konsultacji i terapii online, z wyjątkiem badania ADOS-2, które "
            "wymaga bezpośredniej obserwacji."
        ),
    },
]

# `price` w złotych, `price_prefix` steruje słowem „od" (pełna diagnoza ma cenę stałą).
# `specs` to krótki opis pod kafelkiem usługi na stronie głównej i w blokach „Zobacz też".
SERVICES = {
    "konsultacja": {
        "name": "Konsultacja psychologiczna",
        "includes": [
            "Spotkanie 50 minut w gabinecie lub online",
            "Rozpoznanie sytuacji i nazwanie trudności",
            "Propozycja dalszego kierunku pracy",
            "Możliwość pojedynczego spotkania, bez zobowiązania",
        ],
        "price_label": "od 180 zł",
        "short": "Jedno lub kilka spotkań, żeby rozpoznać sytuację i wskazać kierunek dalszej pracy.",
        "path": "/konsultacje-psychologiczne/",
        "price": 180,
        "price_prefix": "od",
        "unit": "za spotkanie 50 minut",
        "duration": "50 min",
        "specs": "Spotkanie 50 min · od 180 zł",
    },
    "terapia": {
        "name": "Terapia indywidualna",
        "includes": [
            "Sesja 50 minut, zwykle raz w tygodniu",
            "Praca w nurcie CBT lub w terapii schematu",
            "Wspólnie ustalony plan i cele pracy",
            "Możliwość prowadzenia sesji online",
        ],
        "price_label": "od 200 zł",
        "short": "Regularna praca terapeutyczna w nurcie poznawczo-behawioralnym i w terapii schematu.",
        "path": "/terapia-indywidualna/",
        "price": 200,
        "price_prefix": "od",
        "unit": "za sesję 50 minut",
        "duration": "50 min",
        "specs": "Sesja 50 min · od 200 zł",
    },
    "online": {
        "name": "Konsultacja i terapia online",
        "includes": [
            "Sesja 50 minut przez bezpieczne połączenie wideo",
            "Link do spotkania, bez zakładania konta",
            "Dostępne z całej Polski i z zagranicy",
            "Ten sam psycholog, co w gabinecie",
        ],
        "price_label": "od 180 zł",
        "short": "Sesje przez bezpieczne połączenie wideo, z dowolnego miejsca w Polsce.",
        "path": "/wsparcie-online/",
        "price": 180,
        "price_prefix": "od",
        "unit": "za sesję 50 minut",
        "duration": "50 min",
        "specs": "Sesja 50 min · od 180 zł",
    },
    "adhd": {
        "name": "Diagnoza ADHD (DIVA-5)",
        "includes": [
            "Spotkanie 1: szczegółowy wywiad kliniczny, 250 zł",
            "Spotkania 2 i 3: badanie DIVA-5 oraz omówienie wyników, 500 zł",
            "Pisemna opinia psychologiczna z pieczątką i podpisem",
        ],
        "price_label": "750 zł za cały proces",
        "short": "Wywiad kliniczny i badanie DIVA-5 zgodne z DSM-5, zakończone pisemną opinią.",
        "path": "/diagnoza-adhd/",
        "price": 750,
        "price_prefix": "",
        "unit": "cały proces diagnostyczny z opinią",
        "duration": "3 spotkania × 1h",
        "specs": "3 spotkania · pełna opinia · 750 zł",
        "price_breakdown": [
            {"name": "Wywiad kliniczny", "price": 250},
            {"name": "Badanie DIVA-5 i omówienie wyników", "price": 500},
        ],
    },
    "autyzm": {
        "name": "Diagnoza autyzmu (ADOS-2)",
        "includes": [
            "Spotkanie 1: wywiad rozwojowy",
            "Spotkanie 2: badanie protokołem ADOS-2",
            "Spotkanie 3: omówienie wyników i zaleceń",
            "Pisemna opinia kliniczna z pieczątką i podpisem",
        ],
        "price_label": "1000 zł za cały proces",
        "short": "Diagnoza spektrum autyzmu protokołem ADOS-2, prowadzona przez certyfikowanych diagnostów.",
        "path": "/diagnoza-autyzmu/",
        "price": 1000,
        "price_prefix": "",
        "unit": "cały proces diagnostyczny z opinią",
        "duration": "3 spotkania × 1h",
        "specs": "3 spotkania · pełna opinia · 1000 zł",
    },
    "tus": {
        "name": "Trening Umiejętności Społecznych (TUS)",
        "includes": [
            "Spotkanie grupowe 60 minut",
            "Grupa 4-8 osób, dobierana pod względem wieku",
            "Rozliczenie za pojedyncze spotkanie",
            "Spotkanie kwalifikacyjne przed dołączeniem do grupy",
        ],
        "price_label": "120 zł za spotkanie",
        "short": "Zajęcia grupowe rozwijające kompetencje społeczne i komunikacyjne.",
        "path": "/trening-umiejetnosci-spolecznych/",
        "price": 120,
        "price_prefix": "",
        "unit": "za osobę, za jedno spotkanie",
        "duration": "cykl 10 spotkań × 60 min",
        "specs": "Cykl 10 spotkań · 120 zł za spotkanie",
    },
    "logopedia": {
        "name": "Terapia i diagnoza logopedyczna",
        "includes": [
            "Spotkanie 60 minut: 50 minut pracy z dzieckiem i 10 minut rozmowy z rodzicem",
            "Diagnoza logopedyczna przed rozpoczęciem terapii",
            "Plan terapii dostosowany do rodzaju zaburzenia",
            "Wskazówki i ćwiczenia do pracy w domu",
        ],
        "price_label": "od 130 zł",
        "short": "Diagnoza i terapia zaburzeń mowy u dzieci i dorosłych, prowadzona przez logopedę.",
        "path": "/logopedia/",
        "price": 130,
        "price_prefix": "od",
        "unit": "za spotkanie 60 minut",
        "duration": "60 min",
        "specs": "Spotkanie 60 min · od 130 zł",
    },

}

# TUS rozliczany jest za spotkanie, więc cały cykl liczymy raz tutaj, a nie w szablonie.
TUS_CYCLE_LENGTH = 10
TUS_CYCLE_PRICE = SERVICES["tus"]["price"] * TUS_CYCLE_LENGTH

# FAQ: jedno źródło dla widocznej sekcji na stronie i dla danych strukturalnych FAQPage.
# Google wymaga, żeby treść w JSON-LD była identyczna z widoczną na stronie, trzymanie
# obu w jednym miejscu jest jedynym sposobem, żeby to się nie rozjechało.
FAQ = {
    "diagnoza_adhd": [
        (
            "Czy diagnoza ADHD u dorosłych jest możliwa?",
            "Tak, ADHD może być zdiagnozowane w każdym wieku. U wielu osób objawy utrzymują się "
            "od dzieciństwa do dorosłości, ale niekiedy dopiero w życiu dorosłym stają się na tyle "
            "uciążliwe, że osoba poszukuje pomocy. Diagnoza u dorosłych jest równie ważna i możliwa "
            "jak u dzieci.",
        ),
        (
            "Ile kosztuje diagnoza ADHD?",
            f"Koszt pełnej diagnozy ADHD (3 spotkania po 1 godzinie wraz z pisemną opinią) wynosi "
            f"{SERVICES['adhd']['price']} zł: "
            + ", ".join(f"{p['price']} zł za {p['name'][0].lower()}{p['name'][1:]}"
                        for p in SERVICES["adhd"]["price_breakdown"])
            + ". Cena obejmuje wydanie oficjalnej opinii psychologicznej. "
              "Pełny cennik znajdziesz w zakładce Cennik.",
        ),
        (
            "Czy otrzymam oficjalną opinię diagnostyczną?",
            "Tak, po zakończeniu procesu diagnostycznego otrzymasz pisemną opinię psychologiczną "
            "zawierającą opis objawów, wynik diagnozy oraz zalecenia dotyczące dalszego postępowania. "
            "Opinia jest wydawana w formie papierowej z pieczątką i podpisem psychologa, co umożliwia "
            "wykorzystanie jej np. przy ubieganiu się o dostosowania w pracy lub szkole.",
        ),
        (
            "Czy diagnoza ADHD uprawnia do otrzymania recepty na leki?",
            "Psycholog nie ma uprawnień do wypisywania recept. Diagnoza psychologiczna może być "
            "jednak podstawą do skierowania do lekarza psychiatry, który podejmie decyzję "
            "o ewentualnym leczeniu farmakologicznym. Nasza opinia zawiera zalecenia dotyczące "
            "dalszego postępowania, w tym sugestię konsultacji psychiatrycznej, jeśli jest to wskazane.",
        ),
        (
            "Jak szybko dostanę termin na diagnozę ADHD?",
            "Pierwszy termin proponujemy zwykle w ciągu 3 dni roboczych od zgłoszenia. "
            "Diagnozę prowadzimy w gabinetach w Opolu i w Nysie, jeśli w jednej lokalizacji "
            "terminy są zajęte, zwykle da się umówić w drugiej.",
        ),
        (
            "Czym różni się DIVA-5 od testów dostępnych w internecie?",
            "DIVA-5 to ustrukturyzowany wywiad diagnostyczny prowadzony przez psychologa, "
            "zgodny z kryteriami DSM-5, obejmujący wszystkie 18 objawów ADHD w dzieciństwie "
            "i w dorosłości. Testy internetowe (np. ASRS) są narzędziami przesiewowymi, mogą "
            "zasugerować, że warto się zdiagnozować, ale nie stanowią diagnozy.",
        ),
    ],
    "diagnoza_autyzmu": [
        (
            "Czym jest test ADOS-2?",
            "ADOS-2 to protokół obserwacji do diagnozowania zaburzeń ze spektrum autyzmu, uznawany "
            "za „złoty standard” w diagnostyce ASD. Polega na ustrukturyzowanej obserwacji zachowań "
            "społecznych i komunikacyjnych w trakcie zaplanowanych zadań i rozmów. Badanie może "
            "przeprowadzić wyłącznie certyfikowany diagnosta.",
        ),
        (
            "Ile kosztuje diagnoza spektrum autyzmu?",
            f"Koszt pełnego procesu diagnostycznego z badaniem ADOS-2 i pisemną opinią wynosi "
            f"{SERVICES['autyzm']['price']} zł. "
            "Cena obejmuje wywiad rozwojowy, badanie ADOS-2 oraz spotkanie z omówieniem wyników "
            "i wydaniem opinii.",
        ),
        (
            "W jakim wieku można przeprowadzić diagnozę?",
            "ADOS-2 ma moduły dostosowane do wieku i poziomu rozwoju mowy, więc badanie jest możliwe "
            "zarówno u małych dzieci, jak i u młodzieży oraz osób dorosłych. Diagnozujemy wszystkie "
            "te grupy w gabinetach w Opolu i w Nysie.",
        ),
        (
            "Czy opinia jest honorowana przez poradnię psychologiczno-pedagogiczną?",
            "Wydajemy pisemną opinię psychologiczną z opisem przebiegu badania, wynikami i zaleceniami. "
            "Opinia prywatna nie zastępuje orzeczenia wydawanego przez publiczną poradnię "
            "psychologiczno-pedagogiczną, ale stanowi pełnowartościową dokumentację diagnostyczną, "
            "którą poradnia bierze pod uwagę w swoim postępowaniu.",
        ),
        (
            "Czy diagnoza autyzmu u dorosłych ma sens?",
            "Tak. Wiele osób, zwłaszcza kobiet, przez lata funkcjonuje bez diagnozy dzięki maskowaniu, "
            "które kosztuje ogromnie dużo energii. Diagnoza w dorosłości pozwala zrozumieć własne "
            "trudności, zmniejszyć poczucie winy i dobrać wsparcie dopasowane do rzeczywistych potrzeb.",
        ),
    ],
    "tus": [
        (
            "Dla kogo jest TUS?",
            "Trening Umiejętności Społecznych jest przeznaczony dla osób, które mają trudność "
            "w nawiązywaniu i utrzymywaniu relacji, w rozpoznawaniu emocji, w radzeniu sobie "
            "z konfliktem lub w odnalezieniu się w grupie. Prowadzimy grupy dla dzieci, młodzieży "
            "i dorosłych, w tym dla osób w spektrum autyzmu i z ADHD.",
        ),
        (
            "Ile kosztuje TUS?",
            "Jedno spotkanie grupowe kosztuje 120 zł za osobę. Pełny cykl 10 spotkań to łącznie "
            "1200 zł za uczestnika.",
        ),
        (
            "Jak liczne są grupy?",
            "Grupy liczą od 4 do 8 osób. Mniejsza grupa pozwala każdemu uczestnikowi realnie "
            "ćwiczyć umiejętności, a nie tylko obserwować.",
        ),
        (
            "Czy przed zapisaniem się trzeba przejść konsultację?",
            "Tak, przed dołączeniem do grupy umawiamy krótkie spotkanie kwalifikacyjne. Chodzi o to, "
            "żeby dobrać grupę pod względem wieku i potrzeb, źle dobrana grupa nie przynosi efektów.",
        ),
        (
            "Czy TUS wymaga wcześniejszej diagnozy?",
            "Nie. Diagnoza ADHD ani spektrum autyzmu nie jest warunkiem udziału. TUS jest treningiem "
            "konkretnych umiejętności i pomaga każdemu, kto ma trudności w relacjach.",
        ),
    ],
    "terapia_indywidualna": [
        (
            "Ile trwa terapia?",
            "To zależy od celu pracy. Terapia krótkoterminowa to zwykle 10-20 spotkań i koncentruje "
            "się na konkretnym problemie. Praca nad głębiej zakorzenionymi wzorcami trwa dłużej. "
            "Ramy ustalamy wspólnie na początku i weryfikujemy w trakcie.",
        ),
        (
            "W jakim nurcie pracujecie?",
            "Pracujemy głównie w nurcie poznawczo-behawioralnym (CBT) oraz w terapii schematu. "
            "CBT koncentruje się na związku między myślami, emocjami i zachowaniem; terapia schematu "
            "sięga do utrwalonych wzorców z wcześniejszych etapów życia.",
        ),
        (
            "Czym różni się terapia od konsultacji?",
            "Konsultacja to jedno lub kilka spotkań służących rozpoznaniu sytuacji i wskazaniu "
            "kierunku. Terapia to regularny, dłuższy proces prowadzony według wspólnie ustalonego "
            "planu. Jeśli nie wiesz, czego potrzebujesz, zacznij od konsultacji.",
        ),
        (
            "Ile kosztuje sesja terapeutyczna?",
            "Sesja indywidualna trwa 50 minut i kosztuje od 200 zł. Pełny cennik znajdziesz "
            "w zakładce Cennik.",
        ),
        (
            "Czy sesje są objęte tajemnicą zawodową?",
            "Tak. Psychologa obowiązuje tajemnica zawodowa. Treść spotkań nie jest udostępniana "
            "nikomu bez Twojej pisemnej zgody, poza sytuacjami wskazanymi wprost w przepisach "
            "(bezpośrednie zagrożenie życia lub zdrowia).",
        ),
    ],
    "konsultacje": [
        (
            "Kiedy warto umówić konsultację?",
            "Wtedy, gdy dzieje się coś trudnego i nie wiesz, od czego zacząć: kryzys, decyzja, "
            "której nie umiesz podjąć, przeciążenie, nagła zmiana życiowa. Konsultacja służy "
            "rozpoznaniu sytuacji i wskazaniu kierunku, nie musisz zobowiązywać się do terapii.",
        ),
        (
            "Ile kosztuje konsultacja psychologiczna?",
            "Spotkanie trwa 50 minut i kosztuje od 180 zł. Możliwe jest zarówno pojedyncze spotkanie, "
            "jak i kilka konsultacji z rzędu.",
        ),
        (
            "Czy jedno spotkanie może wystarczyć?",
            "Tak, i często wystarcza. Celem konsultacji jest uporządkowanie sytuacji i podjęcie "
            "decyzji o kolejnym kroku. Czasem tym krokiem jest terapia, czasem diagnoza, a czasem "
            "nic więcej nie jest potrzebne.",
        ),
        (
            "Jak szybko dostanę termin?",
            "Zwykle proponujemy termin w ciągu kilku dni roboczych. Przyjmujemy w gabinetach "
            "w Opolu i w Nysie oraz online.",
        ),
        (
            "Jak wygląda pierwsze spotkanie?",
            "Zaczynamy od rozmowy o tym, co Cię przywiodło i co chciałbyś zmienić. Psycholog zadaje "
            "pytania porządkujące obraz sytuacji, a na koniec proponuje możliwe kierunki dalszej "
            "pracy. Nie ma testów ani formularzy do wypełniania na starcie.",
        ),
    ],
    "wsparcie_online": [
        (
            "Czy terapia online jest tak samo skuteczna jak w gabinecie?",
            "Dla większości trudności, tak. Badania nad terapią poznawczo-behawioralną prowadzoną "
            "zdalnie pokazują skuteczność porównywalną z pracą w gabinecie. Wyjątkiem są sytuacje "
            "wymagające bezpośredniego kontaktu, np. diagnoza ADOS-2, której nie prowadzimy zdalnie.",
        ),
        (
            "Jak technicznie wygląda sesja online?",
            "Sesja odbywa się przez bezpieczne połączenie wideo. Przed pierwszym spotkaniem "
            "otrzymujesz link, nie musisz zakładać konta ani instalować dodatkowego oprogramowania. "
            "Potrzebujesz tylko spokojnego miejsca, słuchawek i stabilnego internetu.",
        ),
        (
            "Ile kosztuje sesja online?",
            "Sesja online trwa 50 minut i kosztuje od 180 zł.",
        ),
        (
            "Czy mogę korzystać z sesji online spoza województwa opolskiego?",
            "Tak. Sesje online prowadzimy dla osób z całej Polski i z zagranicy. Gabinety stacjonarne "
            "mamy w Opolu i w Nysie, ale w pracy zdalnej lokalizacja nie ma znaczenia.",
        ),
        (
            "Czy diagnozę ADHD można przeprowadzić online?",
            "Częściowo. Wywiad kliniczny i DIVA-5 da się przeprowadzić zdalnie, ale rekomendujemy "
            "przynajmniej jedno spotkanie na miejscu. Diagnozy spektrum autyzmu testem ADOS-2 "
            "nie prowadzimy online, protokół wymaga bezpośredniej obserwacji.",
        ),
    ],
}


def faq_schema(items):
    """FAQPage w JSON-LD zbudowany z tych samych krotek, co widoczna sekcja FAQ.

    Google wymaga, żeby odpowiedź w danych strukturalnych była identyczna z tą na stronie, składanie JSON-a w szablonie prędzej czy później rozjeżdża się z treścią.
    """
    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in items
        ],
    }
    # `<` uciekamy, żeby treść nie mogła przedwcześnie zamknąć znacznika <script>.
    return json.dumps(payload, ensure_ascii=False).replace("<", "\u003c")


# FAQ na stronach lokalizacyjnych, te same fakty, inne pytania niż na stronach usług.
LOCATION_FAQ = {
    "opole": [
        (
            "Jak umówić wizytę w gabinecie w Opolu?",
            "Najszybciej telefonicznie pod numerem 606 841 722, oddzwaniamy, jeśli nie odbierzemy. Można też zarezerwować termin przez ZnanyLekarz albo wypełnić formularz na stronie; na zgłoszenia z formularza odpowiadamy w ciągu 24 godzin.",
        ),
        (
            "Czy przyjmujecie w Opolu dzieci?",
            "Tak. W Opolu prowadzimy diagnozę i terapię dzieci, młodzieży oraz osób dorosłych. Dla dzieci i młodzieży prowadzimy również grupy TUS dobierane pod względem wieku.",
        ),
        (
            "Czy gabinet w Opolu przyjmuje na NFZ?",
            "Nie, jesteśmy gabinetem prywatnym i nie mamy kontraktu z NFZ. W praktyce oznacza to termin liczony w dniach zamiast w miesiącach oraz pełną dowolność w doborze specjalisty. Wystawiamy rachunek, który bywa podstawą do rozliczenia w ramach ubezpieczenia grupowego lub pakietu pracowniczego.",
        ),
        (
            "Czy mogę zrobić diagnozę w Opolu, a terapię prowadzić online?",
            "Tak i jest to częsty układ. Diagnoza wymaga spotkań na miejscu, natomiast dalszą pracę terapeutyczną można prowadzić zdalnie, z tym samym psychologiem, bez dojazdów.",
        ),
    ],
    "nysa": [
        (
            "Jak umówić wizytę w gabinecie w Nysie?",
            "Telefonicznie pod numerem 606 841 722, przez ZnanyLekarz lub formularzem na stronie. Przy zgłoszeniu warto od razu powiedzieć, czy chodzi o diagnozę, terapię czy konsultację, od tego zależy, ile czasu rezerwujemy na pierwsze spotkanie.",
        ),
        (
            "Jak szybko dostanę termin w Nysie?",
            "Zwykle szybciej niż w Opolu, pierwsze spotkanie proponujemy najczęściej w ciągu kilku dni roboczych. Jeśli terminy w Nysie akurat się skończyły, sprawdzamy dostępność w Opolu.",
        ),
        (
            "Czy gabinet w Nysie przyjmuje na NFZ?",
            "Nie, gabinet w Nysie działa prywatnie. Diagnoza ADHD i spektrum autyzmu w ramach NFZ wiąże się w naszym regionie z wielomiesięcznym oczekiwaniem; u nas cały proces zamyka się zwykle w kilku tygodniach od zgłoszenia.",
        ),
        (
            "Czy do Nysy przyjeżdżają pacjenci spoza miasta?",
            "Tak, znaczna część zgłoszeń pochodzi z powiatu nyskiego i okolic, Otmuchowa, Paczkowa, Głuchołaz, Prudnika i Grodkowa. Dla części osób jest to najbliższe miejsce, gdzie można wykonać badanie ADOS-2.",
        ),
    ],
}


# FAQ na stronie cennika, odpowiada na pytania, które padają przy pierwszym telefonie.
PRICING_FAQ = [
    (
        "Czy przyjmujecie na NFZ?",
        "Nie, jesteśmy gabinetem prywatnym i nie mamy kontraktu z NFZ. Diagnoza ADHD i spektrum "
        "autyzmu w ramach NFZ wiąże się w naszym regionie z wielomiesięcznym oczekiwaniem, "
        "u nas cały proces zamyka się zwykle w kilku tygodniach od zgłoszenia.",
    ),
    (
        "Czy cena diagnozy obejmuje opinię na piśmie?",
        "Tak. Zarówno w diagnozie ADHD, jak i spektrum autyzmu podana cena obejmuje wszystkie "
        "spotkania oraz pisemną opinię psychologiczną z pieczątką i podpisem. Nie ma dopłat "
        "za wydanie dokumentu.",
    ),
    (
        "Czy trzeba zapłacić za całą diagnozę z góry?",
        "Nie. Rozliczamy się po każdym spotkaniu, więc koszt rozkłada się na cały proces. "
        "Jeśli po pierwszym spotkaniu okaże się, że diagnoza nie jest wskazana, płacisz tylko "
        "za to spotkanie.",
    ),
    (
        "Czy wystawiacie rachunek?",
        "Tak, na życzenie wystawiamy rachunek. Bywa on podstawą do rozliczenia w ramach "
        "ubezpieczenia grupowego lub pakietu pracowniczego, warto wcześniej sprawdzić "
        "u swojego ubezpieczyciela, jakich dokumentów wymaga.",
    ),
    (
        "Czy sesje online są tańsze niż w gabinecie?",
        "Sesja online kosztuje tyle samo co konsultacja w gabinecie. Oszczędność jest po Twojej "
        "stronie, nie ponosisz kosztu i czasu dojazdu.",
    ),
    (
        "Czy ceny różnią się między Opolem a Nysą?",
        "Nie. W obu gabinetach obowiązuje ten sam cennik, ten sam zespół i ten sam standard "
        "postępowania diagnostycznego.",
    ),
]


# Zespół, dane zasilają jednocześnie widoczne biogramy i schemat Person (E-E-A-T).
# >>> DO UZUPEŁNIENIA: przy każdej osobie warto dopisać uczelnię i numery certyfikatów <<<
TEAM = [
    {
        "name": "Jakub Lewandowski",
        "role": "Psycholog i diagnosta",
        "photo": "images/jakub-lewandowski.jpg",
        "bio": "Jestem specjalistą diagnozy ADHD i autyzmu oraz interwencji kryzysowych i pracy z dorosłymi. Oferuję wsparcie w zrozumieniu procesów psychicznych, radzeniu sobie z trudnościami emocjonalnymi oraz rozwijaniu umiejętności społecznych. Dzięki indywidualnemu podejściu każdy pacjent otrzymuje pomoc dostosowaną do swoich potrzeb.",
        "knows_about": ["diagnoza ADHD", "diagnoza spektrum autyzmu", "interwencja kryzysowa", "psychologia dorosłych"],
    },
    {
        "name": "Justyna Lewandowska",
        "role": "Logopeda i certyfikowany diagnosta ADOS-2",
        "photo": "images/justyna-lewandowska.jpg",
        "bio": "Jestem certyfikowanym diagnostą ADOS-2 i logopedą z 18-letnim doświadczeniem w pracy z osobami w spektrum autyzmu, dziećmi i dorosłymi. W pracy kieruję się wrażliwością i uważnością na potrzeby drugiego człowieka.",
        "knows_about": ["ADOS-2", "diagnoza spektrum autyzmu", "logopedia", "rozwój mowy"],
    },
    {
        "name": "Dawid Bocz",
        "role": "Psycholog i diagnosta",
        "photo": "images/dawid-bocz.jpg",
        "bio": "Jestem terapeutą z kilkuletnim doświadczeniem w pracy z dziećmi i młodzieżą w Młodzieżowym Ośrodku Socjoterapii. Cierpliwość i aktywne słuchanie pozwalają młodym ludziom czuć się zrozumianymi i bezpiecznymi.",
        "knows_about": ["psychologia młodzieży", "socjoterapia", "praca z zachowaniami trudnymi"],
    },
    {
        "name": "Agata Janicka",
        "role": "Psycholog i diagnosta",
        "photo": "images/agata-janicka.jpg",
        "bio": "Jestem psychologiem pracującym z dziećmi, młodzieżą i dorosłymi. Na co dzień wspieram rozwój emocjonalny najmłodszych oraz towarzyszę dorosłym w odkrywaniu ich zasobów i radzeniu sobie z trudnościami. Prowadzę diagnozy psychologiczne, w tym diagnozę ADHD u dzieci i dorosłych.",
        "knows_about": ["diagnoza ADHD", "psychologia dziecięca", "rozwój emocjonalny"],
    },
    {
        "name": "Katarzyna Kuś-Kozłowska",
        "role": "Psycholog kliniczny, trener TUS",
        "photo": "images/katarzyna-kus.jpg",
        "bio": "Jestem magistrem psychologii klinicznej Uniwersytetu Opolskiego z przygotowaniem pedagogicznym oraz certyfikatem Trenera Umiejętności Społecznych. Pracuję w przedszkolach publicznych, gdzie wspieram dzieci oraz ich rodziców w zakresie rozwoju emocjonalno-społecznego. Jestem otwarta na współpracę z dziećmi i dorosłymi, również z neuroróżnorodnościami.",
        "knows_about": ["psychologia kliniczna", "trening umiejętności społecznych", "neuroróżnorodność"],
    },
    {
        "name": "Maja Rachwał",
        "role": "Psycholog i certyfikowana trenerka TUS",
        "photo": "images/maja-rachwal.jpg",
        "bio": "W swojej pracy opieram się na jasno określonych celach, zrozumieniu i poczuciu bezpieczeństwa. Jestem w trakcie studiów podyplomowych z przygotowania pedagogicznego dla psychologów oraz mam za sobą szkolenia z zakresu wsparcia w kryzysie, diagnozy psychologicznej, poradnictwa dla dzieci i młodzieży oraz pracy z pacjentami z ADHD i ASD. Jestem certyfikowaną trenerką TUS.",
        "knows_about": ["trening umiejętności społecznych", "ADHD", "spektrum autyzmu", "wsparcie w kryzysie"],
    },
    {
        "name": "Agata Brzozowska",
        "role": "Psycholog i diagnosta",
        "photo": "images/agata-brzozowska.jpg",
        "bio": "Pracuję z dorosłymi i dziećmi, prowadząc diagnozę oraz terapię w zakresie ADHD i spektrum autyzmu. Wspieram osoby, które chcą rozwijać swoje zasoby, lepiej radzić sobie z trudnościami oraz szukają wsparcia w kryzysie, w oparciu o empatię i indywidualne podejście.",
        "knows_about": ["diagnoza ADHD", "spektrum autyzmu", "psychologia dzieci i młodzieży"],
    },
]


# FAQ strony logopedycznej.
# >>> WSZYSTKIE ODPOWIEDZI PONIŻEJ WYMAGAJĄ WERYFIKACJI MERYTORYCZNEJ <<<
FAQ["logopedia"] = [
    (
        "Kiedy zgłosić się z dzieckiem do logopedy?",
        "Nie ma jednego progu wiekowego. Do konsultacji warto się zgłosić, gdy dziecko mówi wyraźnie "
        "mniej niż rówieśnicy, nie jest rozumiane przez osoby spoza rodziny, zniekształca głoski, "
        "jąka się albo wsuwa język między zęby. Wcześniejsza konsultacja zwykle oznacza krótszą terapię.",
    ),
    (
        "Czy prowadzicie terapię logopedyczną dla dorosłych?",
        "Tak. Pracujemy z dorosłymi nad wadami wymowy, jąkaniem i emisją głosu. Zakres pracy ustalamy "
        "po diagnozie logopedycznej.",
    ),
    (
        "Jak wygląda diagnoza logopedyczna?",
        "Zaczynamy od wywiadu, badania aparatu mowy i sprawdzenia, jak dziecko lub osoba dorosła "
        "realizuje poszczególne głoski. Na tej podstawie powstaje plan terapii z konkretnymi celami.",
    ),
    (
        "Ile trwa terapia logopedyczna?",
        "Zależy od rodzaju zaburzenia i od tego, czy ćwiczenia są powtarzane w domu. Korekta "
        "pojedynczej głoski to zwykle kilka do kilkunastu spotkań, praca nad opóźnionym rozwojem mowy "
        "albo nad jąkaniem trwa dłużej. Realny czas podajemy po diagnozie.",
    ),
    (
        "Czy logopeda pomoże dziecku w spektrum autyzmu?",
        "Tak, i jest to jeden z częstszych powodów zgłoszeń. Praca logopedyczna z dzieckiem w spektrum "
        "obejmuje nie tylko wymowę, ale też komunikację i rozumienie języka. Można ją prowadzić "
        "równolegle z diagnozą ADOS-2 i z zajęciami TUS.",
    ),
    (
        "Czy terapia logopedyczna jest możliwa online?",
        "Część pracy tak, zwłaszcza ze starszymi dziećmi i z dorosłymi. Diagnoza i praca nad aparatem "
        "artykulacyjnym u młodszych dzieci wymaga spotkania w gabinecie.",
    ),
]


# Zakres i przebieg terapii logopedycznej.
# >>> DO WERYFIKACJI MERYTORYCZNEJ: czy to pokrywa to, co faktycznie prowadzicie? <<<
# Trzy odrębne stawki. Jedna liczba w cenniku nie oddawała różnicy między samą
# diagnozą, pełną oceną kompetencji komunikacyjnych a spotkaniem terapeutycznym.
LOGOPEDIA_PRICES = [
    {"name": "Diagnoza logopedyczna", "scope": "", "price": 150},
    {"name": "Diagnoza, ocena rozwoju kompetencji komunikacyjnych",
     "scope": "wywiad rozwojowy z rodzicem i obserwacja dziecka", "price": 250},
    {"name": "Terapia logopedyczna",
     "scope": "60 minut: 50 minut pracy z dzieckiem i 10 minut rozmowy z rodzicem",
     "price": 130},
]

LOGOPEDIA_SCOPE = [
    {
        "title": "Opóźniony rozwój mowy",
        "text": "Dziecko mówi wyraźnie mniej niż rówieśnicy albo zaczęło mówić później. "
                "Sprawdzamy, czy to kwestia tempa rozwoju, czy zaburzenia wymagającego terapii.",
    },
    {
        "title": "Wady wymowy",
        "text": "Seplenienie, nieprawidłowe realizowanie głoski r, mowa bezdźwięczna, "
                "wsuwanie języka między zęby. Praca polega na wypracowaniu prawidłowego wzorca "
                "i utrwaleniu go w mowie spontanicznej.",
    },
    {
        "title": "Jąkanie i niepłynność mowy",
        "text": "Powtórzenia, przeciąganie głosek, blokowanie się na początku wypowiedzi. "
                "Pracujemy nad płynnością i nad napięciem, które jej towarzyszy.",
    },
    {
        "title": "Mowa a spektrum autyzmu",
        "text": "Wsparcie komunikacji u dzieci w spektrum: rozumienie języka, budowanie wypowiedzi, "
                "komunikacja funkcjonalna. Prowadzone równolegle z diagnozą i z zajęciami TUS.",
    },
    {
        "title": "Trudności w czytaniu i pisaniu",
        "text": "Kłopoty z analizą i syntezą słuchową, mylenie liter, wolne tempo czytania. "
                "Diagnoza logopedyczna pomaga ustalić, czy podłoże jest językowe.",
    },
    {
        "title": "Dorośli",
        "text": "Wady wymowy, które zostały z dzieciństwa, emisja głosu, praca nad wyrazistością "
                "mowy u osób pracujących głosem.",
    },
]

LOGOPEDIA_STEPS = [
    {
        "title": "Diagnoza logopedyczna",
        "text": "Wywiad, badanie aparatu mowy i sprawdzenie, jak realizowane są poszczególne głoski. "
                "Bez tego etapu terapia byłaby zgadywaniem.",
    },
    {
        "title": "Plan terapii",
        "text": "Ustalamy cele, częstotliwość spotkań i zakres ćwiczeń do wykonywania w domu. "
                "Plan omawiamy z rodzicem albo z osobą dorosłą, której dotyczy terapia.",
    },
    {
        "title": "Spotkania terapeutyczne",
        "text": "Regularne sesje po 50 minut. Rodzic dostaje materiał do ćwiczeń między spotkaniami, "
                "bo to praca w domu decyduje o tempie postępów.",
    },
    {
        "title": "Ocena postępów",
        "text": "Co jakiś czas sprawdzamy, na ile cele zostały osiągnięte, i decydujemy, czy terapię "
                "kontynuować, zmodyfikować, czy zakończyć.",
    },
]


# ---------------------------------------------------------------------------
# Standardy Ochrony Małoletnich
#
# Podstawa prawna: art. 22b i 22c ustawy z 13 maja 2016 r. o przeciwdziałaniu zagrożeniom
# przestępczością na tle seksualnym i ochronie małoletnich (tzw. ustawa Kamilka).
# Obowiązek posiadania i publikacji na stronie internetowej obowiązuje od 15 sierpnia 2024 r.
# Ustawa wymaga DWÓCH wersji dokumentu: pełnej oraz skróconej, zrozumiałej dla małoletnich.
#
# >>> DOKUMENT PRAWNY. WYMAGA ZATWIERDZENIA PRZED PUBLIKACJĄ. <<<
# Do uzupełnienia przez właściciela:
#   - imię i nazwisko osoby odpowiedzialnej za przyjmowanie zgłoszeń
#   - imię i nazwisko osoby odpowiedzialnej za standardy i szkolenie personelu
#   - data przyjęcia dokumentu i data najbliższego przeglądu
# ---------------------------------------------------------------------------

CHILD_PROTECTION_META = {
    "responsible_person": "Jakub Lewandowski, psycholog, właściciel gabinetu",
    "training_person": "Jakub Lewandowski, psycholog, właściciel gabinetu",
    "adopted_on": "24 sierpnia 2026 r.",
    # Art. 22c ust. 6: ocena standardów co najmniej raz na dwa lata.
    "review_due": "24 sierpnia 2028 r.",
    "legal_basis": (
        "Ustawa z dnia 13 maja 2016 r. o przeciwdziałaniu zagrożeniom przestępczością "
        "na tle seksualnym i ochronie małoletnich (art. 22b i 22c)"
    ),
}

CHILD_PROTECTION = [
    (
        "Cel i zakres standardów",
        [
            "Standardy Ochrony Małoletnich obowiązują wszystkie osoby pracujące w gabinetach "
            "Spektrum Umysłu w Opolu i w Nysie: psychologów, diagnostów, logopedów, trenerów TUS, "
            "osoby współpracujące oraz osoby wykonujące czynności pomocnicze.",

            "Naczelną zasadą jest dobro małoletniego. Każda osoba z personelu ma obowiązek działać "
            "w granicach obowiązującego prawa i wewnętrznych procedur, a w razie podejrzenia "
            "krzywdzenia małoletniego zareagować niezwłocznie.",

            "Standardy stosuje się do wszystkich form kontaktu z małoletnim: spotkań "
            "diagnostycznych, terapeutycznych, zajęć grupowych oraz kontaktu zdalnego.",
        ],
    ),
    (
        "Zasady bezpiecznych relacji personelu z małoletnim",
        [
            "Kontakt z małoletnim odbywa się wyłącznie w ramach umówionych spotkań, w gabinecie "
            "lub podczas zajęć grupowych, w godzinach pracy placówki.",

            "Personel zwraca się do małoletniego z szacunkiem, w sposób dostosowany do jego wieku "
            "i możliwości rozumienia. Małoletni jest informowany o tym, co będzie się działo "
            "na spotkaniu, i ma prawo zadawać pytania.",

            "Kontakt fizyczny jest ograniczony do sytuacji uzasadnionych metodyką pracy "
            "lub bezpieczeństwem, zawsze za wiedzą małoletniego i w sposób dla niego zrozumiały.",

            "Zachowania niedozwolone wobec małoletniego to w szczególności: stosowanie przemocy "
            "fizycznej i psychicznej, poniżanie, wyśmiewanie, krzyk, groźby, kary fizyczne, "
            "zachowania i wypowiedzi o charakterze seksualnym, nawiązywanie z małoletnim relacji "
            "prywatnych, kontaktowanie się poza kanałami placówki, przyjmowanie i wręczanie "
            "korzyści majątkowych, utrwalanie wizerunku bez zgody, spożywanie alkoholu "
            "lub przyjmowanie substancji psychoaktywnych w obecności małoletniego.",

            "Personel nie kontaktuje się z małoletnim przez prywatne numery telefonów, prywatne "
            "konta w komunikatorach ani w mediach społecznościowych.",
        ],
    ),
    (
        "Zasady bezpiecznych relacji między małoletnimi",
        [
            "Podczas zajęć grupowych obowiązuje zakaz przemocy fizycznej i słownej, wykluczania, "
            "wyśmiewania oraz nagrywania i fotografowania innych uczestników.",

            "Prowadzący zajęcia ustala z grupą zasady na pierwszym spotkaniu i reaguje na każde "
            "ich naruszenie, także wtedy, gdy zgłoszenie pochodzi od uczestnika.",

            "W razie konfliktu prowadzący rozdziela strony, wysłuchuje każdej z osobna "
            "i informuje rodziców lub opiekunów prawnych zaangażowanych małoletnich.",
        ],
    ),
    (
        "Procedura interwencji przy podejrzeniu krzywdzenia",
        [
            "Krok 1. Osoba, która powzięła podejrzenie krzywdzenia małoletniego, niezwłocznie "
            "zgłasza je osobie odpowiedzialnej za przyjmowanie zgłoszeń. Zgłoszenie sporządza "
            "się na piśmie, opisując fakty, a nie oceny.",

            "Krok 2. Osoba odpowiedzialna zapewnia małoletniemu bezpieczeństwo, w tym przerywa "
            "kontakt z osobą podejrzewaną o krzywdzenie, i rozmawia z małoletnim w sposób "
            "dostosowany do jego wieku, bez wywierania nacisku i bez zadawania pytań sugerujących.",

            "Krok 3. Osoba odpowiedzialna informuje rodziców lub opiekunów prawnych, chyba że "
            "zachodzi podejrzenie, że to oni są sprawcami krzywdzenia.",

            "Krok 4. W zależności od charakteru sprawy podejmowane jest zawiadomienie właściwych "
            "organów, zgodnie z procedurą opisaną w kolejnym punkcie.",

            "Krok 5. Sporządzana jest notatka z przebiegu interwencji, a małoletniemu proponowany "
            "jest plan wsparcia.",
        ],
    ),
    (
        "Zawiadamianie organów",
        [
            "Podejrzenie popełnienia przestępstwa na szkodę małoletniego zgłaszane jest "
            "do prokuratury lub na policję. Obowiązek zawiadomienia o przestępstwach wskazanych "
            "w art. 240 Kodeksu karnego, w tym o przestępstwach seksualnych wobec małoletniego, "
            "ma charakter bezwzględny.",

            "W sprawach dotyczących zagrożenia dobra małoletniego, które nie wypełniają znamion "
            "przestępstwa, kierowany jest wniosek do sądu rodzinnego właściwego ze względu "
            "na miejsce zamieszkania małoletniego.",

            "W razie podejrzenia przemocy domowej wszczynana jest procedura Niebieskiej Karty.",

            "Zawiadomienie nie wymaga pewności. Wystarczy uzasadnione podejrzenie. Ocena "
            "wiarygodności należy do organów ścigania, nie do personelu placówki.",
        ],
    ),
    (
        "Osoby odpowiedzialne",
        [
            "Za przyjmowanie zgłoszeń o krzywdzeniu małoletniego oraz za wszczęcie procedury "
            "interwencji odpowiada osoba wskazana w danych na końcu dokumentu.",

            "Za wdrożenie standardów, ich znajomość wśród personelu, monitorowanie stosowania "
            "oraz organizację szkoleń odpowiada osoba wskazana w danych na końcu dokumentu.",

            "W razie nieobecności osoby odpowiedzialnej zgłoszenie przyjmuje inna osoba "
            "z personelu, która niezwłocznie przekazuje je dalej.",
        ],
    ),
    (
        "Weryfikacja personelu",
        [
            "Przed dopuszczeniem do pracy z małoletnimi każda osoba jest weryfikowana "
            "w Rejestrze Sprawców Przestępstw na Tle Seksualnym, w tym w rejestrze z dostępem "
            "ograniczonym i w rejestrze osób, w stosunku do których Państwowa Komisja "
            "do spraw wyjaśniania przypadków czynności skierowanych przeciwko wolności seksualnej "
            "i obyczajności wobec małoletniego poniżej lat 15 wydała postanowienie o wpisie.",

            "Osoba przyjmowana do pracy przedkłada informację z Krajowego Rejestru Karnego "
            "w zakresie przestępstw określonych w ustawie oraz oświadczenie o państwach, "
            "w których zamieszkiwała w ostatnich 20 latach.",

            "Wydruki i oświadczenia są przechowywane w dokumentacji placówki.",
        ],
    ),
    (
        "Ochrona wizerunku i danych małoletniego",
        [
            "Wizerunek małoletniego nie jest utrwalany ani publikowany bez pisemnej zgody "
            "rodzica lub opiekuna prawnego, a w przypadku małoletniego powyżej 13. roku życia "
            "również bez jego zgody.",

            "Dane małoletniego, w tym treść spotkań i dokumentacja diagnostyczna, są objęte "
            "tajemnicą zawodową i przetwarzane zgodnie z RODO oraz z polityką prywatności placówki.",

            "Dokumentacja jest udostępniana wyłącznie osobom uprawnionym, na zasadach opisanych "
            "w polityce prywatności.",
        ],
    ),
    (
        "Urządzenia elektroniczne i kontakt zdalny",
        [
            "Podczas zajęć małoletni nie korzystają z urządzeń elektronicznych, chyba że jest "
            "to element metodyki pracy i odbywa się pod nadzorem prowadzącego.",

            "Spotkania zdalne z małoletnim odbywają się wyłącznie przez kanały wskazane przez "
            "placówkę, za wiedzą i zgodą rodzica lub opiekuna prawnego.",

            "Personel nie nagrywa spotkań z małoletnim bez pisemnej zgody rodzica "
            "lub opiekuna prawnego.",
        ],
    ),
    (
        "Plan wsparcia małoletniego",
        [
            "Po ujawnieniu krzywdzenia małoletniemu proponowany jest plan wsparcia obejmujący "
            "wskazanie osoby kontaktowej w placówce, ustalenie form pomocy psychologicznej "
            "oraz, jeśli to potrzebne, skierowanie do innych instytucji.",

            "Plan jest omawiany z rodzicem lub opiekunem prawnym, chyba że zachodzi podejrzenie, "
            "że to on jest sprawcą krzywdzenia.",

            "Realizacja planu jest monitorowana przez osobę odpowiedzialną.",
        ],
    ),
    (
        "Dokumentowanie, przegląd i udostępnianie",
        [
            "Każde zgłoszenie i każda interwencja są dokumentowane w rejestrze prowadzonym "
            "przez osobę odpowiedzialną. Dokumentacja jest przechowywana w sposób uniemożliwiający "
            "dostęp osobom nieuprawnionym.",

            "Standardy podlegają przeglądowi i w razie potrzeby aktualizacji nie rzadziej "
            "niż raz na dwa lata, a także po każdym zdarzeniu, które ujawni ich niedoskonałość.",

            "Standardy są udostępnione na stronie internetowej placówki oraz w widocznym miejscu "
            "w każdym gabinecie, w wersji pełnej i w wersji skróconej dla małoletnich.",
        ],
    ),
]

# Wersja skrócona, wymagana ustawą, napisana językiem zrozumiałym dla dziecka.
CHILD_PROTECTION_SHORT = [
    (
        "Masz prawo czuć się tu bezpiecznie",
        "Przychodzisz do nas, żeby ktoś Ci pomógł. Nikt nie ma prawa Cię tu skrzywdzić: "
        "ani uderzyć, ani wyśmiewać, ani mówić do Ciebie w sposób, który sprawia, że czujesz się źle.",
    ),
    (
        "Możesz pytać i możesz odmówić",
        "Zawsze możesz zapytać, co będziemy robić na spotkaniu i po co. Jeśli czegoś nie chcesz "
        "robić albo o czymś nie chcesz mówić, powiedz to. To jest w porządku.",
    ),
    (
        "To, co mówisz, zostaje między nami",
        "Nie opowiadamy innym o tym, co mówisz na spotkaniu. Jedyny wyjątek jest wtedy, gdy "
        "dowiemy się, że ktoś Cię krzywdzi albo że jesteś w niebezpieczeństwie. Wtedy musimy "
        "poprosić o pomoc dorosłych, którzy potrafią Cię ochronić. Zawsze powiemy Ci o tym wprost.",
    ),
    (
        "Powiedz komuś, jeśli dzieje się coś złego",
        "Jeśli ktoś Cię krzywdzi, straszy albo robi coś, co sprawia, że czujesz się nieswojo, "
        "powiedz o tym osobie, z którą się spotykasz, albo komukolwiek innemu u nas. Nie musisz "
        "mieć dowodów. Nie musisz być pewien. Wystarczy, że powiesz.",
    ),
    (
        "Nie jesteś winny",
        "Jeśli ktoś Cię skrzywdził, to nigdy nie jest Twoja wina. Nie będziemy Cię za to oceniać "
        "ani karać. Naszym zadaniem jest Ci pomóc.",
    ),
    (
        "Gdzie jeszcze możesz zadzwonić",
        "Telefon Zaufania dla Dzieci i Młodzieży: 116 111, czynny całą dobę, bezpłatny. "
        "Telefon alarmowy: 112.",
    ),
]
