from data_frame_analysis import DataFrameAnalysis
from kalman_filter import KalmanFilter
import pandas as pd
import math
import os
import cv2



def main():

    data_frame_analysis = DataFrameAnalysis()
    file_path = '../../Desktop/testing/NONYOLO/Sinner/bottom_player_coordinates_minimap.xlsx'
    output_filepath = file_path.replace('bottom_player_coordinates_minimap.xlsx', 'output.mp4')
    cap_file_path = file_path.replace('bottom_player_coordinates_minimap.xlsx', 'outputSinner.mp4') #file_path


    #Se il file path non è valido il programma termina
    if not os.path.exists(file_path):
        print("File path non esistente. Inserire un file path valido.\n")
        return


    # leggo il file
    df = pd.read_excel(file_path)
    # df_modified e df_kalman serviranno dopo quando lavoreremo con la funzione clean_file e l'applicazione del filtro di Kalman
    df_modified = None
    df_kalman = None
    #booleani che mi servono per capire se esistono o meno i file cleaned e filtered
    bool_cleaned = True
    bool_kalman = True
    #i nuovi path serviranno dopo quando lavoreremo con la funzione clean_file e l'applicazione del filtro di Kalman per la creazione dei nuovi file
    modified_file_path = None
    kalman_filtered_file_path = None




    #se non esiste già il file cleaned allora bool_cleaned = false altrimenti se esiste inizializzo il "modified_file_path" contenente il file cleaned
    if not os.path.exists(file_path.replace('bottom_player_coordinates_minimap.xlsx', 'bottom_player_coordinates_minimap_cleaned.xlsx')):
        bool_cleaned = False
    else:
        modified_file_path = file_path.replace('bottom_player_coordinates_minimap.xlsx', 'bottom_player_coordinates_minimap_cleaned.xlsx')
        df_modified = pd.read_excel(modified_file_path)
        #se esiste il file cleaned allora pongo il df di partenza = df_modified che mi servirà poi per il calcolo dello spostamento non filtrato
        df = df_modified
    # se non esiste il file filtrato con kalman allora bool_kalman = false altrimenti se esiste inizializzo il "kalman_filtered_file_path" con il file filtrato
    if not os.path.exists(file_path.replace('bottom_player_coordinates_minimap.xlsx','bottom_player_coordinates_minimap_Kalman_filtered.xlsx')):
        bool_kalman = False
    else:
        kalman_filtered_file_path = file_path.replace('bottom_player_coordinates_minimap.xlsx', 'bottom_player_coordinates_minimap_Kalman_filtered.xlsx')
        # df_kalman è il dataframe del file "filtered" mentre "df_modified" è il dataframe del file "cleaned" e "df" è il dataframe iniziale
        df_kalman = pd.read_excel(kalman_filtered_file_path)


    # numero di frames iniziale
    num_rows = df.shape[0]
    #valori del range su cui si vuole lavorare
    starting_frame_value = math.nan
    ending_frame_value = math.nan


    while True:

            #Si seleziona un numero compreso tra 1 e 5 altrimenti stampa un messaggio errore.
            num = int(input("Seleziona un'opzione:\n1. Clean file\n2. Applica filtro di Kalman\n3. Calcola distanza\n4. Calcola velocità\n5. Rimuovi file esistenti\n6. Esci\n"))


            #Se 1 viene selezionato faccio la clean del file su cui si lavora.
            if  num == 1:
                #se esiste il file cleaned allora posso saltare alle operazioni successive
                if bool_cleaned is True:
                    print("File cleaned esistente:\nSelezionare 5 prima di applicare la clean del file")
                else:
                    #pulisco il file da eventuali valori errati e/o nan con le seguenti funzioni
                    data_frame_analysis.select_right_value_excel_file(df, file_path)
                    data_frame_analysis.fill_excel_file_average_values(num_rows, df, file_path)
                    # creo il file_path modificato e salvo
                    modified_file_path = file_path.replace("bottom_player_coordinates_minimap.xlsx","bottom_player_coordinates_minimap_cleaned.xlsx")
                    # Salvo il file con i valori cleaned nel nuovo file_path
                    df.to_excel(modified_file_path, index=False)
                    bool_cleaned = True




            # Se 2 viene selezionato si applica il filtro di kalman
            elif num == 2:
                kalmanf = KalmanFilter()
                #se esiste il file "cleaned" allora posso applicare kalman altrimenti stampa un messaggio di errore
                if bool_cleaned is True:
                    #se esiste il file filtrato con kalman allora evito di fare operazioni inutili.
                    if bool_kalman is True:
                        print("File filtrato con Kalman esistente:\nSelezionare 5 prima di applicare nuovamente Kalman.")
                    else:
                        #genero il file.csv
                        data_frame_analysis.generate_csv(modified_file_path)
                        #Ricorda: df_modified è il dataframe del file "cleaned" mentre df è il dataframe iniziale
                        df_modified = pd.read_excel(modified_file_path)
                        # applico kalman al file cleaned
                        kalmanf.kalman(df_modified, 'player_coordinates_minimap.csv', True)
                        # creo un ulteriore file_path modificato dal filtro di kalman
                        kalman_filtered_file_path = modified_file_path.replace("bottom_player_coordinates_minimap_cleaned.xlsx","bottom_player_coordinates_minimap_Kalman_filtered.xlsx")
                        # Salvo il file con i valori filtrati nel nuovo file_path
                        df_modified.to_excel(kalman_filtered_file_path, index=False)
                        bool_kalman = True
                        # df_kalman è il dataframe del file "filtered" mentre "df_modified" è il dataframe del file "cleaned" e "df" è il dataframe iniziale
                        df_kalman = pd.read_excel(kalman_filtered_file_path)
                else:
                    print("Errore: Effettuare la clean del file prima di generare il file csv.")





            # se 3 viene selezionato calcolo lo spostamento su un dato range
            elif num == 3:
                #Se esiste il file filtrato con Kalman allora calcolo lo spostamento altrimenti stampa un messaggio di errore
                if bool_kalman is True:
                    # aggiorno il valore del numero di righe del dataframe.
                    num_rows_kalman = df_kalman.shape[0]
                    # starting_frame_value ed ending_frame_value sono i valori del range su cui si calcolerà lo spostamento.
                    starting_frame_value, ending_frame_value = data_frame_analysis.check_input(num_rows_kalman)
                    displacement = data_frame_analysis.calculate_displacement(starting_frame_value, ending_frame_value, df)
                    print(f"Distanza non filtrata con Kalman: {round(displacement, 2)} metri")
                    displacement = data_frame_analysis.calculate_displacement(starting_frame_value, ending_frame_value, df_kalman)
                    print(f"Distanza senza fattore di correzione: {round(displacement, 2)} metri")
                    displacement = data_frame_analysis.calculate_displacement_corr(starting_frame_value, ending_frame_value, df_kalman)
                    print(f"Distanza con fattore di correzione: {round(abs(displacement), 2)} metri")


                else:
                    print("Errore: effettuare la clean del file e applicare il filtro di Kalman prima di proseguire con il calcolo dello spostamento.")


            # se 4 viene selezionato calcola la velocità e genera il video in output
            elif num == 4:
                df_speed = None
                df_speed_x = None
                df_speed_y = None
                if bool_kalman is True:
                    # Carica il video
                    cap = cv2.VideoCapture(cap_file_path)
                    if not cap.isOpened():
                       print("Errore nell'aprire il video.")
                    else:
                        #se esiste già un video allora lo rimuovo per poi salvare quello nuovo
                        if os.path.exists(output_filepath):
                            os.remove(output_filepath)

                        k = 15
                        w = 1

                        # calcolo le coordinate (e salvo in un dataframe) della velocità totale
                        df_speed = data_frame_analysis.calculate_speed(k, w, df_kalman, cap)
                        # velocità in x
                        df_speed_x = data_frame_analysis.calculate_speed_x(k, w, df_kalman, cap)
                        # velocità in y
                        df_speed_y = data_frame_analysis.calculate_speed_y(k, w, df_kalman, cap)

                        if df_speed is None:
                            break

                        # Si generano i file excel associati ai dataframe corrispondenti e si applica il filtro di Kalman
                        df_speed.to_excel('speed_coordinates.xlsx', index=False)
                        data_frame_analysis.generate_csv('speed_coordinates.xlsx')
                        kalman = KalmanFilter()
                        kalman.kalman(df_speed, 'player_coordinates_minimap.csv', False)
                        df_speed.to_excel('speed_coordinates_filtered.xlsx', index=False)

                        df_speed_x.to_excel('speed_x_coordinates.xlsx', index=False)
                        data_frame_analysis.generate_csv('speed_x_coordinates.xlsx')
                        kalman.kalman(df_speed_x, 'player_coordinates_minimap.csv', False)
                        df_speed_x.to_excel('speed_x_coordinates_filtered.xlsx', index=False)

                        df_speed_y.to_excel('speed_y_coordinates.xlsx', index=False)
                        data_frame_analysis.generate_csv('speed_y_coordinates.xlsx')
                        kalman.kalman(df_speed_y, 'player_coordinates_minimap.csv', False)
                        df_speed_y.to_excel('speed_y_coordinates_filtered.xlsx', index=False)

                        """
                        # CALCOLO ATAN
                        
                        strings = []
                        t_x = 0
                        res = 0
                        for i in range(len(df_speed_x)):
                            # prende le coordinate di v_x al tempo t
                            coordinates_x = df_speed_x.loc[i, 'x,y']
                            # prende le coordinate di v_y al tempo t
                            coordinates_y = df_speed_y.loc[i, 'x,y']
                            # frame_count è il numero del frame all'iterazione i
                            frame_count = df_speed_x.loc[i, 'Frame']
                            # prende a uno a uno le coordinate t_x e v_x
                            t_x, v_x = ast.literal_eval(coordinates_x)
                            # prende a uno a uno le coordinate t_y e v_y (t_x e t_y sono uguali)
                            t_y, v_y = ast.literal_eval(coordinates_y)
                            # aggiungo un valore "epsilon" = 0.0001 e moltiplico per il segno in modo tale da non avere mai v_x = 0
                            v_x = (abs(v_x) + 0.0001) * (np.sign(v_x))
                            res = math.atan(v_y / v_x)
                            strings.append([frame_count, f"{t_x}, {res}"])
                        df_atan = pd.DataFrame(strings, columns=['Frame', 'x,y'])
                        df_atan.to_excel('speed_atan_coordinates.xlsx', index=False)
                        kalman.kalman(df_atan, 'player_coordinates_minimap.csv', False)
                        df_atan.to_excel('speed_atan_coordinates_filtered.xlsx', index=False)
                        """

                        #Stampa i valori della velocità a video con il dataframe aggiornato (meglio utilizzare il df_speed generale o il df_speed_x e y?)
                        data_frame_analysis.print_speed_into_the_video(k, w, df_speed, cap, output_filepath)
                else:
                    print("Errore: effettuare la clean del file e applicare il filtro di Kalman prima di proseguire con il calcolo dello spostamento.")





            #se 5 viene selezionato allora elimina il file excel cleaned e/o il file excel filtrato con kalman
            elif num == 5:
                if bool_cleaned is True:
                    os.remove(modified_file_path)
                    print("File cleaned rimosso")
                    bool_cleaned = False
                else:
                    print("File cleaned non esistente")


                if bool_kalman is True:
                    os.remove(kalman_filtered_file_path)
                    print("File filtered rimosso")
                    bool_kalman = False
                else:
                    print("File filtered non esistente")




            # se 6 viene selezionato allora esco dal loop (e quindi anche dal programma)
            elif num == 6:
                break
            else:
                print("Errore: il valore deve essere compreso tra 1 e 6")



main()