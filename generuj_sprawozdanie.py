"""Buduje PDF i edytowalny HTML ze zbadanych wynikow MATLAB-a.
Wymaga reportlab; nie przelicza ani nie wymysla wynikow pomiarow.
"""
from pathlib import Path
import json, html, re, textwrap
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                               Table, TableStyle, Image, Preformatted, KeepTogether)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parent
W = ROOT/'wyniki'
data = json.loads((W/'wyniki.json').read_text(encoding='utf-8'))
for name, filename in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),
                       ('Arial-Italic','ariali.ttf'),('Consolas','consola.ttf'),
                       ('Times','times.ttf'),('Cambria','cambria.ttc')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+filename))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
pdfmetrics.registerFontFamily('Cambria',normal='Cambria',bold='Cambria',italic='Cambria',boldItalic='Cambria')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle('BodyPL',fontName='Arial',fontSize=10,leading=14.5,spaceAfter=8))
styles.add(ParagraphStyle('HeadPL',fontName='Arial-Bold',fontSize=18,leading=23,spaceAfter=17,textColor=colors.HexColor('#14354f')))
styles.add(ParagraphStyle('SubPL',fontName='Arial-Bold',fontSize=11,leading=15,spaceBefore=7,spaceAfter=8,textColor=colors.HexColor('#14354f')))
styles.add(ParagraphStyle('EqPL',fontName='Cambria',fontSize=12,leading=18,spaceBefore=5,spaceAfter=10,leftIndent=8))
styles.add(ParagraphStyle('SmallPL',fontName='Arial',fontSize=8,leading=11,spaceAfter=6))
styles.add(ParagraphStyle('CodePL',fontName='Consolas',fontSize=7.4,leading=9.5))
story=[]; source=[]
def p(s,sty='BodyPL'):
    # Arial nie zawiera czesci symboli matematycznych. Jawna czcionka
    # z pelnym zestawem glifow zapobiega pustym kwadratom w PDF.
    rendered=s
    if sty!='EqPL':
        for c in sorted(set(s)):
            if ord(c)>127 and ord(c) not in pdfmetrics.getFont('Arial').face.charToGlyph:
                if ord(c) not in pdfmetrics.getFont('Cambria').face.charToGlyph:
                    raise ValueError('Brak glifu: '+repr(c))
                rendered=rendered.replace(c,'<font name="Cambria">'+c+'</font>')
    story.append(Paragraph(rendered,styles[sty])); source.append(f'<p class="{sty}">{s}</p>')
def eq(s): p(s,'EqPL')
def sub(s): p(s,'SubPL')
def page(title):
    if story: story.append(PageBreak())
    source.append('<div class="page"></div>'); p(title,'HeadPL')
def table(headers,rows,widths=None,small=False):
    sty=styles['SmallPL' if small else 'BodyPL']
    def cell(v):
        s=str(v)
        for c in sorted(set(s)):
            if ord(c)>127 and ord(c) not in pdfmetrics.getFont('Arial').face.charToGlyph:
                s=s.replace(c,'<font name="Cambria">'+c+'</font>')
        return Paragraph(s,sty)
    cells=[[cell(v) for v in row] for row in [headers]+rows]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4edf3')),
                          ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#53758e')),
                          ('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#ccd6df')),
                          ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
                          ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.append(t); story.append(Spacer(1,10))
    source.append('<table>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in [headers]+rows)+'</table>')
def fig(filename,width=490):
    from PIL import Image as PILImage
    path=W/filename
    with PILImage.open(path) as im: iw,ih=im.size
    story.append(Image(str(path),width=width,height=width*ih/iw))
    story.append(Spacer(1,8)); source.append(f'<img src="wyniki/{filename}" style="width:100%">')
def sci(x): return f'{x:.3e}'
def tm(x): return f'{x:.6f}'

page('MNUM - projekt 1.8')
p('Układy liniowe: LDL<super>T</super> i Gauss-Seidel.<br/>Aproksymacja wielomianowa: równania normalne i QR.','SubPL')
p('Opracowanie do zadania <b>MNUM-P1-26Zv2-08.pdf</b>. Kod, wzory, samodzielne wyprowadzenia, eksperymenty i komentarze. Wyniki pochodzą z dołączonego uruchomienia MATLAB-a; czasy zależą od komputera i obciążenia.')
sub('Co wykorzystano z wykładów?')
table(['Materiał Piotra Tatjewskiego','Slajdy / zastosowanie'],[
    ['MNUM_01_PojPodst_slajdy.pdf','8-12: reprezentacja, zaokrąglenia, double i eps. Podstawa interpretacji dokładności.'],
    ['MNUM_02_RownLn_slajdy.pdf','1-5: normy; 8-11: uwarunkowanie; 12-13: podstawianie; 38-45: LLᵀ i LDLᵀ; 53-57: iteracje i Gauss-Seidel.'],
    ['MNUM_03WartWl_slajdy.pdf','1-3: ortogonalność i wąski QR; 31-33: MNK, równania normalne, cond₂(AᵀA) i przejście do QR.'],
    ['MNUM_04RownNln_slajdy.pdf','Nie jest potrzebny: projekt nie dotyczy równań nieliniowych.'],
    ['GS.m - Andrzej Karbowski','Oryginalna procedura przekazana przez użytkownika. Komentarz wskazuje podręcznik P. Tatjewskiego, Metody Numeryczne, OWPW 2013, s. 59. Nie korzystano z treści podręcznika poza tym opisem.']
],widths=[180,315],small=True)
p('Numery oznaczają strony PDF, zgodne z numeracją slajdów. Wyprowadzenia poniżej zapisano samodzielnie na podstawie tych wzorów. Dowody dominacji dla konkretnych macierzy, analiza kosztu, konwersja skali i komentarze do eksperymentów są uzupełnieniem opracowania.','SmallPL')
p('Materiały źródłowe: <link href="https://github.com/MateuszJakubiak591/MNUM_proj1" color="#235e84">github.com/MateuszJakubiak591/MNUM_proj1</link>. Kopie wykorzystanych PDF-ów znajdują się w folderze zrodla. Pełne listingi zebrano na końcu, oddzielnie od teorii.','SmallPL')

page('1. Rozkład LDLᵀ - wyprowadzenie')
p('Szukamy rozkładu rzeczywistej macierzy symetrycznej A = LDLᵀ. L jest dolna trójkątna, l<sub>ii</sub> = 1; D jest diagonalna. W kodzie d(i) przechowuje d<sub>ii</sub>. Oznaczenie L odpowiada macierzy jednostkowej dolnej z wykładu; nie jest to L z rozkładu Cholesky’ego LLᵀ.')
eq('a<sub>ji</sub> = (LDLᵀ)<sub>ji</sub> = ∑<sub>k=1</sub><super>min(j,i)</super> l<sub>jk</sub>d<sub>kk</sub>l<sub>ik</sub>.')
p('W i-tej kolumnie zaczynamy od j = i. Oddzielamy składnik k = i. Ponieważ l<sub>ii</sub> = 1, otrzymujemy:')
eq('a<sub>ii</sub> = ∑<sub>k=1</sub><super>i−1</super> l<sub>ik</sub>²d<sub>kk</sub> + d<sub>ii</sub>,')
eq('<b>d<sub>ii</sub> = a<sub>ii</sub> − ∑<sub>k=1</sub><super>i−1</super> l<sub>ik</sub>²d<sub>kk</sub>.</b>')
p('Dla j &gt; i ostatni składnik sumy ma postać l<sub>ji</sub>d<sub>ii</sub>. Stąd:')
eq('a<sub>ji</sub> = ∑<sub>k=1</sub><super>i−1</super> l<sub>jk</sub>d<sub>kk</sub>l<sub>ik</sub> + l<sub>ji</sub>d<sub>ii</sub>,')
eq('<b>l<sub>ji</sub> = (a<sub>ji</sub> − ∑<sub>k=1</sub><super>i−1</super> l<sub>jk</sub>d<sub>kk</sub>l<sub>ik</sub>) / d<sub>ii</sub>.</b>')
p('Pierwsza kolumna: d<sub>11</sub> = a<sub>11</sub>, l<sub>j1</sub> = a<sub>j1</sub>/d<sub>11</sub>. Następnie wyznaczamy kolumny i = 2,...,n. Puste sumy mają wartość zero. W kodzie wektor v<sub>k</sub> = d<sub>kk</sub>l<sub>ik</sub> pozwala wykonać te same sumy za pomocą mnożenia macierzy przez wektor.')
sub('Rozwiązanie układu po faktoryzacji')
eq('Ax = b ⇒ LDLᵀx = b ⇒ Ly = b, Dz = y, Lᵀx = z.')
eq('y<sub>i</sub> = b<sub>i</sub> − ∑<sub>j=1</sub><super>i−1</super> l<sub>ij</sub>y<sub>j</sub>,     i = 1,...,n;')
eq('z<sub>i</sub> = y<sub>i</sub>/d<sub>ii</sub>;')
eq('x<sub>i</sub> = z<sub>i</sub> − ∑<sub>j=i+1</sub><super>n</super> l<sub>ji</sub>x<sub>j</sub>,     i = n,...,1.')
p('Są to bezpośrednio równania wierszowe układów trójkątnych. W procedurze nie ma wywołań ldl, chol, inv ani operatora rozwiązującego układ. Dzielenie przez pojedynczy d<sub>ii</sub> jest zwykłym dzieleniem skalarnym. Źródło: wykład 02, slajdy 12 oraz 42-43.','SmallPL')

page('2. Stosowalność, koszt i dokładność')
p('Zgodnie z poleceniem solwer nie sprawdza symetrii, dodatniej określoności ani pivotów. Analizujemy je tutaj. Wersja bez przestawień wymaga niezerowych kolejnych d<sub>ii</sub>; sama nieosobliwość nie wystarcza. Przykład A = [0,1;1,0] jest nieosobliwy, ale pierwszy pivot wynosi zero. Dla macierzy symetrycznych dodatnio określonych wszystkie pivoty są dodatnie.')
sub('Macierz z zadania 1')
eq('a<sub>ij</sub> = 2(i+j)+1 (i ≠ j),   a<sub>ii</sub> = 4n²+(2i+4)n,   b<sub>i</sub> = 2.5+0.6i.')
eq('s<sub>i</sub> = ∑<sub>j≠i</sub>|a<sub>ij</sub>| = (2n−4)i+n²+2n−1,')
eq('a<sub>ii</sub>−s<sub>i</sub> = 3n²+4i+2n+1 &gt; 0.')
p('A jest symetryczna i ściśle diagonalnie dominująca z dodatnią przekątną. Dodatnią określoność można wykazać bez obliczania wartości własnych: z 2|x<sub>i</sub>x<sub>j</sub>| ≤ x<sub>i</sub>²+x<sub>j</sub>² wynika poniższe oszacowanie.')
eq('xᵀAx ≥ ∑<sub>i=1</sub><super>n</super> (a<sub>ii</sub>−s<sub>i</sub>)x<sub>i</sub>² &gt; 0,   x ≠ 0.')
eq('κ₂(A) ≤ (9n²+2n−1)/(3n²+2n+5) &lt; 3  (n ≥ 2).')
p('Ostatnia nierówność wynika z dolnego ograniczenia λ<sub>min</sub> przez min(a<sub>ii</sub>−s<sub>i</sub>) i górnego λ<sub>max</sub> przez max(a<sub>ii</sub>+s<sub>i</sub>). Są to dobrze uwarunkowane układy, mimo rosnących elementów macierzy.')
sub('Koszt procedury ogólnej')
eq('∑<sub>i=1</sub><super>n</super> (n−i)(i−1) = n(n−1)(n−2)/6.')
p('Tyle składników występuje w sumach dla elementów pod przekątną. Każdy wymaga mnożenia i dodawania; dochodzą operacje O(n²). Faktoryzacja ma więc koszt Θ(n³), każde podstawianie Θ(n²), pamięć Θ(n²). Przechowanie D jako wektora wymaga O(n). Czasy MATLAB-a zależą także od wektoryzacji, pamięci i bibliotek BLAS.')
sub('Co oznacza wymagany „błąd”?')
eq('r = Ax̃−b,   ε = ‖r‖₂,   ε<sub>rel</sub> = ‖r‖₂/‖b‖₂.')
eq('A(x̃−x*) = r ⇒ ‖x̃−x*‖₂/‖x*‖₂ ≤ κ₂(A) ‖r‖₂/‖b‖₂.')
p('ε jest normą reszty, a nie bezpośrednio odległością od dokładnego x*. Ostatnia nierówność wynika z normy A⁻¹ i ‖b‖₂ ≤ ‖A‖₂‖x*‖₂. Reszta bezwzględna rośnie także ze skalą b; nie musi być stałą wielokrotnością eps. W MATLAB-ie eps = 2⁻⁵² ≈ 2.220446·10⁻¹⁶; unit roundoff przy zaokrąglaniu double to u = 2⁻⁵³. Wykład 01, slajd 12, rozróżnia te pojęcia.')

page('3. Gauss-Seidel - wyprowadzenie')
p('W tej sekcji A = L + D + U, gdzie L i U są ściśle trójkątne, a D diagonalna. To inne macierze L,D niż w faktoryzacji LDLᵀ. Z równania Ax = b przenosimy Ux na prawą stronę, a do iteracji podstawiamy poprzednie przybliżenie:')
eq('(D+L)x<super>(k+1)</super> = b−Ux<super>(k)</super>.')
p('W i-tym równaniu składniki o indeksach j &lt; i są już wyznaczone w bieżącym przebiegu. Składniki o indeksach j &gt; i pochodzą z przebiegu poprzedniego:')
eq('x<sub>i</sub><super>(k+1)</super> = (b<sub>i</sub> − ∑<sub>j=1</sub><super>i−1</super> a<sub>ij</sub>x<sub>j</sub><super>(k+1)</super>')
eq('                                      − ∑<sub>j=i+1</sub><super>n</super> a<sub>ij</sub>x<sub>j</sub><super>(k)</super>) / a<sub>ii</sub>.')
p('Oryginalny GS.m oblicza najpierw w = Ux−b, a następnie podstawia w przód. Startuje od x<sup>(0)</sup> = b. Iteracja oznacza pełny przebieg po i = 1,...,n, nie pojedynczą aktualizację składowej.')
eq('Stop: ‖x<super>(k)</super>−x<super>(k−1)</super>‖₂ ≤ δ  lub  k = itmax,')
eq('δ = 10⁻⁹,   itmax = 1000n.')
p('Zwracana liczba iexe to liczba pełnych przebiegów. texe jest czasem mierzonym wewnątrz GS.m; w tabeli podano również zewnętrzny czas całej operacji razem z obliczeniem reszty. Kryterium stopu bada zmianę przybliżenia, a nie bezpośrednio normę reszty.')
sub('Macierz z zadania 2 i zbieżność')
eq('a<sub>ii</sub> = 24.5,   a<sub>i,i±3</sub> = −5 (o ile indeks jest w zakresie),')
eq('a<sub>ij</sub> = 0 dla pozostałych,   b<sub>i</sub> = −6+0.5i.')
p('Suma modułów elementów poza przekątną nie przekracza 10, więc 24.5 &gt; 10. Macierz jest symetryczna dodatnio określona na mocy oszacowania z poprzedniej strony; GS jest zbieżny. Wartości własne leżą w [14.5,34.5], zatem κ₂(A) ≤ 34.5/14.5 ≈ 2.38.')
p('Dla błędu iteracji e<sup>(k)</sup> = x<sup>(k)</sup>−x* mamy (D+L)e<sup>(k+1)</sup> = −Ue<sup>(k)</sup>. Ogólny warunek zbieżności to promień spektralny macierzy iteracji mniejszy od 1 (wykład 02, slajd 53). Tutaj każdy wewnętrzny wiersz ma co najwyżej jeden poprzednik i jeden następnik o współczynniku 5. Indukcja po wierszach daje poniższą, niezależną od n, ocenę:')
eq('‖e<super>(k+1)</super>‖∞ ≤ q‖e<super>(k)</super>‖∞,   q ≤ 5/(24.5−5) ≈ 0.25641.')
p('Ta sama ocena dotyczy różnic kolejnych iteracji. Dla kryterium w normie 2 można dodatkowo użyć ‖v‖₂ ≤ √n‖v‖∞. Liczba iteracji może nieznacznie rosnąć z n i normą punktu startowego. Ogólna wersja GS.m na macierzy pełnej wykonuje Θ(kn²) działań i przechowuje Θ(n²) danych. Wersja świadoma pasma mogłaby osiągnąć Θ(kn), ale takiej optymalizacji nie wprowadzano do oryginału.')

page('4. Wielomiany i równania normalne')
p('Dla m = 11 par (x<sub>i</sub>,y<sub>i</sub>) wyznaczamy wielomiany stopni p = 3,5,7,9,10. Ustalamy kolejność współczynników zgodną z polyval:')
eq('f(x) = a<sub>p</sub>x<super>p</super> + a<sub>p−1</sub>x<super>p−1</super> + ... + a<sub>1</sub>x + a<sub>0</sub>,')
eq('a = [a<sub>p</sub>, a<sub>p−1</sub>, ..., a<sub>0</sub>]ᵀ,   V<sub>ij</sub> = x<sub>i</sub><super>p−j+1</super>,   j = 1,...,p+1.')
p('Macierz V to macierz projektu, na slajdach MNK oznaczana A. Użycie V odróżnia ją od macierzy układów z zadań 1-2. Jej ostatnia kolumna jest jedynkowa, a Va to wartości wielomianu w węzłach.')
eq('J(a) = ‖Va−y‖₂² = (Va−y)ᵀ(Va−y)')
eq('        = aᵀVᵀVa − 2aᵀVᵀy + yᵀy.')
p('Różniczkujemy względem wektora a. Ponieważ VᵀV jest symetryczna, gradient składnika kwadratowego wynosi 2VᵀVa, a liniowego −2Vᵀy:')
eq('∇J(a) = 2VᵀVa−2Vᵀy = 0 ⇒ <b>VᵀVa = Vᵀy.</b>')
p('Dla dowolnego niezerowego z zachodzi zᵀVᵀVz = ‖Vz‖₂². Węzły są różne, a p ≤ 10. Niezerowy wielomian stopnia p nie może mieć 11 różnych zer, więc kolumny V są liniowo niezależne. Stąd VᵀV jest dodatnio określona, hesjan 2VᵀV dodatnio określony, a znaleziony punkt jest jedynym minimum globalnym.')
eq('G = VᵀV,   h = Vᵀy,   G = LDLᵀ,   Ga = h.')
p('Układ Ga = h rozwiązujemy dokładnie własnym solwerem z zadania 1. W arytmetyce zmiennopozycyjnej utworzenie G pogarsza dokładność: dla wartości szczególnych σ₁ ≥ ... ≥ σ<sub>p+1</sub> &gt; 0 macierzy V wartości własne VᵀV to ich kwadraty.')
eq('κ₂(VᵀV) = σ₁²/σ<sub>p+1</sub>² = κ₂(V)².')
p('To tożsamość dla macierzy dokładnej. W kolumnie cond_gram_computed_2 mierzona jest macierz G już zaokrąglona w MATLAB-ie; przy bardzo złym uwarunkowaniu nie musi spełniać tej równości numerycznie. Źródło równań normalnych i kwadratu uwarunkowania: wykład 03, slajdy 31-32.')
sub('Błędy aproksymacji')
eq('r<sub>i</sub> = polyval(a,x<sub>i</sub>)−y<sub>i</sub>,')
eq('E₂ = ‖r‖₂ = √(∑<sub>i=1</sub><super>m</super> r<sub>i</sub>²),   E∞ = ‖r‖∞ = max<sub>i</sub>|r<sub>i</sub>|.')
p('E₂ jest minimalizowane przez MNK; E∞ jest dodatkową miarą jakości i nie jest celem tej optymalizacji. Mała reszta układu Ga = h nie oznacza małego błędu aproksymacji E₂. Są to dwa różne problemy i dwie różne reszty.')

page('5. QR, skalowanie i obliczanie wartości')
p('Stosujemy wąski, znormalizowany rozkład V = QR, gdzie Q ma m wierszy i p+1 kolumn, QᵀQ = I, a R jest kwadratowa górna trójkątna. W MATLAB-ie odpowiada mu [Q,R] = qr(V,0).')
eq('VᵀVa = Vᵀy ⇒ RᵀQᵀQRa = RᵀQᵀy ⇒ RᵀRa = RᵀQᵀy.')
p('R jest nieosobliwa, więc lewostronne skrócenie przez Rᵀ daje:')
eq('<b>Ra = Qᵀy.</b>')
p('To wyprowadzenie algebraiczne nie oznacza tworzenia równań normalnych w kodzie QR. Kod oblicza Q,R bez tworzenia VᵀV, a następnie rozwiązuje układ trójkątny własnym podstawianiem:')
eq('a<sub>i</sub> = (c<sub>i</sub> − ∑<sub>j=i+1</sub><super>p+1</super> R<sub>ij</sub>a<sub>j</sub>)/R<sub>ii</sub>,   c = Qᵀy.')
p('Niezależne wyjaśnienie geometryczne: Va należy do przestrzeni kolumn Q, a (I−QQᵀ)y jest do niej prostopadły. Twierdzenie Pitagorasa daje:')
eq('‖Va−y‖₂² = ‖Ra−Qᵀy‖₂² + ‖(I−QQᵀ)y‖₂².')
p('Drugi składnik nie zależy od a; pierwszy ma minimum zero dla Ra = Qᵀy. Ponieważ Q zachowuje długości wektorów, V i R mają te same wartości szczególne, zatem κ₂(R) = κ₂(V). QR unika kwadratu wskaźnika uwarunkowania. Źródło: wykład 03, slajdy 1-3 i 33.')
sub('Dodatkowy eksperyment: przeskalowanie zmiennej')
eq('t = (x−μ)/s,   μ = (min(x)+max(x))/2,   s = max<sub>i</sub>|x<sub>i</sub>−μ|.')
p('Tutaj μ = 0, s = 10, więc t = x/10 ∈ [−1,1]. Rozwiązujemy ten sam problem w bazie potęg t. Przestrzeń wielomianów się nie zmienia, zatem w dokładnej arytmetyce nie zmienia się optymalna funkcja. Zmieniają się skale kolumn i błędy numeryczne.')
eq('g(t) = ∑<sub>k=0</sub><super>p</super> c<sub>k</sub>t<super>k</super>,   f(x) = g((x−μ)/s),')
eq('a<sub>j</sub> = ∑<sub>k=j</sub><super>p</super> c<sub>k</sub>s<super>−k</super> (k nad j) (−μ)<super>k−j</super>;   μ = 0 ⇒ a<sub>j</sub> = c<sub>j</sub>/s<super>j</super>.')
p('Wzór wynika z dwumianu Newtona dla (x−μ)<sup>k</sup>. Implementacja dokonuje tej konwersji przez składanie wielomianów w schemacie Hornera, dlatego zawsze zwraca a dla oryginalnego x. Do oceny wartości używa polyval(a,x), także do błędów w tabelach.')
eq('f(x) = (...((a<sub>p</sub>x+a<sub>p−1</sub>)x+a<sub>p−2</sub>)x+...)+a<sub>0</sub>.')
p('Horner wynika z kolejnego wyłączania x przed nawias. Wymaga p mnożeń i p dodawań na punkt. Krzywe rysujemy w 1001 punktach od −10 do 10: krok 0.02 wobec kroku 2 danych, czyli 100 razy gęściej niż próbki. Skalowanie, konwersja i powyższe wyprowadzenie Hornera są uzupełnieniem opracowania.')

page('6. Pomiary - zadanie 1')
meta=data['meta']; t1=data['task1']; t2=data['task2']; t3=data['task3']
p(f"Środowisko: MATLAB {html.escape(meta['matlab'])}, {meta['computer']}. Zapis uruchomienia: {meta['timestamp']} (czas lokalny). Typ danych double; eps = {meta['eps']:.16g}.")
p('Po wstępnej rozgrzewce solwerów dla każdego n wykonano trzy pomiary zewnętrznym tic/toc; tabela pokazuje medianę. Czas obejmuje faktoryzację, rozwiązanie i obliczenie reszty, a wyklucza tworzenie danych, drukowanie i rysowanie. Nie jest to sam czas faktoryzacji. Reszta jest wynikiem ostatniego powtórzenia.')
table(['n','czas LDLᵀ [s]','ε = ‖Ax̃−b‖₂','ε / ‖b‖₂'],[[r['n'],tm(r['time_ldlt_s']),sci(r['residual_2']),sci(r['relative_residual_2'])] for r in t1],widths=[55,130,150,160],small=True)
fig('zadanie1.png')
lo,hi=t1[0],t1[-1]
p(f"Reszty bezwzględne mieszczą się w zakresie {sci(min(r['residual_2'] for r in t1))} do {sci(max(r['residual_2'] for r in t1))}. Są małymi ułamkami; reszty względne są rzędu {sci(max(r['relative_residual_2'] for r in t1))} lub mniejsze. Z oszacowania κ₂(A)&lt;3 wynika mały błąd względny rozwiązania. Rosnąca reszta bezwzględna nie oznacza pogarszania uwarunkowania.")
p(f"Czas dla n=2000 wyniósł {hi['time_ldlt_s']:.3f} s wobec {lo['time_ldlt_s']:.6f} s dla n=50. Oczekiwany koszt jest sześcienny; nie należy dopasowywać dokładnie n³ do krótkich czasów zdominowanych przez narzuty, JIT i zmiany sprawności operacji pamięciowych.")

page('7. Pomiary - zadanie 2')
p('Obie metody otrzymują tę samą pełną macierz (full). Nie wykorzystano sparse ani specjalnego algorytmu pasmowego. Dzięki temu porównanie dotyczy podanych implementacji. Pomimo wielu zer ogólny LDLᵀ wykonuje mnożenia pełnych fragmentów macierzy.')
table(['n','LDLᵀ [s]','ε LDLᵀ','GS [s]','ε GS','iteracje'],[[r['n'],tm(r['time_ldlt_s']),sci(r['residual_ldlt_2']),tm(r['time_gs_s']),sci(r['residual_gs_2']),r['iterations_gs']] for r in t2],widths=[45,85,95,85,105,80],small=True)
fig('zadanie2.png')
p(f"GS wykonał od {min(r['iterations_gs'] for r in t2)} do {max(r['iterations_gs'] for r in t2)} iteracji, znacznie mniej niż limit 1000n. Odpowiada to silnej dominacji diagonalnej i ocenie kontrakcji niezależnej od n. Nie ma powodu oczekiwać liczby iteracji proporcjonalnej do liczby równań.")
p(f"Maksymalna reszta LDLᵀ to {sci(max(r['residual_ldlt_2'] for r in t2))}, a GS {sci(max(r['residual_gs_2'] for r in t2))}. GS kończy po osiągnięciu δ dla zmiany iteratów, dlatego jego reszta jest większa niż metody bezpośredniej i nie musi wynosić δ. Obie metody prowadzą do bliskich rozwiązań; największa norma ich różnicy wyniosła {sci(max(r['difference_solutions_2'] for r in t2))}.")
last=t2[-1]
p(f"Przy n=2000 zmierzono {last['time_ldlt_s']:.3f} s dla LDLᵀ oraz {last['time_gs_s']:.3f} s dla GS (stosunek LDLᵀ/GS = {last['time_ldlt_s']/last['time_gs_s']:.2f}). Dla macierzy pełnej GS ma koszt Θ(kn²), a LDLᵀ Θ(n³). Porównanie czasów dla małych n może być zaburzone narzutem pętli i przygotowania D,L,U.")
p('W pliku zadanie2.csv dodatkowo zapisano czas texe zwracany przez GS.m. Nie obejmuje on obliczenia reszty na zewnątrz; dlatego wykresy i główna tabela używają porównywalnych zewnętrznych pomiarów. Pełne dane liczbowe i różnice rozwiązań są dostępne w CSV, MAT i JSON.','SmallPL')

page('8. Pomiary - aproksymacja')
p('Dane: x = −10,−8,...,10; y = [−5.460, −3.880, −1.969, −1.666, −0.076, −0.397, −1.030, −4.548, −11.528, −21.641, −34.445]. E₂ i E∞ są liczone wyłącznie w tych 11 punktach.')
sub('Wariant podstawowy: bez skalowania, V w potęgach x')
table(['p','E₂ normalne','E∞ normalne','E₂ QR','E∞ QR','κ₂(V)'],[[r['degree'],sci(r['error_normal_2']),sci(r['error_normal_inf']),sci(r['error_qr_2']),sci(r['error_qr_inf']),sci(r['cond_V_2'])] for r in t3[:5]],widths=[30,95,100,90,95,85],small=True)
sub('Wariant dodatkowy: skalowanie t = x/10')
table(['p','E₂ normalne','E∞ normalne','E₂ QR','E∞ QR','κ₂(V)'],[[r['degree'],sci(r['error_normal_2']),sci(r['error_normal_inf']),sci(r['error_qr_2']),sci(r['error_qr_inf']),sci(r['cond_V_2'])] for r in t3[5:]],widths=[30,95,100,90,95,85],small=True)
p('Dla p=10 liczba współczynników jest równa liczbie danych. W dokładnej arytmetyce otrzymujemy wielomian interpolacyjny i zerową resztę. Pozostałe reszty są skutkiem zaokrągleń. To nie dowodzi dobrej jakości modelu pomiędzy węzłami ani poza zakresem danych.')
p('Przestrzenie wielomianów są zagnieżdżone, więc minimalny E₂ w dokładnej arytmetyce nie może rosnąć ze stopniem. E∞ nie ma analogicznej gwarancji dla rozwiązań MNK. Różnice między normalnymi a QR przy wysokich stopniach należy wiązać przede wszystkim z uwarunkowaniem i arytmetyką, nie z innym celem optymalizacji.')
sub('Czasy [µs] - mediany z 201 wywołań po rozgrzewce')
table(['p','normalne, x','QR, x','normalne, x/10','QR, x/10'],[[t3[i]['degree'],f"{1e6*t3[i]['time_normal_s']:.2f}",f"{1e6*t3[i]['time_qr_s']:.2f}",f"{1e6*t3[i+5]['time_normal_s']:.2f}",f"{1e6*t3[i+5]['time_qr_s']:.2f}"] for i in range(5)],widths=[35,115,115,115,115],small=True)
p('Mierzono całą poly_lsq: budowę V, rozwiązanie, konwersję współczynników i obliczenie błędów. Kolejność wywołań obu metod zmieniano naprzemiennie. Dla tak małych macierzy narzuty funkcji są istotne, a wbudowane QR korzysta ze zoptymalizowanych bibliotek. Nie można na tej podstawie twierdzić, że jedna metoda zawsze jest szybsza.')

page('9. Otrzymane funkcje na tle danych')
p('Wariant wymagany: bez skalowania. Każdy panel przedstawia osobny stopień, dane pomiarowe oraz obie metody. Nakładanie się krzywych oznacza zbliżone dopasowanie w skali rysunku, nie identyczność wszystkich cyfr współczynników.')
fig('zadanie3_skala0.png')
p('Krzywe obliczono funkcją polyval w 1001 punktach. Szczególnie dla p=9 i p=10 dopasowanie w węzłach może współistnieć z wyraźnymi oscylacjami między nimi. Wysoki stopień zwiększa swobodę modelu; nie ma danych walidacyjnych, które pozwalałyby ocenić błąd względem nieznanej funkcji rzeczywistej.')
sub('Jak czytać współczynniki?')
p('Pełne wektory wszystkich stopni i obu metod zapisano w wyniki/wspolczynniki.txt z 17 cyframi znaczącymi. Kolejność to [a_p,...,a_0]. Na kolejnych stronach podano wybrane wartości oraz wszystkie wektory QR po skalowaniu. Nie są to współczynniki w zmiennej t: kod przelicza je na oryginalne x.')

page('10. Wpływ skalowania i uwarunkowania')
fig('zadanie3_skala1.png')
sub('Porównanie wskaźników uwarunkowania')
table(['p','κ₂(V), potęgi x','κ₂(V), potęgi x/10','κ₂(V)², baza x'],[[t3[i]['degree'],sci(t3[i]['cond_V_2']),sci(t3[i+5]['cond_V_2']),sci(t3[i]['cond_V_2']**2)] for i in range(5)],widths=[35,155,155,150],small=True)
p('W bazie x najwyższa potęga dla p=10 osiąga 10¹⁰, podczas gdy kolumna stała ma wartość 1. W bazie x/10 potęgi mają moduł nie większy niż 1. Skalowanie ogranicza różnice wielkości kolumn i zmniejsza uwarunkowanie, ale nie usuwa wszystkich problemów bazy jednomianowej. Dla większych stopni można rozważać bazy ortogonalne; nie jest to część wymaganego projektu.')
p(f"W tym uruchomieniu dla p=10 reszta normalnych po skalowaniu wyniosła {sci(t3[9]['error_normal_2'])}, wobec {sci(t3[4]['error_normal_2'])} bez skalowania, czyli była większa mimo znacznie mniejszego κ₂(V). Wskaźnik uwarunkowania opisuje wrażliwość w najgorszym przypadku, a nie gwarantowaną resztę konkretnego obliczenia. Zmieniają się zaokrąglenia przy tworzeniu G, faktoryzacji i ocenie wielomianu; nie wolno deklarować automatycznej poprawy każdej mierzonej reszty.")

page('11. Błędy i koszty aproksymacji')
fig('zadanie3_bledy_czasy.png')
p('Normalne i QR rozwiązują to samo zadanie MNK. Gdy reszta dopasowania jest znacznie większa od błędów zaokrągleń, obie metody dają niemal ten sam E₂. Przy interpolacji p=10 te błędy stają się widoczne, bo teoretyczna reszta wynosi zero.')
p('Dla m punktów i q=p+1 współczynników utworzenie V kosztuje O(mq). Równania normalne wymagają O(mq²) na VᵀV i O(q³) na LDLᵀ. Wąski QR ma koszt O(mq²) dla m≥q. Obie metody mają więc podobny rząd kosztu, lecz różne stałe i własności numeryczne. QR jest zwykle bezpieczniejszym wyborem przy źle uwarunkowanej macierzy projektu.')

page('12. Współczynniki i wnioski')
sub('Wielomiany QR po skalowaniu - współczynniki dla x')
for i in range(5,10):
    # jsonencode komorek MATLAB-a splaszcza tablice 10x2 kolumnami:
    # pierwsze 10 wektorow to normalne, nastepne 10 to QR.
    pdeg=t3[i]['degree']; coef=data['coefficients'][i+10]
    # MATLAB moze zapisac wektor kolumnowy jako plaska tablice JSON.
    vals=[float(v[0] if isinstance(v,list) else v) for v in coef]
    p(f'<b>p = {pdeg}</b>: ['+', '.join(f'{v:.10g}' for v in vals)+']','SmallPL')
sub('Wnioski końcowe')
p('1. Własny LDLᵀ rozwiązuje oba typy dobrze uwarunkowanych układów z małymi resztami. Ogólna faktoryzacja bez pivotingu jest uzasadniona dodatnią określonością badanych macierzy, a nie samym faktem ich nieosobliwości.')
p('2. GS jest zbieżny dzięki silnej dominacji diagonalnej. Dla rosnącego n wykonuje niewiele iteracji w porównaniu z dopuszczonym limitem. Mniejszy koszt uzyskuje przy dokładności określonej przez δ; nie ma tej samej reszty co metoda bezpośrednia.')
p('3. Obie metody MNK minimalizują tę samą sumę kwadratów. Normalne wzmacniają problem uwarunkowania przez kwadrat κ₂(V). QR nie tworzy VᵀV, dlatego lepiej zachowuje dokładność, szczególnie przy wysokich stopniach.')
p('4. Skalowanie x do [−1,1] poprawia uwarunkowanie bez zmiany przestrzeni aproksymujących funkcji. Nie gwarantuje mniejszej reszty w każdym obliczeniu. Stopień 10 interpoluje 11 danych, ale zerowa reszta w próbkach nie stanowi dowodu najlepszego modelu. Bez założeń o błędach pomiarów i zbioru walidacyjnego nie można wskazać stopnia najlepszego do przewidywania.')
sub('Uruchomienie i weryfikacja')
p('W MATLAB-ie przejdź do folderu kod i wykonaj <b>results = run_project;</b>. Skrypt najpierw wywoła test_solvers, a potem odtworzy pomiary, wykresy, CSV, JSON i MAT. Sam PDF można odbudować skryptem generuj_sprawozdanie.py po ponownym uruchomieniu eksperymentów.')
p('Testy porównują własny LDLᵀ z rozwiązaniem referencyjnym A&#92;b poza solwerem, kontrolują odtworzenie A = LDLᵀ oraz znany wielomian. Obejmują n=1, macierze losowe dodatnio określone, macierz nieokreśloną z niezerowymi pivotami i konwersję skali na niesymetrycznej dziedzinie. Wszystkie testy zakończyły się poprawnie.')
p('Plik GS.m zachowano bez zmian obliczeniowych. Rysunki i drukowanie znajdują się poza solwerami. Wywołanie wbudowanego QR występuje jedynie w dozwolonej gałęzi aproksymacji; gotowe rozwiązanie układu jest używane tylko jako odniesienie w osobnym pliku testowym.','SmallPL')

# Pelne listingi: oddzielna czesc, bez przeplatania z wyprowadzeniami.
files=['ldlt_solve.m','back_substitution.m','poly_lsq.m','GS.m','test_solvers.m','run_project.m']
for filename in files:
    raw=(ROOT/'kod'/filename).read_bytes()
    try: code=raw.decode('utf-8-sig')
    except UnicodeDecodeError: code=raw.decode('cp1250')
    lines=code.splitlines()
    wrapped=[]
    for n,line in enumerate(lines,1):
        pieces=textwrap.wrap(line,width=91,replace_whitespace=False,drop_whitespace=False) or ['']
        wrapped.extend([f'{n:3}  '+pieces[0]]+['     '+piece for piece in pieces[1:]])
    for start in range(0,len(wrapped),65):
        page('Listing: '+filename+(' (ciąg dalszy)' if start else ''))
        if start==0 and filename=='GS.m':
            p('Autor: Andrzej Karbowski. Kod źródłowy przekazany przez użytkownika; zachowano oryginalną implementację.','SmallPL')
        snippet='\n'.join(wrapped[start:start+65])
        story.append(Preformatted(snippet,styles['CodePL']))
        source.append('<pre>'+html.escape(snippet)+'</pre>')

def footer(canvas,doc):
    canvas.saveState(); canvas.setStrokeColor(colors.HexColor('#b8cbd9'))
    canvas.line(45,37,A4[0]-45,37)
    canvas.setFont('Arial',8); canvas.setFillColor(colors.HexColor('#506779'))
    canvas.drawString(45,24,'MNUM | Projekt 1.8 | LDLᵀ, Gauss-Seidel, MNK')
    canvas.drawRightString(A4[0]-45,24,str(doc.page)); canvas.restoreState()
doc=SimpleDocTemplate(str(ROOT/'Sprawozdanie_MNUM_P1_8.pdf'),pagesize=A4,
                      rightMargin=45,leftMargin=45,topMargin=42,bottomMargin=49,
                      title='MNUM - Projekt 1.8: LDLT, Gauss-Seidel, MNK',author='Opracowanie projektu MNUM 1.8')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
css='body{font:16px/1.6 Arial;max-width:1000px;margin:40px auto;color:#182d3e} .HeadPL{font-size:28px;font-weight:bold}.SubPL{font-weight:bold}.EqPL{font:20px/1.7 Cambria,serif;background:#f1f5f8;padding:10px}.SmallPL{font-size:13px}td{padding:9px;border-bottom:1px solid #ccd6df}pre{font:12px/1.5 Consolas;background:#f5f5f5;padding:20px;white-space:pre-wrap}.page{break-before:page;border-top:1px solid #ccd6df;margin-top:45px}'
(ROOT/'Sprawozdanie_MNUM_P1_8.html').write_text('<!doctype html><html lang="pl"><meta charset="utf-8"><title>MNUM 1.8</title><style>'+css+'</style>'+''.join(source).replace('<super>','<sup>').replace('</super>','</sup>')+'</html>',encoding='utf-8')
print(ROOT/'Sprawozdanie_MNUM_P1_8.pdf')
