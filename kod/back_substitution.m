function a = back_substitution(R, c)
%BACK_SUBSTITUTION Wlasne podstawianie wstecz dla R*a=c.
% R - nieosobliwa macierz gorna trojkatna, c - wektor kolumnowy.
n = size(R, 1);
a = zeros(n, 1);
for i = n:-1:1
    a(i) = (c(i) - R(i,i+1:n)*a(i+1:n,1)) / R(i,i);
end
end
