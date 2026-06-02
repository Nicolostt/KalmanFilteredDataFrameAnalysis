# Computer Vision for Human Activity Recognition for Professional Sports
## Computer Vision | CNR Pisa | 2024

### Context
The project focused on the development of computer vision algorithms for analyzing the movement of a tennis player during matches. I starded from an existing project "Tennis Project" by Sergey Kosolapov where he used Object Detection to recognize/detect the players, the ball and the tennis court during a tennis match with a Faster R-CNN. The extracted coordinates are then projected onto a reproduction of the top of the playing rectangle, using a homographic matrix, a fundamental element for the correct calculation of spatial metrics.

### My contribution
I contributed to the design and implementation of solutions for the automatic calculation of metrics such as player displacement and speed, using video sequences as input. Extracting the coordinates frame by frame from the minimap, I started to develop some functions that cleaned up duplicate, noisy, and missing data were found to have several anomalies in the original design that prevented the calculation of correct displacement and velocity, for example:
- for the same frame, both the player and external bodies (often the ball boy) were recognized;
- no player was recognized, so there were no coordinates for that frame (NaN).
This was resolved by first approximating the player's motion using the previous and subsequent coordinates, and only then implementing the Kalman filter to clean up the noisy data. 
After that, the functions that calculate the displacement, the velocity and the printing of the velocity values ​​on the screen were implemented.

### Tecnologies

Python, OpenCV, PyTorch, Numpy.
The PC configuration is as follows:
- NVIDIA GeForce RTX 4060 graphics card (8 GB VRAM);
- 64 GB RAM;
- Intel Core i7-9700F processor.

### Results
Thanks to this contribution, the system is no longer limited to visually representing in game actions, it now includes an initial module capable of providing quantitative parameters to support coaches and technical staff in evaluating athletes performance.
