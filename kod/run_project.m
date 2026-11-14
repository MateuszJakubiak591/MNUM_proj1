function results = run_project
%RUN_PROJECT Wszystkie eksperymenty projektu MNUM 1.8.
% Uruchom: cd do folderu kod, nastepnie results=run_project.
% Solwery nie rysuja i nie wypisuja. Wszystkie wyniki trafiaja do ../wyniki.
root = fileparts(fileparts(mfilename('fullpath')));
out = fullfile(root,'wyniki');
if ~exist(out,'dir'), mkdir(out); end
oldVisibility = get(groot,'defaultFigureVisible');
cleanup = onCleanup(@() set(groot,'defaultFigureVisible',oldVisibility));
set(groot,'defaultFigureVisible','off');
test_solvers;
ns = [50;100;250;500;1000;1500;2000];
repeats = 3;
delta = 1e-9;
results.meta = struct('matlab',version,'computer',computer, ...
    'timestamp',char(datetime('now','Format','yyyy-MM-dd HH:mm:ss')), ...
    'eps',eps,'repeats',repeats,'delta',delta, ...
    'timing','Median of external tic/toc; includes residual; excludes data and plots');

% Rozgrzewka JIT i bibliotek poza pomiarami.
ldlt_solve([4,1;1,3],[1;2]);
GS([4,1;1,3],[1;2],delta,2000);
T1 = zeros(numel(ns),4);
T2 = zeros(numel(ns),8);
for q = 1:numel(ns)
    n = ns(q); i = (1:n).';

    % Punkt 1: macierz pelna, czas zawiera faktoryzacje i reszte.
    A = 2*(i+i.')+1;
    A(1:n+1:end) = 4*n^2+(2*i+4)*n;
    b = 2.5+0.6*i;
    elapsed = zeros(repeats,1);
    for rep = 1:repeats
        t = tic;
        [x,epsilon] = ldlt_solve(A,b);
        elapsed(rep) = toc(t);
    end
    T1(q,:) = [n,median(elapsed),epsilon,epsilon/norm(b)];

    % Punkt 2: obydwa solwery otrzymuja identyczne macierze PELNE.
    % Pozwala porownac algorytmy bez zmiany reprezentacji danych.
    A = 24.5*eye(n)+diag(-5*ones(n-3,1),3)+diag(-5*ones(n-3,1),-3);
    b = -6+0.5*i;
    td = zeros(repeats,1); tg = td; tgInternal = td;
    for rep = 1:repeats
        t = tic;
        [xd,ed] = ldlt_solve(A,b);
        td(rep) = toc(t);
        t = tic;
        [xg,k,tgInternal(rep)] = GS(A,b,delta,1000*n);
        eg = norm(A*xg-b,2);
        tg(rep) = toc(t);
    end
    T2(q,:) = [n,median(td),ed,median(tg),eg,k, ...
        median(tgInternal),norm(xd-xg,2)];
    fprintf('n=%4d: LDLT(1) %.3fs; LDLT(2) %.3fs; GS %.3fs, k=%d\n', ...
        n,T1(q,2),T2(q,2),T2(q,4),k);
end
results.task1 = array2table(T1,'VariableNames', ...
    {'n','time_ldlt_s','residual_2','relative_residual_2'});
results.task2 = array2table(T2,'VariableNames', ...
    {'n','time_ldlt_s','residual_ldlt_2','time_gs_s','residual_gs_2', ...
    'iterations_gs','time_gs_internal_s','difference_solutions_2'});
writetable(results.task1,fullfile(out,'zadanie1.csv'));
writetable(results.task2,fullfile(out,'zadanie2.csv'));

% Wykresy zadania 1.
f = figure('Position',[100,100,1100,450]);
tiledlayout(1,2);
nexttile; loglog(ns,T1(:,2),'-o','LineWidth',1.5); grid on;
xlabel('Liczba rownan n'); ylabel('Czas [s]'); title('Zadanie 1: LDL^T');
nexttile; loglog(ns,T1(:,3),'-o','LineWidth',1.5); grid on;
xlabel('Liczba rownan n'); ylabel('||Ax-b||_2'); title('Reszta ukladu');
saveplot(f,out,'zadanie1');

% Wykresy zadania 2, w tym liczba iteracji GS.
f = figure('Position',[100,100,1400,430]); tiledlayout(1,3);
nexttile; loglog(ns,T2(:,2),'-o',ns,T2(:,4),'-s','LineWidth',1.5);
grid on; xlabel('n'); ylabel('Czas [s]'); legend('LDL^T','GS','Location','best');
title('Zadanie 2: czasy');
nexttile; loglog(ns,T2(:,3),'-o',ns,T2(:,5),'-s','LineWidth',1.5);
grid on; xlabel('n'); ylabel('||Ax-b||_2'); legend('LDL^T','GS','Location','best');
title('Reszty ukladu');
nexttile; plot(ns,T2(:,6),'-o','LineWidth',1.5); grid on;
xlabel('n'); ylabel('Liczba pelnych iteracji'); title('Gauss-Seidel');
saveplot(f,out,'zadanie2');

% Punkt 3: dane i wszystkie wymagane stopnie.
x = (-10:2:10).';
y = [-5.460;-3.880;-1.969;-1.666;-0.076;-0.397;-1.030; ...
    -4.548;-11.528;-21.641;-34.445];
degrees = [3;5;7;9;10];
xx = linspace(min(x),max(x),1001).'; % krok 0.02 zamiast 2: 100x gesciej
approxRepeats = 201;
T3 = zeros(10,10); coefficients = cell(10,2);
for scaled = [false,true]
    f = figure('Position',[100,100,1300,750]); tiledlayout(2,3);
    for q = 1:numel(degrees)
        p = degrees(q); row = q+5*scaled;
        for method = {'normal','qr'}
            poly_lsq(x,y,p,method{1},scaled); % rozgrzewka
        end
        tn = zeros(approxRepeats,1); tq = tn;
        for rep = 1:approxRepeats
            % Naprzemienna kolejnosc zmniejsza systematyczny wplyw kolejnosci.
            if mod(rep,2)
                t=tic; [an,en2,eni]=poly_lsq(x,y,p,'normal',scaled); tn(rep)=toc(t);
                t=tic; [aq,eq2,eqi]=poly_lsq(x,y,p,'qr',scaled); tq(rep)=toc(t);
            else
                t=tic; [aq,eq2,eqi]=poly_lsq(x,y,p,'qr',scaled); tq(rep)=toc(t);
                t=tic; [an,en2,eni]=poly_lsq(x,y,p,'normal',scaled); tn(rep)=toc(t);
            end
        end
        tnodes=x;
        if scaled, tnodes=x/10; end
        V = tnodes .^ (p:-1:0);
        T3(row,:)=[p,scaled,median(tn),en2,eni,median(tq),eq2,eqi, ...
            cond(V,2),cond(V.'*V,2)];
        coefficients(row,:)={an,aq};
        nexttile; plot(x,y,'ko','MarkerFaceColor','k'); hold on;
        plot(xx,polyval(an,xx),'-',xx,polyval(aq,xx),'--','LineWidth',1.3);
        grid on; xlabel('x'); ylabel('y'); title(sprintf('Stopien %d',p));
        legend('Dane','Normalne + LDL^T','QR','Location','best');
    end
    nexttile; axis off;
    text(0,0.8,sprintf('Skalowanie: %d\n11 probek danych\n1001 punktow krzywych',scaled));
    saveplot(f,out,sprintf('zadanie3_skala%d',scaled));
end
results.task3=array2table(T3,'VariableNames',{'degree','scaled','time_normal_s', ...
    'error_normal_2','error_normal_inf','time_qr_s','error_qr_2','error_qr_inf', ...
    'cond_V_2','cond_gram_computed_2'});
results.coefficients=coefficients;
results.x_data=x; results.y_data=y;
results.meta.approx_repeats=approxRepeats;
writetable(results.task3,fullfile(out,'zadanie3.csv'));
fid=fopen(fullfile(out,'wspolczynniki.txt'),'w','n','UTF-8');
for row=1:10
    fprintf(fid,'p=%d, skala=%d; [a_p,...,a_0] w zmiennej x\n',T3(row,1:2));
    fprintf(fid,'normal: '); fprintf(fid,'%.17g ',coefficients{row,1}); fprintf(fid,'\n');
    fprintf(fid,'qr:     '); fprintf(fid,'%.17g ',coefficients{row,2}); fprintf(fid,'\n\n');
end
fclose(fid);
% Dodatkowe wykresy bledow i czasow MNK dla obu baz.
f=figure('Position',[100,100,1100,800]); tiledlayout(2,2);
for scaled=[false,true]
    rows=(1:5)+5*scaled;
    nexttile; semilogy(degrees,T3(rows,4),'-o',degrees,T3(rows,7),'--s');
    grid on; xlabel('Stopien p'); ylabel('||r||_2');
    legend('Normalne + LDL^T','QR','Location','best'); title(sprintf('Bledy, skala=%d',scaled));
    nexttile; plot(degrees,1e6*T3(rows,3),'-o',degrees,1e6*T3(rows,6),'--s');
    grid on; xlabel('Stopien p'); ylabel('Czas [us]');
    legend('Normalne + LDL^T','QR','Location','best'); title(sprintf('Czasy, skala=%d',scaled));
end
saveplot(f,out,'zadanie3_bledy_czasy');
save(fullfile(out,'wyniki.mat'),'results');
fid=fopen(fullfile(out,'wyniki.json'),'w','n','UTF-8');
json=struct('meta',results.meta,'task1',table2struct(results.task1), ...
    'task2',table2struct(results.task2),'task3',table2struct(results.task3), ...
    'coefficients',{coefficients});
fprintf(fid,'%s',jsonencode(json,'PrettyPrint',true)); fclose(fid);
disp(results.task1); disp(results.task2); disp(results.task3);
fprintf('Gotowe. Wyniki zapisano w: %s\n',out);
end

function saveplot(f,out,name)
exportgraphics(f,fullfile(out,[name,'.png']),'Resolution',180);
close(f);
end
