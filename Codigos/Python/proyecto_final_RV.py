import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import time
import serial
import cvzone
import threading
import numpy as np

serialArduino = serial.Serial("COM5", 115200, timeout=1)
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
parametros = cv2.aruco.DetectorParameters_create()
diccionario = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_100)

ang_vel = 0
ang_giro = 0
w_izq = 0
w_der = 0
w_der_A = 0
w_der_B = 0
w_izq_A = 0
w_izq_B = 0
text_1 = "Velocidad izq: % "
text_2 = "Velocidad der: % "
cad = str(w_der + 100) + "," + str(w_izq + 100)
start = False
detector = HandDetector(detectionCon=0.8, maxHands=2)

def func():
    while True:
        time.sleep(1)
        serialArduino.write(cad.encode('ascii'))
        print(cad)


t1 = threading.Thread(target=func)
t1.daemon = True
t1.start()

while True:
    success, img2 = cap.read()
    img = cv2.flip(img2, 1)
    hands, img = detector.findHands(img, flipType=False)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    esquinas, ids, bads = cv2.aruco.detectMarkers(img, diccionario, parameters=parametros)

    if hands:
        if len(hands) == 2:
            hand1 = hands[0]
            lmList1 = hand1['lmList']
            centerPoint1 = hand1["center"]
            bbox1 = hand1['bbox']
            handType1 = hand1["type"]
            fingers1 = detector.fingersUp(hand1)

            hand2 = hands[1]
            lmList2 = hand2["lmList"]
            bbox2 = hand2["bbox"]
            centerPoint2 = hand2["center"]
            handType2 = hand2["type"]
            fingers2 = detector.fingersUp(hand2)

            if hand1["type"] == "Right":
                if sum(fingers1) == 1:
                    start = True
                if start:
                    ang_giro = math.degrees(math.atan2((centerPoint1[0] - 480), 480 - centerPoint1[1]))
                    length1_R, info1_R, img = detector.findDistance(centerPoint1, [480, 480], img)

            if hand2["type"] == "Right":
                if sum(fingers2) == 1:
                    start = True
                if start:
                    ang_giro = math.degrees(math.atan2((centerPoint2[0] - 480), 480 - centerPoint2[1]))
                    length2_R, info2_R, img = detector.findDistance(centerPoint2, [480, 480], img)

            if hand1["type"] == "Left":
                if sum(fingers1) == 1:
                    start = False

                if start:
                    ang_vel = math.degrees(math.atan2((centerPoint1[0]), 240 - centerPoint1[1]) - math.pi / 2)
                    length1_L, info1_L, img = detector.findDistance(centerPoint1, [0, 240], img)

            if hand2["type"] == "Left":
                if sum(fingers2) == 1:
                    start = False
                if start:
                    ang_vel = math.degrees(math.atan2((centerPoint2[0]), 240 - centerPoint2[1]) - math.pi / 2)
                    length2_L, info2_R, img = detector.findDistance(centerPoint2, [0, 240], img)

            if ang_vel > 10:  # retroceder
                if ang_vel > 40:
                    ang_vel = 40
                w_der_A = (ang_vel - 10) * (-2)
                w_izq_A = (ang_vel - 10) * (-2)

            elif ang_vel < -10:  # avanzar
                if ang_vel < -40:
                    ang_vel = -40
                w_der_A = (ang_vel * (-1) - 10) * 2
                w_izq_A = (ang_vel * (-1) - 10) * 2

            else:
                w_izq_A = 0
                w_der_A = 0

            if ang_giro > 10:  # giro derecha
                if ang_giro > 30:
                    ang_giro = 30
                w_der_B = (ang_giro - 10) * 2
                w_izq_B = 0
            elif ang_giro < -10:  # giro izquierda
                if ang_giro < -30:
                    ang_giro = -30
                w_izq_B = (ang_giro * (-1) - 10) * 2
                w_der_B = 0
            else:
                w_izq_B = 0
                w_der_B = 0

            w_izq = int(w_izq_A + w_izq_B)
            w_der = int(w_der_A + w_der_B)

        else:
            w_izq = 0
            w_der = 0

    else:
        w_izq = 0
        w_der = 0

    if np.all(ids != None):
        aruco = cv2.aruco.drawDetectedMarkers(img, esquinas)

        c1 = (esquinas[0][0][0][0], esquinas[0][0][0][1])
        c2 = (esquinas[0][0][1][0], esquinas[0][0][1][1])
        c3 = (esquinas[0][0][2][0], esquinas[0][0][2][1])
        c4 = (esquinas[0][0][3][0], esquinas[0][0][3][1])

        copy = img
        if 1 in ids:
            imagen = cv2.imread("1.jpg")
            start = False
        if 2 in ids:
            imagen = cv2.imread("2.jpg")
            start = True
            w_izq = -30
            w_der = 30

        if 3 in ids:
            imagen = cv2.imread("3.jpg")
            start = True
            w_izq = 30
            w_der = 30

        tamaño = imagen.shape

        puntos_aruco = np.array([c1, c2, c3, c4])

        puntos_imagen = np.array([
            [0, 0],
            [tamaño[1] - 1, 0],
            [tamaño[1] - 1, tamaño[0] - 1],
            [0, tamaño[0] - 1]
        ], dtype=float)

        h, estado = cv2.findHomography(puntos_imagen, puntos_aruco)

        perspectiva = cv2.warpPerspective(imagen, h, (copy.shape[1], copy.shape[0]))
        cv2.fillConvexPoly(copy, puntos_aruco.astype(int), 0, 16)
        img = copy + perspectiva

    elif np.all(ids == None) and (len(hands) != 2):
        start = False

    if w_izq > 100:
        w_izq = 100
    if w_izq < -100:
        w_izq = -100
    if w_der > 100:
        w_der = 100
    if w_der < -100:
        w_der = -100

    w_izq_s = w_izq + 100
    w_der_s = w_der + 100
    cad = str(w_der_s) + "," + str(w_izq_s)

    if start == False:
        cv2.putText(img, "PAUSADO", (220, 240), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)


    cv2.rectangle(img, (0, 480), (250, 427), (0, 0, 0), -1)
    cv2.putText(img, text_1 + str(w_izq), (0, 450), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1)
    cv2.putText(img, text_2 + str(w_der), (0, 470), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
