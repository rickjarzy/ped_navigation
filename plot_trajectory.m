%%  Paul Arzberger
%   Plot the computed Trajectory
clear all;
clc;
data_normal = importdata('trajektory_min_peaks_all_sensors_filtered_dyn_step_normal.txt')
data_stairs = importdata('trajektory_min_peaks_all_sensors_filtered_dyn_step_stairs.txt')

phi_start = 47.06427;
lam_start = 15.43513;

% Plot
figure;
hold on;
plot(data_normal(:,2),data_normal(:,1),'k');
plot(data_stairs(:,2), data_stairs(:,1), 'g');
scatter(data_normal(1,2),data_normal(1,1), 'g*');
scatter(data_normal(end,2),data_normal(end,1), 'c*');
xlabel('\lambda [°]');
ylabel('\phi [°]');
legend('Trajectory','Stairs', 'Start', 'End')
plot_google_map_15('APIKey','AIzaSyCyJuOW-15fzA0HWpu4lceIihrfJsVgZvY');

%% Fin - Programm ENDE
fclose('all');