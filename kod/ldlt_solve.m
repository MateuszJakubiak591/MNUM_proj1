function [x, epsilon, L, d] = ldlt_solve(A, b)
%LDLT_SOLVE Rozwiazanie Ax=b przez wlasna faktoryzacje A=L*D*L'.
% A - rzeczywista macierz symetryczna z niezerowymi pivotami LDLT.
% b - wektor prawej strony; x - rozwiazanie kolumnowe.
% epsilon = norm(A*x-b,2); L - dolna trojkatna z jedynkami na diagonali.
% d(i) = d_ii, czyli D=diag(d). Bez testow stosowalnosci i bez pivotingu.
% W szczegolnosci procedura dziala dla macierzy dodatnio okreslonych.
% Nie uzywa ldl, chol, inv, mldivide ani innych gotowych solwerow.
n = size(A, 1);
b = b(:);
L = eye(n);
d = zeros(n, 1);

% Faktoryzacja kolumnowa: wzory ze slajdow 42-43 wykladu 02.
for i = 1:n
    k = 1:i-1;
    v = d(k,1) .* L(i,k).';
    d(i) = A(i,i) - L(i,k)*v;
    if i < n
        L(i+1:n,i) = (A(i+1:n,i) - L(i+1:n,k)*v) / d(i);
    end
end

% Podstawianie w przod: L*y=b, l_ii=1.
y = zeros(n, 1);
for i = 1:n
    y(i) = b(i) - L(i,1:i-1)*y(1:i-1,1);
end

% Uklad diagonalny D*z=y (dzielenie skalarne, nie macierzowe).
z = y ./ d;

% Podstawianie wstecz: L'*x=z, l_ii=1.
x = zeros(n, 1);
for i = n:-1:1
    x(i) = z(i) - L(i+1:n,i).'*x(i+1:n,1);
end
epsilon = norm(A*x-b, 2);
end
