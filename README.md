# WEDT-Projekt
Projekt z przedmiotu WEDT - Wprowadzenie do eksploracji danych tekstowych w sieci WWW

Odpowiadanie na pytania (Question Answering). 2-3 os.
- jezyk implementacji: dowolny

Zadania:
1. Studia literaturowe.
2. Wybor rozwiazania.
3. Zgromadzenie i przygotowanie danych do uczenia.
4. Wytrenowanie modelu.

### Program `summary_search.py` 
Program zajmuje się odpytywaniem popularnych wyszukiwarek internetowych, celem zdobycia podsumowań (snippetów), z których wyciągane będą odpowiedzi na zadane pytania. Wykorzystuje on przeglądarkę headless, bez renderowania okna. Do jej uruchomienia, oprócz należy zainstalować odpowiedni driver do Firefoxa. Aby to zrobić, po zainstalowaniu środowiska i otworzeniu shella, należy wykonać polecenie `webdrivermanager firexox`. Pobierze to odpowiedni sterownik, zainstaluje w wirtualnym środowisku i pozwoli na uruchamianie przeglądarki w trybie headless.

### Program `kps.py`
Program który odpowiada na zadane pytania. Komunikuje się z innymi serwisami aby uzyskać potrzebną bazę wiedzy, wyniki analizy morfologicznej, rozkłady zdania oraz inne informacje potrzebne do ekstrakcji odpowiedzi.