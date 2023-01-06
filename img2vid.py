from random import randint
import cv2
import numpy as np
#import psycopg2
import mysql.connector
from mysql.connector import errorcode
import logging

# git info
PATH_OF_GIT_REPO = r'/home/ec2-user/python/world/main'

# Logger
logging.basicConfig(filename='./img2vid.log', level=logging.DEBUG)

# data scale
w, h = 10,10 
# dot scale
dot_scale = 10
# video size
sw, sh = (w* dot_scale, h* dot_scale)
# video fps
fps = 60.0
# frame count
fnum = 1

# output file
videoout = './world/main/output.mp4'
imgout = './world/main/frame.png'

#R step
step_res = 5
# Res values
resLib = [0,135,195,230,255]

#G step
step_ord = 3
# Ord values
ordLib = [0,210,255]

#B step
step_pio = 4
# Pio values
pioLib = [0,180,210,255]

# random stock
stock =[0,0,1,1,2]


def main():

    # set codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(videoout, fourcc, fps, (sw, sh))

    # get current params
    datalist = getCurrent()
    # get 2D map data
    datamap = get2DMap(datalist)
    # get scaled RGB image
    # rgbframe = getRGBMap(datamap).repeat(dot_scale, axis=0).repeat(dot_scale,axis=1)
    # writer.write(rgbframe)

    nextmap=datamap
    for i in range(fnum):
        # get next map
        nextmap = drawNext(nextmap)
        # get scaled RGB image
        nextframe = getRGBMap(nextmap).repeat(dot_scale, axis=0).repeat(dot_scale,axis=1)
        writer.write(nextframe)
        writer.write(nextframe)

    # export img           
    # cv2.imwrite(imgout,rgbframe)
    # write video
    # frame  =cv2.imread("./indexL.png")
    writer.release()


# get current data from DB
def getCurrent():
    try:
        # Create Conn(MySQL)
        conn = mysql.connector.connect(
            host='localhost',
            user='gen',
            password='vrcWorld_001',
            port= '3306',
            database='worldgen',
            auth_plugin="mysql_native_password"
            )

        # Create Conn(PG)
        #dsn = "dbname=worldgen host=localhost port=5432 user=gen password=vrcworld001"
        #conn = psycopg2.connect(dsn)

        cur = conn.cursor()
    
        cur.execute("select * from env_score")
        datalist = cur.fetchall()

        cur.close()
        conn.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Cannnot connect database.')
        else:
            print(err)
    else:
        conn.close()
    
    return datalist


# convert list to 2Dmap
def get2DMap(datalist):
    # Generate blank Image
    dataMap = np.zeros((w, h, 3), dtype=np.uint8)
    
    for data in datalist:
        x = data[0]
        y = data[1]
        #G
        ord = data[2]
        #R
        res = data[3]
        #B
        pio = data[4]
        trr = data[5]
        # [G,B,R]
        dataMap[x,y] = [ord,pio,res]
        # logging.debug(dataMap[x,y])

    return dataMap


# convert map to RGB
def getRGBMap(dataMap):
    rgbMap=np.zeros((w, h, 3), dtype=np.uint8)

    for x1 in range(w):
        for y1 in range(h):
            dot = dataMap[x1,y1]
            #G
            ord = ordLib[(dot[0])]
            #B
            pio = pioLib[(dot[1])]
            #R
            res = resLib[(dot[2])]            
            # [G,B,R]
            rgbMap[x1,y1] = [ord,pio,res]
            logging.debug("{0},{1}:{2}".format(x1,y1,dataMap[x1,y1]))

    return rgbMap


# calculate next data
def drawNext(data_old):

    data=np.pad(data_old,[(1,1),(1,1),(0,0)],"constant")
    newlist = np.zeros((w, h, 3), dtype=np.uint8)

    # border
    #borderg=[0,7,13] #18
    borderg=[6,12] #18
    #borderb=[0,7,14,21] #27
    borderb=[9,18] #27
    #borderr=[0,9,16,23,30] #36
    borderr=[12,24] #36

    for dy in range(1,h+1):
        for dx in range(1,w+1):

            [ord,pio,res]=data[dx,dy]

            life =(data[dx-1,dy-1]+data[dx,dy-1]+data[dx+1,dy-1]
                    +data[dx-1,dy]+data[dx,dy]+data[dx+1,dy]
                    +data[dx-1,dy+1]+data[dx,dy+1]+data[dx+1,dy+1])

            # g layer in data[dx,dy][0]
            if   (life[0] < borderg[0]) :               ord+=-1
            elif (borderg[0] <= life[0] < borderg[1]) : ord+=0
            elif (borderg[1] <= life[0]):               ord+=1
            ord +=(stock[randint(0,4)])
            ord -=data[dx,dy][0]
            if ord < 0 : ord = 0
            if ord > 2 : ord = 2

            # b layer in data[dx,dy][1]
            if   (life[1] < borderb[0]) :               pio+=-1
            elif (borderb[0] <= life[1] < borderb[1]) : pio+=0
            elif (borderb[1] <= life[1]):               pio+=1
            pio +=(stock[randint(0,4)])
            pio -=data[dx,dy][1]
            if pio < 0 : pio = 0
            if pio > 3 : pio = 3

            # r layer in data[dx,dy][2]
            if   (life[2] < borderr[0]) :               res+=-1
            elif (borderr[0] <= life[2] < borderr[1]) : res+=0
            elif (borderr[1] <= life[2]):               res+=1
            res +=(stock[randint(0,4)])
            res -=data[dx,dy][2]
            if res < 0 : res = 0
            if res > 4 : res = 4

            logging.debug([ord,pio,res])
            newlist[dx-1,dy-1]=[ord,pio,res]

    return newlist

if __name__ == "__main__":
    main()
