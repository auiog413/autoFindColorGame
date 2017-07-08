import cv2
import numpy as np
import os
import pyscreenshot as ss
import time
import sys

############################
# Configration Start
############################
BROWSER='firefox'
GAME_URL='http://www.4399.com/flash/144484_2.htm'
TM_THRESHOLD=10000
TEMPLATE_BROWSER_ADDRESS_BAR='area-' + str(BROWSER) + '-address-bar.png'
############################
# Configration End
############################

def templateMatching(tpl):
    template = cv2.imread(tpl,0)
    w, h = template.shape[::-1]
    os.system('scrot -q 100 tmp.png >/dev/null 2>&1')
    src = cv2.imread('tmp.png', 0)
    res = cv2.matchTemplate(src,template,cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    os.system('rm -f tmp.png');
    (x,y)=min_loc
    return x+w/2,y+h/2,min_val

def mouseMoveAndClick(x,y):
    os.system('xdotool mousemove ' + str(x) + ' ' + str(y))
    os.system('xdotool click 1')

def clickArea(tpl, threshold):
    min_val=int(threshold)+1
    while (min_val > threshold):
        time.sleep(0.5)
        (click_x, click_y, min_val)=templateMatching(tpl)
    mouseMoveAndClick(click_x, click_y)
    return click_x, click_y, min_val

flag = True
pLeftTop = None
pRightBottom = None
grabRightBottom = None

os.system('xdotool exec ' + str(BROWSER) + ' >/dev/null 2>&1')

# detect location of chromium address bar using opencv template matching and click it
threshold = TM_THRESHOLD + 1
while (threshold > TM_THRESHOLD):
    (click_x, click_y, threshold) = templateMatching(TEMPLATE_BROWSER_ADDRESS_BAR)
# type the game url using xdotool
mouseMoveAndClick(click_x, click_y)
os.system('xdotool type "' + str(GAME_URL) + '"')
os.system('xdotool key Return')

# detect location of play button of first screen and click it
clickArea('btn-start-play.png', TM_THRESHOLD)

# detect location of play button of second screen and click it
(click_x, click_y, threshold) = clickArea('btn-play.png', TM_THRESHOLD)
# close background music
clickArea('btn-music.png', TM_THRESHOLD)

pLeftTop = (int(click_x) - 209, int(click_y) - 249)
pRightBottom = (int(click_x) + 140, int(click_y) + 100)
time.sleep(1)

grabRightBottom = templateMatching('area-social.png')

while True:
    img = ss.grab(bbox=(0,0,grabRightBottom[0],grabRightBottom[1]))
    img = np.array(img)
    target = img[pLeftTop[1]:pRightBottom[1],pLeftTop[0]:pRightBottom[0]]
    gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    im, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    centersGray = []
    for c in contours:
        (x,y), radius = cv2.minEnclosingCircle(c)
        x, y = int(x), int(y)
        centers.append((x,y))
        centersGray.append(gray[y,x])
    sets = set(centersGray)
    index = None
    for s in sets:
        if centersGray.count(s) == 1:
            index = centersGray.index(s)
            break
    realX = centers[index][0] + pLeftTop[0]
    realY = centers[index][1] + pLeftTop[1]
    os.system('xdotool mousemove '+str(realX)+' '+str(realY))
    os.system('xdotool click 1')
    print(realX,realY)
    time.sleep(0.1)