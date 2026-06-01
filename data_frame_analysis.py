import ast
import pandas as pd
import math
import cv2
import time
import numpy as np




class DataFrameAnalysis :

    #controlla che il range dei valori sia corretto
    def check_input(self, num_rows):

        # Prendo in input il numero del frame iniziale
        while True:
            try:
                starting_frame_value = int(input(f"Inserire il numero del frame di inizio compreso tra 0 e {num_rows-1}: "))
                if 0 <= starting_frame_value <= num_rows-1:
                    break
                else:
                    print(f"Errore: il numero iniziale deve essere compreso tra 0 e {num_rows-1}")
            except ValueError:
                print("Errore: Inserisci un numero valido.")

        # Prendo in input il numero del frame finale
        while True:
            try:
                ending_frame_value = int(input(f"Inserire il numero del frame finale compreso tra {starting_frame_value} e {num_rows-1}: "))
                if starting_frame_value < ending_frame_value <= num_rows-1:
                    break
                else:
                    print(f"Errore: il numero finale deve essere compreso tra {starting_frame_value} e {num_rows-1}")
            except ValueError:
                print("Errore: Inserisci un numero valido.")

        return starting_frame_value, ending_frame_value







    # prende come parametri il df, e il file_path. Ritorna il file_path dove si salveranno i valori cleaned
    def select_right_value_excel_file(self, df, file_path):
        #coordinate (x,y) precedenti, correnti e successive.
        x_prev, x_curr, x_succ = 0, 0, 0
        y_prev, y_curr, y_succ = 0, 0, 0
        #tengo una copia delle ultime coppie di coordinate valide
        last_valid_x = 0
        last_valid_y = 0
        #indice
        i = 0
        # parametri k che mi servono per tenere un margine che il delta non può superare (vedi delta dopo)
        k_x_prev, k_y_prev = 0, 0
        k_x, k_y = 0, 0
        #costante di margine che andremo a sommare al k
        k_corr = 20
        # il valore delta è dato dalla differenza tra le coordinate correnti e quelle precedenti
        delta_x, delta_y = 0, 0
        #counter che incremento quando trovo valori nan
        counter = 1

        while i < len(df):  # Usa len(df) per evitare errori di lunghezza dinamica
            print("Iterazione:")
            print(i)
            print("last_valid_x")
            print(last_valid_x)
            print("last_valid_y")
            print(last_valid_y)
            # se sono alla prima iterazione non inizializzo i valori precedenti poiché non ce ne sono ancora.
            if i > 0:
                # inizializzo le coordinate precedenti
                coordinates_prev = df.loc[i - 1, 'x,y']
                if not pd.isna(coordinates_prev):
                    x_prev, y_prev = ast.literal_eval(coordinates_prev)
                else:
                    x_prev = math.nan
                    y_prev = math.nan


            # inizializzo le coordinate correnti
            coordinates_curr = df.loc[i, 'x,y']
            if not pd.isna(coordinates_curr):
                x_curr, y_curr = ast.literal_eval(coordinates_curr)
            else:
                x_curr = math.nan
                y_curr = math.nan


            # Verifica che i + 1 sia valido prima di accedere
            if i + 1 < len(df):

                # inizializzo le coordinate successive
                coordinates_succ = df.loc[i + 1, 'x,y']
                if pd.isna(coordinates_succ):
                    x_succ, y_succ = math.nan, math.nan
                else:
                    x_succ, y_succ = ast.literal_eval(coordinates_succ)


                #memorizzo il numero del frame corrente e successivo
                frame_curr = df.loc[i, 'Frame']
                frame_succ = df.loc[i + 1, 'Frame']


                # se sono alla prima iterazione il primo valore del delta_x e del delta_y saranno uguali a 0.
                if i == 0:

                    delta_x = 0
                    delta_y = 0

                elif i > 0:
                    print("x_curr")
                    print(x_curr)
                    print("x_prev")
                    print(x_prev)
                    #Se i valori correnti e precedenti non sono nan allora delta = valori correnti - valori precedenti
                    if (not pd.isna(x_curr) and not pd.isna(y_curr)) and (not pd.isna(x_prev) and not pd.isna(y_prev)):
                        print("valori correnti e precedenti validi")
                        delta_x = abs(x_curr - x_prev)
                        print("delta_x")
                        print(delta_x)
                        delta_y = abs(y_curr - y_prev)
                        print("delta_y")
                        print(delta_y)
                        # aggiorno i parametri k_x e k_y
                        k_x = (delta_x + k_x_prev) / 2
                        k_y = (delta_y + k_y_prev) / 2
                        print("k_x_prev")
                        print(k_x_prev)
                        print("k_y_prev")
                        print(k_y_prev)
                        #Se il delta è valido allora memorizzo i valori correnti come gli ultimi valori validi
                        if delta_x <= k_x + k_corr and delta_y <= k_y + k_corr:
                            last_valid_x = x_curr
                            last_valid_y = y_curr
                    #Se i valori correnti non sono nan e i precedenti sono nan allora delta = valori correnti - ultimi valori validi
                    elif (not pd.isna(x_curr) and not pd.isna(y_curr)) and (pd.isna(x_prev) and pd.isna(y_prev)):
                        print("Valori correnti validi, precedenti nan")
                        delta_x = abs(x_curr - last_valid_x)
                        print("delta_x")
                        print(delta_x)
                        delta_y = abs(y_curr - last_valid_y)
                        print("delta_y")
                        print(delta_y)
                        # aggiorno i parametri k_x e k_y
                        k_x = (delta_x + k_x_prev) / 2
                        k_y = (delta_y + k_y_prev) / 2
                        print("k_x_prev")
                        print(k_x_prev)
                        print("k_y_prev")
                        print(k_y_prev)
                        """
                        faccio un check per evitare di aggiornare l'ultimo valore valido con un valore errato
                        Esempio:
                        Frame   coordinates
                        216     534, 3205
                        217     nan, nan
                        218     67, 2064
                        last_valid_x = 67 ma è troppo piccolo rispetto all'ultimo valore valido quindi il delta sarà grande.
                        """
                        if delta_x <= k_x + k_corr and delta_y <= k_y + k_corr:
                            last_valid_x = x_curr
                            last_valid_y = y_curr



                #Se il valore corrente è nan aggiorno il counter e incremento il valore di k_x e k_y
                if pd.isna(x_curr) and pd.isna(y_curr):
                    counter = counter + 1
                    print("Counter")
                    print(counter)
                    k_x = k_x_prev * counter
                    k_y = k_y_prev * counter


                #calcolo il limite superiore dei valori k.
                k_x = math.ceil(k_x)
                k_y = math.ceil(k_y)
                print("k_x arrotondato:")
                print(k_x)
                print("k_y arrotondato:")
                print(k_y)



                if frame_curr == frame_succ:

                    print("FRAME CURR = FRAME SUCC")

                    #se sono alla prima iterazione allora delta_x1 e delta_y1 saranno uguali alle coordinate successive.
                    if i == 0:
                        delta_x1 = 0
                        delta_y1 = 0
                    else:
                        if not pd.isna(x_prev) and not pd.isna(y_prev):
                            delta_x1 = abs(x_succ - x_prev)
                            delta_y1 = abs(y_succ - y_prev)
                        elif pd.isna(x_prev) and pd.isna(y_prev):
                            delta_x1 = abs(x_succ - last_valid_x)
                            delta_y1 = abs(x_succ - last_valid_y)


                    """
                    se il delta (coordinate correnti - coordinate precedenti) è minore di delta' (coordinate successiva - coordinate precedenti)
                    allora scelgo il primo valore eliminando il secondo (o viceversa) e reindicizzo.
                    """
                    if (delta_x < delta_x1 and delta_y < delta_y1) and (delta_x <= k_x + k_corr and delta_y <= k_y + k_corr):
                        print("primo if: Delta<100")
                        # elimino il frame (duplicato) successivo e reindicizzo
                        df.drop(i + 1, inplace=True)
                        df.reset_index(drop=True, inplace=True)  # Reindicizza dopo la rimozione
                        continue
                    elif (delta_x > delta_x1 and delta_y > delta_y1) and (delta_x1 <= k_x + k_corr and delta_y1 <= k_y + k_corr):
                        print("Primo elif")
                        df.drop(i, inplace=True)
                        df.reset_index(drop=True, inplace=True)  # Reindicizza dopo la rimozione
                        continue
                    #altrimenti, se c'è troppa differenza tra due valori consecutivi, inserisco nan e reindicizzo.
                    else:
                        print("ELSE")
                        df.loc[i, 'x,y'] = math.nan
                        df.drop(i + 1, inplace=True)
                        df.reset_index(drop=True, inplace=True)  # Reindicizza dopo la rimozione
                        continue

                #se i due frame consecutivi non sono duplicati allora controllo che non ci sia troppa differenza tra il valore precedente e il valore corrente.
                else:
                 if not pd.isna(x_curr) and not pd.isna(y_curr):
                     if(delta_x > k_x + k_corr or  delta_y > k_y + k_corr):
                        df.loc[i, 'x,y'] = math.nan

            else:
                # Se i + 1 non è valido, esci dal ciclo
                break

            # mi memorizzo i parametri k precedenti per l'iterazione successiva
            k_x_prev = k_x
            k_y_prev = k_y
            # reimposto il counter
            counter = 1

            i += 1



    def fill_excel_file_average_values(self, num_rows, df, file_path):
        b = False  # Booleano per capire se ci sono NaN
        x1, y1 = 0, 0  # Valori iniziali X e Y
        x2, y2 = 0, 0  # Valori finali X e Y
        nan_indices = []  # Lista per memorizzare gli indici con NaN consecutivi

        for i in range(len(df)):

            coordinates_curr = df.loc[i, 'x,y']
            coordinates_succ = df.loc[i + 1, 'x,y'] if i + 1 < len(df) else None

            # Se il valore corrente NON è NaN
            if not pd.isna(coordinates_curr):
                # Aggiorno il valore iniziale
                x1, y1 = ast.literal_eval(coordinates_curr)
                nan_indices = []  # Resetta la lista dei NaN

            # Se il valore corrente È NaN
            elif pd.isna(coordinates_curr):
                b = True  # Segnalo che ci sono NaN
                nan_indices.append(i)  # Aggiungo l'indice del NaN

                # Se il successivo NON è NaN, calcolo gli incrementi
                if not pd.isna(coordinates_succ):
                    x2, y2 = ast.literal_eval(coordinates_succ)
                    counter = len(nan_indices)  # Numero di NaN consecutivi
                    increment_x = (x2 - x1) / (counter + 1)
                    increment_y = (y2 - y1) / (counter + 1)

                    # Riempio progressivamente i valori
                    for idx, nan_idx in enumerate(nan_indices, 1):
                        filled_x = x1 + increment_x * idx
                        filled_y = y1 + increment_y * idx
                        df.loc[nan_idx, 'x,y'] = f"{int(filled_x)}, {int(filled_y)}"

                    nan_indices = []  # Resetta la lista dopo aver riempito

            # Se arrivo alla fine del range e ho ancora valori NaN
            if i == num_rows - 1 and nan_indices:
                for nan_idx in nan_indices:
                    df.loc[nan_idx, 'x,y'] = f"{int(x1)}, {int(y1)}"








    #generazione del file.csv a cui si applica il filtro di Kalman
    def generate_csv(self, file_path):


        # Leggi separatamente l'intestazione
        header = pd.read_excel(file_path, nrows=0).columns
        # Carica i dati specificando skiprows e nrows (il range va da starting_frame_value a ending_frame_value-1)
        df = pd.read_excel(file_path)

        # Assegna l'intestazione corretta
        df.columns = header

        # Verifica che 'x,y' esista
        if 'x,y' not in df.columns:
            raise KeyError("'x,y' non è presente nelle colonne del DataFrame.")

        # Rimuovi parentesi e dividi in 'x' e 'y'
        df[['x', 'y']] = df['x,y'].str.split(',', expand=True)

        # Crea un nuovo DataFrame con 'x' e 'y'
        player_coordinates_minimap = df[['x', 'y']]

        # Salva in CSV
        player_coordinates_minimap.to_csv('player_coordinates_minimap.csv', index=False, header=True)










    #calcola lo spostamento
    def calculate_displacement(self, starting_frame_value, ending_frame_value, df):
        spazio_percorso_pixel = 0
        # Loop dal frame starting_frame_value a ending_frame_value
        for i in range(starting_frame_value, ending_frame_value):
            if i + starting_frame_value < 10:
                continue

            # Prendo i valori x1 e y1 del giocatore a partire nella posizione i
            x1, y1 = ast.literal_eval(df.loc[i, 'x,y'])
            # Prendo i valori x2 e y2 del giocatore nella posizione successiva i + 1
            x2, y2 = ast.literal_eval(df.loc[i + 1, 'x,y'])


            # Calcolo distanza in pixel tra la posizione i e i + 1
            distanza_pixel = math.sqrt((x2-x1)**2 + (y2-y1)**2)


            # Calcolo lo spazio totale percorso.
            spazio_percorso_pixel += distanza_pixel


        #misure campo da tennis in metri
        lunghezza_metri = 23.77

        #misure campo da tennis in pixel
        lunghezza_pixel = 2374

        #Conversione pixel - metri
        conversione_lunghezza = lunghezza_metri/lunghezza_pixel


        # Conversione spazio percorso da pixel in metri
        spazio_percorso_metri = spazio_percorso_pixel * conversione_lunghezza
        return spazio_percorso_metri









    # calcola lo spostamento
    def calculate_displacement_corr(self, starting_frame_value, ending_frame_value, df):  # Devo mettere quella roba dell'offset percorso così come faccio per calculate_displacement_x e y? quindi per vedere il calcolo del segno?

            spazio_percorso_pixel = 0

            average_value_x = 7.9
            real_value_x = 8.23
            fattore_correzione_x = real_value_x / average_value_x

            real_value_y1 = 5.49
            real_value_y2 = 6.4

            avg_y1 = 5.91
            avg_y2 = 9.67

            corr_y1 = real_value_y1 / avg_y1
            corr_y2 = real_value_y2 / avg_y2

            fattore_correzione_y = (corr_y1 + corr_y2) / 2
            offset_percorso_x = 0
            offset_percorso_y = 0

            # Loop dal frame starting_frame_value a ending_frame_value
            for i in range(starting_frame_value, ending_frame_value):
                if i + starting_frame_value < 10:
                    continue

                # Prendo i valori x1 e y1 del giocatore a partire nella posizione i
                x1, y1 = ast.literal_eval(df.loc[i, 'x,y'])
                # Prendo i valori x2 e y2 del giocatore nella posizione successiva i + 1
                x2, y2 = ast.literal_eval(df.loc[i + 1, 'x,y'])

                # Calcolo distanza in pixel tra la posizione i e i + 1
                distanza_pixel = math.sqrt(((x2 - x1)*fattore_correzione_x) ** 2 + ((y2 - y1)*fattore_correzione_y) ** 2)

                offset_percorso_x += (x2-x1)*fattore_correzione_x
                offset_percorso_y += (y2-y1)*fattore_correzione_y

                # Calcolo lo spazio totale percorso.
                spazio_percorso_pixel += distanza_pixel


            if offset_percorso_x < 0 or offset_percorso_y < 0:
                spazio_percorso_pixel = -spazio_percorso_pixel



            # misure campo da tennis in metri
            lunghezza_metri = 23.77

            # misure campo da tennis in pixel
            lunghezza_pixel = 2374

            # Conversione pixel - metri
            conversione_lunghezza = lunghezza_metri / lunghezza_pixel

            # Conversione spazio percorso da pixel in metri
            spazio_percorso_metri = spazio_percorso_pixel * conversione_lunghezza
            return (spazio_percorso_metri)















    # calcola lo spostamento in x
    def calculate_displacement_x(self, starting_frame_value, ending_frame_value, df):

        spazio_percorso_pixel = 0
        offset_percorso = 0
        delta_x = 0
        delta_x1 = 0


        # Loop dal frame starting_frame_value a ending_frame_value
        for i in range(starting_frame_value, ending_frame_value):

            if i + starting_frame_value < 10:
                continue

            # Prendo i valori x1 e y1 del giocatore a partire nella posizione i
            x1, y1 = ast.literal_eval(df.loc[i, 'x,y'])
            # Prendo i valori x2 e y2 del giocatore nella posizione successiva i + 1
            x2, y2 = ast.literal_eval(df.loc[i + 1, 'x,y'])

            delta_x = abs(x2-x1)
            delta_x1 = x2 - x1

            # Calcolo lo spazio totale percorso.
            spazio_percorso_pixel += delta_x
            offset_percorso += delta_x1

        if offset_percorso < 0:
            spazio_percorso_pixel = -spazio_percorso_pixel

        # misura del campo da tennis in metri
        lunghezza_metri = 23.77

        # misura del campo da tennis in pixel
        lunghezza_pixel = 2374

        # Conversione pixel - metri
        conversione_lunghezza = lunghezza_metri / lunghezza_pixel

        # Conversione spazio percorso da pixel in metri
        spazio_percorso_metri = spazio_percorso_pixel * conversione_lunghezza
        return spazio_percorso_metri














    # calcola lo spostamento in y
    def calculate_displacement_y(self, starting_frame_value, ending_frame_value, df):

        spazio_percorso_pixel = 0
        offset_percorso = 0
        delta_y = 0
        delta_y1 = 0


        # Loop dal frame starting_frame_value a ending_frame_value
        for i in range(starting_frame_value, ending_frame_value):

            if i + starting_frame_value < 10:
                continue

            # Prendo i valori x1 e y1 del giocatore a partire nella posizione i
            x1, y1 = ast.literal_eval(df.loc[i, 'x,y'])
            # Prendo i valori x2 e y2 del giocatore nella posizione successiva i + 1
            x2, y2 = ast.literal_eval(df.loc[i + 1, 'x,y'])


            delta_y = abs(y1 - y2)
            delta_y1 = y1 - y2


            # Calcolo lo spazio totale percorso.
            spazio_percorso_pixel += delta_y
            offset_percorso += delta_y1

        if offset_percorso < 0:
            spazio_percorso_pixel = -spazio_percorso_pixel

        # misura del campo da tennis in metri
        lunghezza_metri = 23.77

        # misura del campo da tennis in pixel
        lunghezza_pixel = 2374

        # Conversione pixel - metri
        conversione_lunghezza = lunghezza_metri / lunghezza_pixel

        # Conversione spazio percorso da pixel in metri
        spazio_percorso_metri = spazio_percorso_pixel * conversione_lunghezza
        return spazio_percorso_metri












    """la funzione calcola la velocità del giocatore nel video e genera il video con la velocità del giocatore.
    per calcolare la distanza con la funzione calculate_displacement serve partire dalle coordinate nel dataframe.
    k è il range di frame che si vuole calcolare ad ogni iterazione. w è la finestra di cui sposto il range 
    per esempio per k = 15 e w = 10 avrò 0-14, 10-24, 20-34 ecc.ecc.
    cap è il parametro che passo per leggere i frame da un file video. La funzione calcola prima la velocità.
    """
    def calculate_speed(self, k, w, df, cap):
        if k < w:
            print("Errore: k non può essere minore di w")
            return None
        frame_init = 0
        frame_final =  k - 1
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        #il tempo è uguale al parametro k diviso 30 che è il valore dei fps del video.
        t = (k-1)/fps
        # Numero totale di frame nel video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Riparti dal primo frame
        #cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_count = 0


        strings = []
        while frame_count < total_frames:
            #se frame_final è maggiore della lunghezza del video allora correggo il valore
            if frame_final >= total_frames:
                frame_final = total_frames - 1
            print(f"Range {frame_init} - {frame_final}")
            displacement = self.calculate_displacement_corr(frame_init, frame_final, df)
            speed = displacement / t
            # memorizza il frame "frame_count" e i valori della velocità "speed" al tempo "(t*frame_count)/k"
            strings.append([frame_count, f"{(t*frame_count)/(k-1)}, {speed}"])
            print(f"Velocità in m/s: {speed} m/s")

            for i in range(w):
                frame_count += 1
                if frame_count >= total_frames:
                    break
            # Aggiorna i frame iniziali e finali per il prossimo ciclo
            frame_init = frame_init + w
            frame_final = frame_final + w





        #Salvo i valori dei tempi e delle velocità nel dataframe
        df_speed = pd.DataFrame(strings, columns=['Frame', 'x,y'])
        return df_speed






    def calculate_speed_x(self, k, w, df, cap):
        if k < w:
            print("Errore: k non può essere minore di w")
            return -1
        frame_init = 0
        frame_final =  k - 1
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        print(f"fps : {fps}")
        #il tempo è uguale al parametro k diviso 30 che è il valore dei fps del video.
        t = (k-1)/fps

        # Numero totale di frame nel video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0

        #memorizza il frame "frame_count" e i valori della velocità "speed" al tempo "(t*frame_count)/k"
        strings = []
        while frame_count < total_frames:
            #se frame_final è maggiore della lunghezza del video allora correggo il valore
            if frame_final >= total_frames:
                frame_final = total_frames - 1
            print(f"Range {frame_init} - {frame_final}")
            displacement_x = self.calculate_displacement_x(frame_init, frame_final, df)
            speed_x = displacement_x / t
            strings.append([frame_count, f"{(t*frame_count)/(k-1)}, {speed_x}"])
            print(f"Velocità in m/s: {speed_x} m/s")

            for i in range(w):
                frame_count += 1
                if frame_count >= total_frames:
                    break
            # Aggiorna i frame iniziali e finali per il prossimo ciclo
            frame_init = frame_init + w
            frame_final = frame_final + w


        #Salvo i valori dei tempi e delle velocità nel dataframe
        df_speed_x = pd.DataFrame(strings, columns=['Frame', 'x,y'])
        #self.generate_csv('speed_x_coordinates.xlsx')
        #df_speed_x.to_excel('speed_x_coordinates_filtered.xlsx', index=False)
        return df_speed_x










    def calculate_speed_y(self, k, w, df, cap):
        if k < w:
            print("Errore: k non può essere minore di w")
            return -1
        frame_init = 0
        frame_final =  k - 1
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        #il tempo è uguale al parametro k diviso 30 che è il valore dei fps del video.
        t = (k-1)/fps

        # Numero totale di frame nel video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Riparti dal primo frame
        #cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_count = 0

        #memorizza il frame "frame_count" e i valori della velocità "speed" al tempo "(t*frame_count)/k"
        strings = []
        while frame_count < total_frames:
            #se frame_final è maggiore della lunghezza del video allora correggo il valore
            if frame_final >= total_frames:
                frame_final = total_frames - 1
            print(f"Range {frame_init} - {frame_final}")
            displacement_y = self.calculate_displacement_y(frame_init, frame_final, df)
            speed_y = displacement_y / t
            strings.append([frame_count, f"{(t*frame_count)/(k-1)}, {speed_y}"])
            print(f"Velocità y in m/s: {speed_y} m/s")

            for i in range(w):
                frame_count += 1
                if frame_count >= total_frames:
                    break
            # Aggiorna i frame iniziali e finali per il prossimo ciclo
            frame_init = frame_init + w
            frame_final = frame_final + w


        #Salvo i valori dei tempi e delle velocità nel dataframe
        df_speed_y = pd.DataFrame(strings, columns=['Frame', 'x,y'])
        return df_speed_y














    def print_speed_into_the_video(self, k, w, df, cap, output_filepath): #VEDI SE C'E DA LEVARE LA Y

        fps = int(cap.get(cv2.CAP_PROP_FPS))


        # Ottieni le informazioni sul video (come larghezza e altezza dei frame)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Codifica video per MJPG
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        # Crea l'oggetto VideoWriter per salvare il video
        out = cv2.VideoWriter(output_filepath, fourcc, fps, (frame_width, frame_height))

        # Controlla se il VideoWriter è stato creato correttamente
        if not out.isOpened():
            print("Errore nell'aprire il file video per la scrittura.")
            return

        # Numero totale di frame nel video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Riparti dal primo frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_init = 0
        frame_final = k - 1
        frame_count = 0

        time_t = 0
        time_t_succ = 0

        speed = 0
        speed_succ = 0
        coordinates = None
        coordinates_succ = None
        counter_frame = 0
        counter = 0
        j = 0

        while frame_count < total_frames:
            # se frame_final è maggiore della lunghezza del video allora correggo il valore
            if frame_final >= total_frames:
                frame_final = total_frames - 1

            print(f"frame count = {frame_count}")

            coordinates = df.loc[j, 'x,y']
            time_t, speed = ast.literal_eval(coordinates)


            if frame_count < total_frames-1:
                coordinates_succ = df.loc[j+1, 'x,y']
                time_t_succ, speed_succ = ast.literal_eval(coordinates_succ)

            j += 1

            print(f"speed: {speed}")
            if np.sign(speed) != np.sign(speed_succ):
                text = ('Fermo.')
                counter_frame = 5
                counter = counter + 1
            else:
                if counter_frame > 0:
                    text = ('Fermo.')
                    counter_frame = counter_frame-1
                else:
                    text = f'{abs(speed):.2f} m/s'

            for i in range(w):
                # Leggi il frame corrente dal video

                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count == total_frames-1:
                    # stampo counter - 1 cambi di direzione totali perché all'ultimo frame la velocità è 0
                    # e quindi viene sempre considerato come cambio di direzione
                    text = (f"Cambi di direzione totali: {counter-1}")
                # Aggiungi il testo sul frame
                cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_4)
                # Aggiungi il frame elaborato al video di output
                out.write(frame)

                frame_count += 1
                if frame_count >= total_frames:
                    break

                # Interrompi se premi 'q'
                if cv2.waitKey(33) & 0xFF == ord('q'):
                    break

            # Aggiorna i frame iniziali e finali per il prossimo ciclo
            frame_init = frame_init + w
            frame_final = frame_final + w

        # release the cap object
        cap.release()
        # Rilascia l'oggetto VideoWriter e chiudi le finestre
        out.release()
        time.sleep(1)
        # close all windows
        cv2.destroyAllWindows()