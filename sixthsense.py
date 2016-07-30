import cv2
import numpy as np
import math
import os

frame_counter = 0
handCenterPositions_x = [0,0,0,0,0,0,0,0,0,0]
handCenterPositions_y = [0,0,0,0,0,0,0,0,0,0]
paint_x = []
paint_y = []
eraser_x = []
eraser_y = []

val = 0
value = lambda x, y: x / y;
euclid_distance = lambda e0,e1,s0,s1 :math.sqrt((e0 - s0) ** 2 + (e1 - s1) ** 2);


def track_handcentre():
    for i in range(len(handCenterPositions_x)):
      cv2.circle(drawing, (handCenterPositions_x[i], handCenterPositions_y[i]), 5, (255, 25*i, 0), -1)

def draw_paint():
    for i in range(len(paint_x)):
        cv2.circle(painting, (300-paint_x[i], paint_y[i]), 5, (255, 255, 255), -1)
        #the brush point


def ersase():
    for p in range(len(eraser_x)):
        cv2.circle(painting,(eraser_x[p],eraser_y[p]),30 ,(0,0,0), -1)

def click_photo(t,l,cx,cy):

   '''photo_clicked = crop[0:0, :cx:cy]
   if cx > 0 and cy > 0 :
     cv2.imshow("photo", photo_clicked)
   else:
       cv2.putText(img, 'error in size...', (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 4, cv2.LINE_AA)
    '''
def nothing(x):
  pass




video_input = cv2.VideoCapture(0)

video_input.get(10)
previous_defects = 45

track = np.zeros((100,400,3), np.uint8)
cv2.namedWindow('thresh_val')
cv2.createTrackbar('Value','thresh_val',0,255,nothing)
val = 35
while(video_input.isOpened()):
    ret, test = video_input.read()
    crop = test[100:400, 100:400]
    grey = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
    blurr = cv2.GaussianBlur(grey, (35, 35), 0)
    val = cv2.getTrackbarPos('Value', 'thresh_val')
    print val
    ret, thresh = cv2.threshold(blurr,val,255,0)
    cv2.imshow('thresh_val', thresh)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()

while(video_input.isOpened()):


    ret, img = video_input.read()
    cv2.rectangle(img, (400, 400), (100, 100), (255, 0, 255), 3)
    crop = img[100:400,100:400]
    gray = cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(35,35),0)

    ret,thresh1 = cv2.threshold(blur,val,255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    cv2.imshow('Threshold_image', thresh1)

    _,contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_area = -1
    for i in range(len(contours)):
        cnt=contours[i]
        area = cv2.contourArea(cnt)
        if(area>max_area):
            max_area=area
            ci=i
    cnt=contours[ci]
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(crop, (x, y), (x + w, y + h), (0, 0, 255), 0)
    hull = cv2.convexHull(cnt)
    drawing = np.zeros(crop.shape,np.uint8)
    cv2.drawContours(drawing,[cnt],0,(0,255,0),2)
    cv2.drawContours(drawing,[hull],0,(0,0,255),2)
    hull = cv2.convexHull(cnt,returnPoints = False)
    defects = cv2.convexityDefects(cnt,hull)

    moments = cv2.moments(cnt)
    if moments['m00']!=0:
        cx = value(moments['m10'],moments['m00'])
        cy = value(moments['m01'],moments['m00'])
    centr=(cx,cy)
    c1 = int(cx)
    c2 = int(cy)

    cv2.circle(drawing, (c1,c2), 4, (0,0 , 255), -1)
    counter = frame_counter % 10
    handCenterPositions_x[counter]=c1
    handCenterPositions_y[counter]=c2


    if frame_counter>=10:
        track_handcentre()

    mind = 0
    maxd = 0
    j = 0
    for j in range(0,len(hull),1) :
        x = hull[j]

        cc1 = cnt[x][0][0][0]
        cc2 = cnt[x][0][0][1]
        cv2.circle(drawing,(cc1,cc2),5, (255,0 , 0), -1)

    # "Going to Next frame..."
    #paint_x[frame_counter] = c1
    #paint_y[frame_counter] = c2
    topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
    leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
    cv2.circle(drawing, (topmost[0], topmost[1]), 13, (120, 0, 120), -1)
    cv2.circle(drawing, (leftmost[0], leftmost[1]), 13, (0, 200, 200), -1)
    cv2.circle(img, (topmost[0] -400, topmost[1]-100), 13, (120, 0, 120), -1)
    cv2.circle(img, (leftmost[0]-100, leftmost[1]-400), 13, (0, 200, 200), -1)
    tt = (int)(topmost[0])
    ll = (int)(leftmost[0])

    if (tt-ll)in [-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,0,1,2,3,4,5,6,7,8,9,10] :
     paint_x.append(topmost[0])
     paint_y.append(topmost[1])

    painting = np.zeros(crop.shape, np.uint8)  # used for painting...
    draw_paint()



    cd = 0
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        dist = cv2.pointPolygonTest(cnt,centr,True)
        cv2.line(drawing,start,end,[255,255,255],2)


        a = euclid_distance(end[0],end[1],start[0],start[1])
        b = euclid_distance(far[0],far[1],start[0],start[1])
        c = euclid_distance(end[0],end[1],far[0],far[1])
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57
        if angle <= 90:
            cd += 1
            cv2.circle(drawing, far, 5, [255, 0, 255], -1)

    leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
    topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])


    if (cd==1):
        cv2.putText(img,'1', (10, 500), cv2.FONT_HERSHEY_SIMPLEX,3,2)
        if (previous_defects != cd):
            print cd
            os.system("say 'one'")
    elif (cd== 2):
        cv2.putText(img, "2", (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 3, 2)
        #click_photo(topmost, leftmost, c1, c2)
        if (previous_defects != cd):
            print cd
            os.system("say 'two'")
    elif (cd == 3):
        cv2.putText(img, "3", (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 3, 2)
        if (previous_defects != cd):
            print cd
            os.system("say 'three'")
    elif (cd == 4):
        cv2.putText(img, "4", (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 3, 2)
        if (previous_defects != cd):
            print cd
            os.system("say 'four'")
    elif (cd == 5):
        cv2.putText(img, "5", (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 3, 2)
        if (previous_defects != cd):
            print cd
            os.system("say 'five'")
    else :
        cv2.putText(img, "other gesture...", (100, 500), cv2.FONT_HERSHEY_SIMPLEX, 3, 2)
        eraser_x.append(300 - topmost[0])
        eraser_y.append(topmost[1])
        ersase()


    cv2.imshow('Original_image', img)
    cv2.imshow('Output1', drawing)
    previous_defects = cd
    frame_counter += 1
    cv2.imshow('Paint_brush', painting)
    k = cv2.waitKey(10)
    if k == 27:
        break

print frame_counter
