function test_solvers
%TEST_SOLVERS Sprawdzenie niezalezne od benchmarku; gotowy A\b tylko tutaj.
rng(8);
for n = [1, 2, 7, 23]
    B = randn(n);
    A = B*B.' + eye(n);
    b = randn(n,1);
    [x, e, L, d] = ldlt_solve(A,b);
    assert(norm(A-L*diag(d)*L.','fro')/norm(A,'fro') < 1e-13);
    assert(norm(x-A\b)/max(1,norm(x)) < 1e-12);
    assert(e/max(1,norm(b)) < 1e-12);
end
% Macierz symetryczna nieokreslona z niezerowymi pivotami.
A = [2,1;1,-2]; b = [1;3];
x = ldlt_solve(A,b);
assert(norm(A*x-b) < 1e-13);

% Znany wielomian i niesymetryczna dziedzina: sprawdza konwersje skali.
x = linspace(2,8,15).'; a0 = [2;-3;4;-1]; y = polyval(a0,x);
for scaled = [false,true]
    for method = {'normal','qr'}
        [a,e2] = poly_lsq(x,y,3,method{1},scaled);
        assert(norm(a-a0)/norm(a0) < 1e-7);
        assert(e2/norm(y) < 1e-10);
    end
end
% Porownanie z wbudowanym MNK tylko w niezaleznym tescie.
x = (-10:2:10).'; y = sin(x);
for p = [3,5,7,9,10]
    [a,~,~,info] = poly_lsq(x,y,p,'qr',true);
    V = x .^ (p:-1:0);
    aref = V\y;
    assert(norm(polyval(a,x)-polyval(aref,x)) < 1e-7);
    assert(norm(polyval(a,x)-polyval(info.c,(x-info.mu)/info.s)) < 1e-10);
end
fprintf('TESTY: wszystkie sprawdzenia zakonczone poprawnie.\n');
end
