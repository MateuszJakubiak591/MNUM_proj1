function [a, e2, einf, info] = poly_lsq(x, y, p, metoda, skala)
%POLY_LSQ Uniwersalna aproksymacja wielomianem stopnia p.
% metoda: 'normal' -> rownania normalne i wlasny LDLT;
%         'qr'     -> ekonomiczny qr(V,0) i wlasne podstawianie.
% skala=false (domyslnie): baza 1,x,...,x^p;
% skala=true: t=(x-mu)/s, lepsze uwarunkowanie bazy.
% a jest ZAWSZE wektorem [a_p;...;a_0] w oryginalnej zmiennej x.
% polyval(a,x) daje wartosci; e2 i einf liczone w wezlach pomiarowych.
% info.c - wspolczynniki w zmiennej t; info.mu i info.s - przeskalowanie.
% info.epsilon_normal - reszta ukladu normalnego (nie blad aproksymacji).
if nargin < 5, skala = false; end
x = x(:); y = y(:);
m = numel(x);
if numel(y) ~= m || p < 0 || p ~= fix(p) || p >= m
    error('poly_lsq:dane', 'Wymagane: tyle samo x,y oraz 0<=p<liczba probek.');
end
mu = 0; s = 1;
if skala
    mu = (min(x)+max(x))/2;
    s = max(abs(x-mu));
    if s == 0, s = 1; end
end
t = (x-mu)/s;

% Macierz V (oznaczenie A z wykladu 03), kolejnosc dla polyval.
V = ones(m, p+1);
for j = p:-1:1
    V(:,j) = t .* V(:,j+1);
end
epsilon_normal = NaN;
switch lower(metoda)
    case 'normal'
        G = V.'*V;
        h = V.'*y;
        [c, epsilon_normal] = ldlt_solve(G, h);
    case 'qr'
        [Q, R] = qr(V, 0);
        c = back_substitution(R, Q.'*y);
    otherwise
        error('poly_lsq:metoda', 'Metoda musi byc normal albo qr.');
end

% Przejscie c(t) -> a(x) przez schemat Hornera i skladanie wielomianow.
a = c(1);
for j = 2:p+1
    a = conv(a(:).', [1/s, -mu/s]);
    a(end) = a(end) + c(j);
end
a = a(:);
r = polyval(a, x) - y;
e2 = norm(r, 2);
einf = norm(r, inf);
info = struct('c',c,'mu',mu,'s',s,'epsilon_normal',epsilon_normal);
end
