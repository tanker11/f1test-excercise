# f1test-excercise

A megoldásban Forma-1-es eredményeket használok a 2023-as, befejezett idényből.
A kiválasztott adatforrás: https://openf1.org/?python#api-methods


## A megoldás vázlata
### Adatfelolvasás API interfészen keresztül - APILOAD
Az adatokat az openf1.org-ról API-n keresztül letöltjük és egy belső sqlite adatbázisba tesszük
A szolgáltatás a /health endpointon keresztük riportolja a folyamatot, illetve ha kész, akkor "ready" állapotot.
A /data endpointon keresztül egy előre gyártott SQL lekérdezés alapján "ömlesztve" felkínálja

### Adatok áttöltése - TRANSFORM
Az adatokat API-n keresztül áttöltjük, a felkínált, ömlesztett formában (egyetlen tábla)
A szolgáltatás a /health endpointon keresztük riportolja a folyamatot, illetve ha kész, akkor "ready" állapotot.
A /data endpointon keresztül egy előre gyártott SQL lekérdezés alapján szűrve felkínálja

### Adatfelolvasás API interfészen keresztül - DISPLAY
Az adatokat API-n keresztül áttöltjük, a felkínált, szűrt formában.
Ez már csak a szükséges adatokat tartalmazza.
Itt viszont a formátum nem felel meg a bokeh plot-nak, így át kell alakítani.
A legfontosabb elem, hogy a versenyzők pozíciói (positions) csak akkor szerepelnek, ha épp változik, egyéb esetben nincs hozzá adat.
A változások nem körönként, hanem időadattal vannak megadva, ezt a lekérdezés folyamán helyettesítjük egy folyamatos sorszámozással (a TRANSFORM lekérdezés folyamán)

#Az adatforrásból lehívott adatok
### MEETINGS - a versenyhétvégék
Itt érhető el a dokumentáció: https://openf1.org/?python#meetings

Tipikus output:
[
  {
    "circuit_key": 61,
    "circuit_short_name": "Singapore",
    "country_code": "SGP",
    "country_key": 157,
    "country_name": "Singapore",
    "date_start": "2023-09-15T09:30:00+00:00",
    "gmt_offset": "08:00:00",
    "location": "Marina Bay",
    "meeting_key": 1219,
    "meeting_name": "Singapore Grand Prix",
    "meeting_official_name": "FORMULA 1 SINGAPORE AIRLINES SINGAPORE GRAND PRIX 2023",
    "year": 2023
  }
]

### Sessions - Egy hétvégén belüli események
Példák: Practice 1,Practice 2,Practice 3, Qualifying, Race
Itt érhető el a dokumentáció: https://openf1.org/?python#sessions

Tipikus output:
[
  {
    "circuit_key": 7,
    "circuit_short_name": "Spa-Francorchamps",
    "country_code": "BEL",
    "country_key": 16,
    "country_name": "Belgium",
    "date_end": "2023-07-29T15:35:00+00:00",
    "date_start": "2023-07-29T15:05:00+00:00",
    "gmt_offset": "02:00:00",
    "location": "Spa-Francorchamps",
    "meeting_key": 1216,
    "session_key": 9140,
    "session_name": "Sprint",
    "session_type": "Race",
    "year": 2023
  }
]

### Position - Egy session-ön belül az elért helyezések

Itt érhető el a dokumentáció: https://openf1.org/?python#position

Tipikus output:
[
  {
    "date": "2023-08-26T09:30:47.199000+00:00",
    "driver_number": 40,
    "meeting_key": 1217,
    "position": 2,
    "session_key": 9144
  },
  {
    "date": "2023-08-26T09:35:51.477000+00:00",
    "driver_number": 40,
    "meeting_key": 1217,
    "position": 3,
    "session_key": 9144
  }
]

Itt a 40-es pilóta két időpillanatban elért pozícióját látjuk, előbb 2., majd 3. helyezést kapunk vissza eredményül.

### Weather - nem használtam fel az adatokat
Itt érhető el a dokumentáció: https://openf1.org/?python#weather

# VÁZLAT KÉP

# Modulok összefűzése
A 3 modul egymásra épül, így a második vizsgálja az első, a harmadik pedig vizsgálja a második állapotát a /health endpointon keresztül.
Akkor lép tovább, ha az "ready".
Az első automatikusan letölti az adatokat, a második "ready" után áttülti magának, a hatmadik pedig szintén "ready" után elkészíti a diagramot.

## Konténerizáció
A három odult egy-egy Dockerfile ír le a létrehozandó Python környezettel és a futtatandó parancsokkal együtt.
A három modul függőségekben való indítására pedig Docker Compose-t használunk, mely kijelöli a használt portokat.

# Használat
Telepítsük a Docker Desktopot magunknak.
Töltsük le ezt a Repository-t, és csomagoljuk ki.
Másoljuk be a fájlokat egy általunk választott helyre, és ott a terminálban adjuk ki a Docker Compose parancsot, hogy felépüljön a három mikorszolgáltatás konténere, és elinduljanak a szolgáltatások.

# IDE JÖN MAJD A VÉGEREDMÉNY MEGNÉZÉSÉNEK LEÍRÁSA

# Mit mutat be a megoldás
Ingyenes, webes F1 adatok letöltését, és átalakítás utáni megjelenítését böngészőben.
Három mikroszolgáltatás futtatását egy adatletöltés-feldolgozás-megjalanítés pipeline mentén, melyek elvégzik a fenti műveletet, miután egymás után felépültek, és jelentették egymásnak az állapotukat.

!!!A feladat nincsen finomhangolva és optimalizálva, lehetnek benne javítandó részek!!!