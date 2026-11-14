# MNUM - projekt 1.8 (MNUM-P1-26Zv2-08)

Kompletne rozwiązanie trzech punktów projektu: własny LDLᵀ, oryginalny GS.m oraz aproksymacja wielomianami stopni 3, 5, 7, 9, 10 przez równania normalne i QR.

## Uruchomienie

Rozpakuj ZIP. W MATLAB-ie ustaw folder `kod` jako Current Folder i uruchom:

```matlab
results = run_project;
```

Skrypt najpierw sprawdza solwery, następnie odtwarza eksperymenty i zapisuje tabele, współczynniki oraz wykresy w `wyniki`. Nie wymaga dodatkowych toolboxów. Zweryfikowano w MATLAB R2025b na Windows (szczegóły wersji w `wyniki/wyniki.json`). Ponowne uruchomienie zastąpi wygenerowane pliki wyników; czasy będą zależały od obciążenia komputera.

## Zawartość

- `Sprawozdanie_MNUM_P1_8.pdf`: 21 stron; wzory i wyprowadzenia, konkretne slajdy wykładów, tabele, wykresy, wyniki, wnioski i pełne listingi. Listingów nie przeplatano teorią.
- `Sprawozdanie_MNUM_P1_8.html`: edytowalna wersja treści raportu; obrazy w sąsiednim folderze `wyniki`.
- `kod/run_project.m`: wszystkie wymagane eksperymenty, pomiary, drukowanie i rysunki.
- `kod/ldlt_solve.m`: własny uniwersalny solwer LDLᵀ bez pivotingu i bez sprawdzania stosowalności metody, zgodnie z poleceniem.
- `kod/back_substitution.m`: własne podstawianie wstecz dla macierzy górnej trójkątnej.
- `kod/poly_lsq.m`: uniwersalna aproksymacja MNK przez normalne + LDLᵀ lub ekonomiczny QR.
- `kod/GS.m`: procedura Andrzeja Karbowskiego przekazana przez użytkownika; zachowana bez zmian.
- `kod/test_solvers.m`: niezależne sprawdzenia. Gotowy operator rozwiązywania układu występuje wyłącznie w testach jako odniesienie, poza solwerami.
- `wyniki`: CSV, MAT, JSON, PNG, log MATLAB-a i współczynniki z 17 cyframi znaczącymi.
- `zrodla`: treść zadania i cztery wykłady z podanego repozytorium.
- `generuj_sprawozdanie.py`: źródło PDF i HTML (wymaga Python + reportlab + Pillow oraz fontów Windows Arial, Cambria i Consolas). Po zmianie wyników uruchom `python generuj_sprawozdanie.py` z dowolnego katalogu. MATLAB nie przebudowuje automatycznie samego PDF-a.

## Przykłady wywołań

```matlab
A = [4, 1; 1, 3];
b = [1; 2];
[x, epsilon, L, d] = ldlt_solve(A, b);
% D = diag(d), A = L*D*L', epsilon = norm(A*x-b,2).

xdata = (-10:2:10).';
ydata = [-5.460;-3.880;-1.969;-1.666;-0.076;-0.397; ...
         -1.030;-4.548;-11.528;-21.641;-34.445];
[a,E2,Einf] = poly_lsq(xdata,ydata,5,'normal');
[a,E2,Einf] = poly_lsq(xdata,ydata,5,'qr');
[a,E2,Einf,info] = poly_lsq(xdata,ydata,5,'qr',true);
yfit = polyval(a,xdata);
```

`a` zawsze ma kolejność `[a_p;...;a_0]` i dotyczy oryginalnego x, również przy skalowaniu. `info.c` zawiera współczynniki w zmiennej t. Wymagane są co najmniej p+1 różnych węzłów i pełny rząd macierzy projektu. LDLᵀ bez pivotingu wymaga rzeczywistej symetrycznej macierzy i niezerowych kolejnych pivotów; dodatnia określoność jest warunkiem wystarczającym. Sama nieosobliwość nie wystarcza.

## Interpretacja i metodologia

- W zadaniach 1-2 `epsilon = norm(A*x-b,2)` oznacza normę reszty, nie bezpośrednią odległość od rozwiązania dokładnego. Dodatkowo obliczono względną normę reszty w zadaniu 1.
- W zadaniu 2 oba solwery otrzymują te same **pełne** macierze. Nie zmieniano oryginalnego GS.m i nie stosowano optymalizacji pasmowych. GS startuje od x=b, zatrzymuje się po `norm(xold-x)<=1e-9` lub `1000*n` iteracjach. To kryterium zmiany iteratów, a nie kryterium reszty.
- Zewnętrzne czasy zawierają obliczanie reszty, wykluczają tworzenie danych i wykresy. W zadaniach 1-2 użyto mediany z 3 pomiarów; w zadaniu 3 mediany z 201 wywołań po rozgrzewce.
- W zadaniu 3 podstawowy eksperyment używa potęg x. **Dodatkowy** wariant skaluje x do [-1,1]. Nie zastępuje on wymaganego eksperymentu. Mimo lepszego uwarunkowania w tym uruchomieniu reszta normalnych dla p=10 po skalowaniu była większa; raport wyjaśnia tę obserwację.
- Krzywe mają 1001 punktów, czyli krok 0.02 wobec kroku 2 danych. Wszystkie wartości wielomianów obliczane są funkcją `polyval`.
- `wyniki.json`: MATLAB spłaszcza tablicę komórek `coefficients` kolumnami: pierwszych 10 wektorów to normalne, następnych 10 to QR. W każdej dziesiątce kolejno stopnie 3,5,7,9,10 bez skalowania i 3,5,7,9,10 ze skalowaniem. Czytelniejszy zapis jest w `wspolczynniki.txt`.

## Pochodzenie materiałów

Repozytorium źródłowe: https://github.com/MateuszJakubiak591/MNUM_proj1

W raporcie wskazano numery slajdów Piotra Tatjewskiego. Wykłady 01-03 są wykorzystywane; wykład 04 o równaniach nieliniowych nie jest potrzebny. Dodatkowe wyprowadzenia dotyczą m.in. dominacji badanych macierzy, kosztu obliczeń i konwersji skali. Autorstwo oryginalnego GS.m pozostaje przypisane Andrzejowi Karbowskiemu.
