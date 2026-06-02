# This is a sample Python script.

import numpy as np
from matplotlib import pyplot as plt



np.set_printoptions(threshold=3)
np.set_printoptions(suppress=True)
from numpy import genfromtxt


# Notation used coming from: https://www.bzarg.com/p/how-a-kalman-filter-works-in-pictures/

class KalmanFilter():


    def prediction(self, X_hat_t_1, P_t_1, F_t, B_t, U_t, Q_t):
        X_hat_t = F_t.dot(X_hat_t_1) + (B_t.dot(U_t).reshape(B_t.shape[0], -1))
        P_t = np.diag(np.diag(F_t.dot(P_t_1).dot(F_t.transpose()))) + Q_t
        return X_hat_t, P_t


    def update(self, X_hat_t, P_t, Z_t, R_t, H_t):
        K_prime = P_t.dot(H_t.transpose()).dot(np.linalg.inv(H_t.dot(P_t).dot(H_t.transpose()) + R_t))
        print("K:\n", K_prime)

        X_t = X_hat_t + K_prime.dot(Z_t - H_t.dot(X_hat_t))
        P_t = P_t - K_prime.dot(H_t).dot(P_t)

        return X_t, P_t


    #Il booleano b serve per capire se serve invertire gli assi o meno e per distinguere se viene utilizzato dalla funzione velocità o dalla funzione spostamento
    def kalman(self, df, csv_file, b):
        output_x = []
        output_y = []
        acceleration = 0
        delta_t = 1/1000  # millisecond

        #groundTruth = genfromtxt('data/groundTruth.csv', delimiter=',', skip_header=1)

        # Observations: position_X, position_Y
        measurments = genfromtxt(csv_file, delimiter=',', skip_header=1)


        print(len(measurments))


        #reduced_measurements = rdp (measurments, epsilon=1e-4)

       # measurments = reduced_measurements
        print(len(measurments))
        #TEST PER VISUALIZZARE DATI NON FILTRATI

        for i in range(measurments.shape[0]):
            print(measurments[i][0])
            output_x.append(float(measurments[i][0]))
            output_y.append(float(measurments[i][1]))

        if b is True:
            plt.gca().invert_yaxis()
            plt.plot(output_x,output_y)
            plt.scatter(output_x,output_y)
            plt.xlabel("x")
            plt.ylabel("y")
            plt.title("Grafico dello spostamento non filtrato con Kalman")
            plt.grid()
            plt.show()
        elif b is False:
            plt.plot(output_x, output_y)
            plt.scatter(output_x, output_y)
            plt.xlabel("time")
            plt.ylabel("speed")
            plt.title("Grafico della velocità non filtrato con Kalman")
            plt.grid()
            plt.show()


        # Checking our result with OpenCV
        #opencvKalmanOutput = genfromtxt('data/kalmanv.csv', delimiter=',', skip_header=1)

        # Transition matrix
        F_t = np.array([[1, 0, delta_t, 0], [0, 1, 0, delta_t], [0, 0, 1, 0], [0, 0, 0, 1]])

        # Initial State cov
        P_t = np.identity(4) * 0.2

        # Process cov
        Q_t = np.identity(4)

        # Control matrix
        B_t = np.array([[0], [0], [0], [0]])

        # Control vector
        U_t = acceleration

        # Measurment Matrix
        H_t = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])

        # Measurment cov
        R_t = np.identity(2) * 5

        # Initial State
        X_hat_t = np.array([[0], [0], [0], [0]])
        print("X_hat_t", X_hat_t.shape)
        print("P_t", P_t.shape)
        print("F_t", F_t.shape)
        print("B_t", B_t.shape)
        print("Q_t", Q_t.shape)
        print("R_t", R_t.shape)
        print("H_t", H_t.shape)

        output_x.clear()
        output_y.clear()
        for i in range(measurments.shape[0]):
            X_hat_t, P_hat_t = self.prediction(X_hat_t, P_t, F_t, B_t, U_t, Q_t)
            print("Prediction:")
            print("X_hat_t:\n", X_hat_t, "\nP_t:\n", P_t)

            Z_t = measurments[i].transpose()
            Z_t = Z_t.reshape(Z_t.shape[0], -1)

            print(Z_t.shape)

            X_t, P_t = self.update(X_hat_t, P_hat_t, Z_t, R_t, H_t)
            print("Update:")
            print("X_t:\n", X_t, "\nP_t:\n", P_t)

            #offset_X = abs(X_hat_t[0] - X_t[0])
            #offset_Y = abs(X_hat_t[1] - X_t[1])


            X_hat_t = X_t
            P_hat_t = P_t

            print("Iteration: ",measurments.shape[0])
            output_x.append(float(X_hat_t[0]))
            output_y.append(float(X_hat_t[1]))

        del output_y[0:9]
        del output_x[0:9]

        prev_item_X = output_x[0]
        prev_item_Y = output_y[0]

        count = 0
        max_count = len(output_x)
        threshold = 1

        x_value = 0
        y_value = 0
        print(len(output_x))
        if b is True:
            plt.gca().invert_yaxis() #Inverto l'asse y (nella reference del video di output l'origine degli assi non è standard ma si trova nell'angolo in alto a sinistra)
            for i in range(len(output_x)):
                # Punti da visualizzare
                #plt.plot(output_x[:i+1], output_y[:i+1])  # Collega i punti fino a quello corrente
                #plt.scatter(output_x[:i+1], output_y[:i+1])  # Aggiungi i punti fino a quello corrente
                x_value = (int)(output_x[i])
                y_value = (int)(output_y[i])
                df.loc[i, 'x,y'] = f"{x_value}, {y_value}"
                #plt.draw()  # Aggiorna il grafico
                plt.pause(0.0001)  # Aggiungi un piccolo ritardo per aggiornare il grafico (0.1 secondi)


            # Mostra il grafico finale
            plt.plot(output_x, output_y)
            plt.scatter(output_x, output_y)
            plt.xlabel("x")
            plt.ylabel("y")
            plt.title("Grafico dello spostamento filtrato con Kalman")
            plt.grid()
            plt.show()

        elif b is False:
            for i in range(len(output_x)):
                # Punti da visualizzare
                #plt.plot(output_x[:i+1], output_y[:i+1])  # Collega i punti fino a quello corrente
                #plt.scatter(output_x[:i+1], output_y[:i+1])  # Aggiungi i punti fino a quello corrente
                x_value = output_x[i]
                y_value = output_y[i]
                df.loc[i, 'x,y'] = f"{x_value}, {y_value}"
                #plt.draw()  # Aggiorna il grafico
                plt.pause(0.0001)  # Aggiungi un piccolo ritardo per aggiornare il grafico (0.1 secondi)


            # Mostra il grafico finale
            plt.plot(output_x, output_y)
            plt.scatter(output_x, output_y)
            plt.xlabel("time")
            plt.ylabel("speed")
            plt.title("Grafico della velocità filtrato con Kalman")
            plt.grid()
            plt.show()

