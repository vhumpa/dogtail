#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'


# Nautilus test
# Takes an image file, uses Imagemagick to chop it into tiles,
# then arranges the Nautilus thumbnail icons into a collage
# FIXME: somewhat unstable, requires a 640x480 image called victim.png

from dogtail.apps.wrappers.nautilus import *
from math import sin, cos, pi

import os

import dogtail.config
#dogtail.config.config.debugSearching=True
#dogtail.config.config.debugSleep = True

n = NautilusApp()

class Jigsaw:
    def __init__(self, sourceImage):
        self.sourceImage = os.path.abspath(sourceImage)
        self.basePath = os.curdir
        self.piecesPath = os.path.abspath(os.path.join(self.basePath, "JigsawPieces"))
        self.resultPath = os.path.abspath(os.path.join(self.basePath, "JigsawResult"))
        self.pieceArg = os.path.join(self.piecesPath, "piece.png")

        self.baseWidth = 640
        self.baseHeight = 480
        self.divisor = 5
        self.pieceWidth = self.baseWidth/self.divisor
        self.pieceHeight = self.baseHeight/self.divisor
        self.iconWidth = 70.0 # self.baseWidth/self.divisor
        self.iconHeight = 54.0 # self.baseHeight/self.divisor

    def makeCropCommand(self):
        return 'convert -crop %sx%s %s %s'%(self.pieceWidth, self.pieceHeight, self.sourceImage, self.pieceArg)

    def targetLocation(self, baseXY, index):
        (baseX, baseY) = baseXY
        (pieceX,pieceY) = ((float(index)%self.divisor)*self.iconWidth, (float(index)/self.divisor)*self.iconHeight)
        return (baseX+pieceX,baseY+pieceY)

    def makeDirectories(self):
        try: os.mkdir(self.piecesPath)
        except OSError: pass

        try: os.mkdir(self.resultPath)
        except OSError: pass

class Drag:
    def __init__(self, startXY, endXY):
        self.startXY = startXY
        self.endXY = endXY

    def doDrag(self, duration, steps):
        ev = atspi.EventGenerator()

        (x,y) = self.calcCoord(0.0)
        ev.absoluteMotion(x, y)
        doDelay(0.1)
        ev.press (x,y,1)

        for step in range(steps):
            frac = float(step)/float(steps)
            (x,y) = self.calcCoord(frac)
            #doDelay(duration/steps)
            ev.absoluteMotion(x, y)

        (x,y) = self.calcCoord(1.0)
        ev.absoluteMotion(x,y)
        doDelay(0.5)
        ev.release (x,y,1)

    def calcCoord(self, frac):
        raise NotImplementedError

class LinearDrag(Drag):
    def calcCoord(self, frac):
        (startX, startY) = self.startXY
        (endX, endY) = self.endXY
        #(deltaX, deltaY) = (endX-startX, endY-startY)

        return ( (startX*(1.0-frac)) + (endX*frac), (startY*(1.0-frac)) + (endY*frac))

jigsaw = Jigsaw('victim.png')

jigsaw.makeDirectories()

command = jigsaw.makeCropCommand()
print command
os.system(command)
#raise "foo"
#os.exit()

def prepareNautilusWindow(w):
    viewMenu = w.menu("View")

    # Ensure it's in icon view mode:
    viewMenu.menuItem("View as Icons").click()

    viewMenu.menuItem("Normal Size").click()
    viewMenu.menuItem("Zoom In").click()

    # Ensure we're in manual layout mode:
    viewMenu.menu("Arrange Items").menuItem("Manually").click()

    viewMenu.menuItem("Clean Up by Name").click()



piecesWindow = n.openPath(jigsaw.piecesPath)
resultWindow = n.openPath(jigsaw.resultPath)

prepareNautilusWindow (piecesWindow)
prepareNautilusWindow (resultWindow)

#FIXME: now need to get both on top, with sane sizes

# Find the icons:
iv = piecesWindow.iconView()
icons = iv.findChildren(IsAnIcon(), recursive=True)

matcher = re.compile('piece-(.*).png')

for icon in icons:
    #print icon
    index = int(matcher.match(icon.name).group(1))
    (x,y,w,h) = icon.extents

    (dstX, dstY, dstW, dstH) = resultWindow.iconView().extents

    (targetX, targetY) = jigsaw.targetLocation((dstX+100, dstY+100), index)

    # FIXME: different drag routes!
    drag = LinearDrag((x+w/2,y+h/2), (targetX+w/2,targetY+h/2))
    drag.doDrag(2.0, 50)

# Drag out to select the entire collage:
(dstX, dstY, dstW, dstH) = resultWindow.iconView().extents
drag = LinearDrag((dstX+50, dstY+50), (dstX+500, dstY+500))
drag.doDrag(2.0, 500)

sleep(0.5)

# Drag it somewhere:
drag = LinearDrag((dstX+300, dstY+300), (dstX+600, dstY+600))
drag.doDrag(2.0, 50)

sleep(0.5)

click(dstX+50, dstY+50, 1)
#viewMenu = resultWindow.menu("View")
#viewMenu.menuItem("Zoom In").click()
#viewMenu.menuItem("Zoom In").click()
