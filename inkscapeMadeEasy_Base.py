#!/usr/bin/python

# -----------------------------------------------------------------------------
#
#    inkscapeMadeEasy: - Helper module that extends Aaron Spike's inkex.py module,
#                        focusing productivity in inkscape extension development
#
#    Copyright (C) 2016 by Fernando Moura
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# -----------------------------------------------------------------------------

import inkex
import re
from lxml.etree import tostring
import numpy as np
import os
import sys

"""
Base helper module that extends Aaron Spike's inkex.py module, adding basic manipulation functions

This module requires the following modules: inkex, re, lxml, numpy and os.
"""


#---------------------------------------------
class inkscapeMadeEasy(inkex.Effect):
    """
    Base class for extensions.

    This class extends the inkex.Effect class by adding several basic functions to help manipulating inkscape elements. All extensions should inherit this class.

    """

    def __init__(self):
        inkex.Effect.__init__(self)

    # coordinates o the origin of the grid. unfortunately the grid does not fit
    # x0=0
    # y0=-7.637817382813
    
    def displayMsg(self,msg):
        """Displays a message to the user.

        :param msg: message
        :type msg: string
        
        :returns: nothing
        :rtype: -

        """
        sys.stderr.write(msg + '\n')

    def getBasicLatexPackagesFile(self):
        """Returns the full path  of the ``basicLatexPackages.tex`` file with commonly used Latex packages 

        The default packages are::

        \usepackage{amsmath,amsthm,amsbsy,amsfonts,amssymb}
        \usepackage[per=slash]{siunitx}
        \usepackage{steinmetz}

        You can add other packages to the file ``basicLatexPackages.tex``, located in the extension directory.

        :returns:  Full path  of the file with commonly used Latex packages 
        :rtype: string

        """
        directory = os.getcwd()
        return directory + '/textextLib/basicLatexPackages.tex'

    def Dump(self, obj, file='./dump_file.txt', mode='w'):
        """Function to easily output the result of ``str(obj)`` to a file

        This function was created to help debugging the code while it is running under inkscape. Since inkscape does not possess a terminal as today (2016), this function overcomes partially the issue of sending things to stdout by dumping result of the function ``str()`` in a text file.


        :param obj: object to sent to a file. Any type that can be used in ``str()``
        :param file: file path. Default: ``./dump_file.txt``
        :param mode: writing mode of the file Default: ``w`` (write)
        :type obj: any, as long as ``str(obj)`` is implemented (see ``__str__()`` metaclass definition )
        :type arg2: string
        :type mode: string
        :returns:  nothing
        :rtype: -

        **Example**

        >>> from inkscapeMadeEasy_Base import inkscapeMadeEasy 
        >>> x=inkscapeMadeEasy
        >>> vector1=[1,2,3,4,5,6]
        >>> x.Dump(vector,file='~/temporary.txt',mode='w')   % writes the list to a file
        >>> vector2=[7,8,9,10]
        >>> x.Dump(vector2,file='~/temporary.txt',mode='a')   % append the list to a file


        """
        file = open(file, mode)
        file.write(str(obj) + '\n')
        file.close()

    #
    def uniqueIdNumber(prefix_id):
        """ Generates a unique ID with a given prefix ID by adding a numeric suffix

        This function is used to generate a valid unique ID by concatenating a given prefix with a numeric suffix. The overall format is ``prefix-%05d``.

        This function makes sure the ID is unique by checking in ``doc_ids`` member. This function is specially useful for creating an unique ID for markers and other elements in defs.


        :param prefix_id: prefix of the ID
        :type prefix_id: string
        :returns: the unique ID
        :rtype: string

        .. note:: This function has been adapted from Aaron Spike's inkex.py  https://github.com/hacktoon/ink2canvas/blob/master/ink2canvas/lib/inkex.py

        **Example**

        >>> from inkscapeMadeEasy_Base import inkscapeMadeEasy 
        >>> x=inkscapeMadeEasy
        >>> a=x.uniqueIdNumber('myName')   % a=myName-00001
        >>> b=x.uniqueIdNumber('myName')   % b=myName-00002
        >>> c=x.uniqueIdNumber('myName')   % c=myName-00003


        """
        numberID = 1
        new_id = prefix_id + '-%05d' % (numberID)
        while new_id in self.doc_ids:
            numberID += 1
            new_id = prefix_id + '-%05d' % (numberID)
        self.doc_ids[new_id] = 1

        return new_id

    #---------------------------------------------
    def getDefinitions(self):
        """ retrieves the Defs (xpath) element of the svg file.


        This function returns the element Defs of the current svg file. This elements stores the definition (e.g. marker definition)

        if no Defs can be found, a new empty Defs is created

        :returns: the defs element
        :rtype: xpath

        """
        defs = self.xpathSingle('/svg:svg//svg:defs')
        if defs == None:
            defs = inkex.etree.SubElement(self.document.getroot(), inkex.addNS('defs', 'svg'))

        return defs

    #---------------------------------------------
    def createGroup(self, parent, label='none'):
        """Creates a new empty group of elements.

        This function creates a new empty group of elements. In order to create new elements inside this groups you must create them informing the group as the parent element.


        :param parent: parent object of the group. It can be another group or the root element
        :param label: label of the group. Default: 'none'
        :type parent: element object
        :type label: string
        :returns: the group object
        :rtype: group element


        .. note:: The label does not have to be unique

        **Example**

        >>> rootLayer = self.document.getroot()                              # retrieves the root layer of the file
        >>> groupA = self.createGroup(rootLayer,label='temp')                # creates a group inside rootLayer
        >>> groupB = self.createGroup(groupA,label='child')                  # creates a group inside groupA
        >>> line1 = inkscapeMadeEasy_Draw.line.relCoords(groupA, [[10,0]],[0,0])       # creates a line in groupA
        >>> line2 = inkscapeMadeEasy_Draw.line.relCoords(groupB, [[20,0]],[0,0])       # creates a line in groupB
        """
        if label != 'none':
            g_attribs = {inkex.addNS('label', 'inkscape'): label}
            group = inkex.etree.SubElement(parent, 'g', g_attribs)
        else:
            group = inkex.etree.SubElement(parent, 'g')

        return group

    #---------------------------------------------
    def getTransformMatrix(self, element):
        """Returns the transformation attribute of the given element and the resulting transformation matrix (numpy Array)

        This function is used to extract the transformation operator of a given element.

        :param element: element object
        :type element: element object
        :returns: [transfAttrib, transfMatrix]

          - transfAttrib: string containing all transformations as it is in the file
          - transfMatrix: numpy array with the resulting transformation matrix
        :rtype: tuple

        If the element does not have any transformation attribute, this function returns:
           - transfAttrib=''
           - transfMatrix=identity matrix
        """

        transfAttrib = ''
        transfMatrix = np.eye(3)

        if 'transform' in element.attrib:
            transfAttrib = element.attrib['transform']

        if not transfAttrib:
            return transfAttrib, transfMatrix

        # split operation into several strings
        listOperations = [e + ')' for e in transfAttrib.replace(',', ' ').split(')') if e != ""]

        for operation in listOperations:
            if 'translate' in operation:
                data = re.compile("translate\((.*?\S)\)").match(operation.lstrip()).group(1).split()  # retrieves x and y values
                x = float(data[0])
                y = float(data[1])
                mat = np.array([[1, 0, x], [0, 1, y], [0, 0, 1]])
                transfMatrix = np.dot(transfMatrix, mat)

            if 'scale' in operation:
                data = re.compile("scale\((.*?\S)\)").match(operation.lstrip()).group(1).split()  # retrieves x and y values
                scalex = float(data[0])
                if len(data) == 2:
                    scaley = float(data[1])
                else:
                    scaley = scalex
                mat = np.diag([scalex, scaley, 1])
                transfMatrix = np.dot(transfMatrix, mat)

            if 'rotate' in operation:
                data = re.compile("rotate\((.*?\S)\)").match(operation.lstrip()).group(1).split()  # retrieves x and y values
                angleRad = -float(data[0]) * np.pi / 180.0  # negative angle because inkscape is upside down =(
                matRot = np.array([[np.cos(angleRad), np.sin(angleRad), 0], [-np.sin(angleRad), np.cos(angleRad), 0], [0, 0, 1]])
                if len(data) == 3:  # must translate before and after rotation
                    x = float(data[1])
                    y = float(data[2])
                    matBefore = np.array([[1, 0, x], [0, 1, y], [0, 0, 1]])  # translation before rotation
                    matAfter = np.array([[1, 0, -x], [0, 1, -y], [0, 0, 1]])  # translation after rotation
                    matRot = np.dot(matBefore, matRot)
                    matRot = np.dot(matRot, matAfter)

                transfMatrix = np.dot(transfMatrix, matRot)

            if 'skewX' in operation:
                data = re.compile("skewX\((.*?\S)\)").match(operation.lstrip()).group(1).split()  # retrieves x and y values
                angleRad = float(data[0]) * np.pi / 180.0
                mat = np.array([[1, np.tan(angleRad), 0], [0, 1, 0], [0, 0, 1]])
                transfMatrix = np.dot(transfMatrix, mat)

            if 'skewY' in operation:
                data = re.compile("skewY\((.*?\S)\)").match(operation.lstrip()).group(1).split()  # retrieves x and y values
                angleRad = float(data[0]) * np.pi / 180.0
                mat = np.array([[1, 0, 0], [np.tan(angleRad), 1, 0], [0, 0, 1]])
                transfMatrix = np.dot(transfMatrix, mat)

            if 'matrix' in operation:
                data = re.compile("matrix\((.*?\S)\)").match(operation.lstrip()).group(1).split()  # retrieves x and y values
                a = float(data[0])
                b = float(data[1])
                c = float(data[2])
                d = float(data[3])
                e = float(data[4])
                f = float(data[5])
                mat = np.array([[a, c, e], [b, d, f], [0, 0, 1]])
                transfMatrix = np.dot(transfMatrix, mat)

        return transfAttrib, transfMatrix

    #---------------------------------------------
    def rotateElement(self, element, center, angleDeg):
        """Rotates the element using the transformation attribute.

        It is possible to rotate elements isolated or entire groups.

        :param element: element object to be rotated
        :param center: tuple with center point of rotation
        :param angleDeg: angle of rotation in degrees, counter-clockwise direction
        :type element: element object
        :type center: tuple
        :type angleDeg: float
        :returns:  nothing
        :rtype: -

        **Example**

        >>> rootLayer = self.document.getroot()                              # retrieves the root layer of the file
        >>> groupA = self.createGroup(rootLayer,label='temp')                # creates a group inside rootLayer
        >>> line1 = inkscapeMadeEasy_Draw.line.relCoords(groupA, [[5,0]],[0,0])       # creates a line in groupA
        >>> line2 = inkscapeMadeEasy_Draw.line.relCoords(rootLayer, [[5,0]],[0,0])    # creates a line in rootLayer
        >>> self.rotateElement(line2,[0,0],120)                              # rotates line2 120 degrees around center x=0,y=0
        >>> self.rotateElement(groupA,[1,1],-90)                             # rotates groupA -90 degrees around center x=1,y=1
        """
        transfString = ''

        if angleDeg == 0:
            return

        if 'transform' in element.attrib:
            transfString = element.attrib['transform']

        # if transform attribute is present, we must add the new rotation
        if transfString:
            newTransform = 'rotate(%f %f %f) %s' % (-angleDeg, center[0], center[1], transfString)  # negative angle bc inkscape is upside down
        else:  # if no transform attribute was found
            newTransform = 'rotate(%f %f %f)' % (-angleDeg, center[0], center[1])  # negative angle bc inkscape is upside down

        element.attrib['transform'] = newTransform

    #---------------------------------------------
    def moveElement(self, element, distance):
        """Moves the element using the transformation attribute.

        It is possible to move elements isolated or entire groups.

        :param element: element object to be rotated
        :param distance: tuple with the distance to move the object
        :type element: element object
        :type distance: tuple
        :returns:  nothing
        :rtype: -

        **Example**

        >>> rootLayer = self.document.getroot()                              # retrieves the root layer of the file
        >>> groupA = self.createGroup(rootLayer,label='temp')                # creates a group inside rootLayer
        >>> line1 = inkscapeMadeEasy_Draw.line.relCoords(groupA, [[5,0]],[0,0])       # creates a line in groupA
        >>> line2 = inkscapeMadeEasy_Draw.line.relCoords(rootLayer, [[5,0]],[0,0])    # creates a line in rootLayer
        >>> self.moveElement(line2,[10,10])                                  # moves line2  DeltaX=10, DdeltaY=10
        >>> self.moveElement(groupA,[10,-10])                                # moves line2  DeltaX=10, DdeltaY=-10
        """

        if distance == 0:
            return

        transfString = ''

        if 'transform' in element.attrib:
            transfString = element.attrib['transform']

        # if transform attribute is present, we must add the new translation
        if transfString:
            newTransform = 'translate(%f %f) %s ' % (distance[0], distance[1], transfString)
        else:  # if no transform attribute was found
            newTransform = 'translate(%f %f)' % (distance[0], distance[1])

        element.attrib['transform'] = newTransform

    #---------------------------------------------
    def scaleElement(self, element, scaleX=1.0, scaleY=0.0):
        """Scales the element using the transformation attribute.

        It is possible to scale elements isolated or entire groups.

        :param element: element object to be rotated
        :param scaleX: scaling factor in X direction. Default=1.0
        :param scaleY: scaling factor in Y direction. Default=0.0
        :type element: element object
        :type scaleX: float
        :type scaleX: float
        :returns:  nothing
        :rtype: -


        .. note:: If scaleY==0, then scaleY=scaleX is assumed (default behavior)

        **Example**

        >>> rootLayer = self.document.getroot()                              # retrieves the root layer of the file
        >>> groupA = self.createGroup(rootLayer,label='temp')                # creates a group inside rootLayer
        >>> circ1 = centerRadius(groupA,centerPoint=[0,0],radius=1.0)        # creates a line in groupA
        >>> circ2 = centerRadius(rootLayer,centerPoint=[0,0],radius=1.0)     # creates a line in rootLayer
        >>> self.scaleElement(circ1,2.0)                                     # scales x2 in both X and Y directions
        >>> self.scaleElement(circ1,2.0,3.0)                                 # scales x2 in X and x3 in Y
        >>> self.scaleElement(groupA,0.5)                                    # scales x0.5 the group in both X and Y directions
        """

        transfString = ''

        if 'transform' in element.attrib:
            transfString = element.attrib['transform']

        # if transform attribute is present, we must add the new translation
        if transfString:
            if scaleY != 0.0:
                newTransform = 'scale(%f %f) %s ' % (scaleX, scaleY, transfString)
            else:
                newTransform = 'scale(%f) %s' % (scaleX, transfString)
        else:  # if no transform attribute was found
            if scaleY != 0.0:
                newTransform = 'scale(%f %f)' % (scaleX, scaleY)
            else:
                newTransform = 'scale(%f)' % (scaleX)

        element.attrib['transform'] = newTransform

    #---------------------------------------------
    def findMarker(self, markerName):
        """Search for markerName in the document.

        :param markerName: marker name
        :type markerName: string

        :returns: True if markerName was found
        :rtype: bool
        """

        doc_markers = {}

        for child in self.getDefinitions():
            if child.get('id') == markerName:
                return True

        return False

    #---------------------------------------------
    def getPoints(self, element):
        """Retrieves the list of points of the element.

        This function works on paths, texts or groups. In the case of a group, the function will include recursively all its components

        :param element: element object
        :type element: element object
        :returns: list of points
        :rtype: list of list

        .. note:: This function will consider any transformation stored in transform attribute, that is, it will compute the resulting coordinates of each object

        **Example**

        >>> rootLayer = self.document.getroot()                                   # retrieves the root layer of the file
        >>> line1 = inkscapeMadeEasy_Draw.line.relCoords(rootLayer, [[5,0],[0,6]],[0,0])   # creates a line in groupA
        >>> list = self.getPoints(line1)                                          # gets list = [[0.0, 0.0], [5.0, 0.0], [5.0, 6.0]]

        """

        # stores the list of coordinates
        listCoords = []

        # check if element is valid. 'path', 'text' and 'g' are valid
        accepted_strings = set( [ inkex.addNS('path', 'svg'), inkex.addNS('text', 'svg'), 'g', 'path'] )
        if element.tag not in accepted_strings:
            return listCoords

        if element.tag == inkex.addNS('path', 'svg') or element.tag == 'path':  # if object is path


            dString = re.sub('([a-df-zA-DF-Z])+?', r'#\1#', element.attrib['d']).replace('z', '').replace('Z', '').replace(',', ' ').split('#')  # adds special character between letters and splits. the first regular expression excludes e and E bc they are used to represent scientific notation  =S

            dString = [i.lstrip() for i in dString]  # removes leading spaces from strings
            dString = filter(None, dString)  # removes empty elements
            Xcurrent = 0
            Ycurrent = 0
            while len(dString) > 0:
                commandType = dString[0]
                argument = [float(x) for x in dString[1].split()]  # extracts arguments from M command and converts to float
                del dString[0]
                del dString[0]

                if commandType in 'mMlLtT':  # extracts points from command 'move to' M/m or 'line to' l/L or 'smooth quadratic Bezier curveto't/T
                    X = argument[0::2]  # 2 parameters per segment, x is 1st
                    Y = argument[1::2]  # 2 parameters per segment, y is 2nd

                if commandType in 'hH':  # extracts points from command 'horizontal line' h/H
                    X = argument
                    Y = [Ycurrent] * len(X)

                if commandType in 'vV':  # extracts points from command 'vertical line' v/V
                    Y = argument
                    X = [Xcurrent] * len(Y)

                if commandType in 'cC':  # extracts points from command 'Bezier Curve' c/C
                    X = argument[4::6]  # 6 parameters per segment, x is 5th
                    Y = argument[5::6]  # 6 parameters per segment, y is 6th

                if commandType in 'sSqQ':  # extracts points from command 'quadratic Bezier Curve' q/Q or 'smooth curveto' s/S
                    X = argument[2::4]  # 4 parameters per segment, x is 3rd
                    Y = argument[3::4]  # 4 parameters per segment, y is 4th

                if commandType in 'aA':  # extracts points from command 'arc' a/A
                    X = argument[5::7]  # 7 parameters per segment, x is 6th
                    Y = argument[6::7]  # 7 parameters per segment, y is 7th

                if commandType in 'h':  # if h
                    for i in range(1, len(X)):  # convert to abs coordinates
                        X[i] = X[i] + X[i - 1]

                if commandType in 'v':  # if v
                    for i in range(1, len(Y)):  # convert to abs coordinates
                        Y[i] = Y[i] + Y[i - 1]

                if commandType in 'mltcsqa':  # if m or l
                    for i in range(1, len(X)):  # convert to abs coordinates
                        X[i] = X[i] + X[i - 1]
                        Y[i] = Y[i] + Y[i - 1]

                coords = zip(X, Y)
                listCoords.extend(coords)
                Xcurrent = X[-1]
                Ycurrent = Y[-1]

        if element.tag == inkex.addNS('text', 'svg'):  # if object is a text
            x = float(element.attrib['x'])
            y = float(element.attrib['y'])
            coords = [[x, y]]
            listCoords.extend(coords)

        if element.tag == 'g':  # if object is a group
            for obj in element.iter():
                if obj != element:
                    listPoints = self.getPoints(obj)
                    listCoords.extend(listPoints)

        # apply transformation
        transfMat = self.getTransformMatrix(element)[1]

        # creates numpy array with the points to be transformed
        coordsNP = np.hstack((np.array(listCoords), np.ones([len(listCoords), 1]))).transpose()

        coordsTransformed = np.dot(transfMat, coordsNP)
        coordsTransformed = np.delete(coordsTransformed, 2, 0).transpose().tolist()  # remove last line, transposes and converts to list of lists

        return coordsTransformed

    #---------------------------------------------
    def getBoundingBox(self, element):
        """Retrieves the bounding Box of the element.

        This function works on paths, texts or groups. In the case of a group, the function will consider recursively all its components

        :param element: element object
        :type element: element object
        :returns: two lists: [xMin,yMin] and [xMax,yMax]
        :rtype: list

        .. note:: This function will consider any transformation stored in transform attribute, that is, it will compute the resulting coordinates of each object

        **Example**

        >>> rootLayer = self.document.getroot()                                   # retrieves the root layer of the file
        >>> line1 = inkscapeMadeEasy_Draw.line.relCoords(rootLayer, [[5,0],[0,6]],[0,0])   # creates a line in groupA
        >>> BboxMin,BboxMax = self.getBoundingBox(line1)                          # gets BboxMin = [0.0, 0.0] and BboxMax = [5.0, 6.0]

        """
        coords = self.getPoints(element)
        coordsNP = np.array(coords)

        bboxMax = np.max(coordsNP, 0)
        bboxMin = np.min(coordsNP, 0)
        return bboxMin.tolist(), bboxMax.tolist()

    #---------------------------------------------
    def getCenter(self, element):
        """Retrieves the center coordinates of the bounding Box of the element.

        This function works on paths, texts or groups. In the case of a group, the function will consider recursively all its components

        :param element: element object
        :type element: element object
        :returns: two lists: [xCenter,yCenter]
        :rtype: list

        .. note:: This function will consider any transformation stored in transform attribute, that is, it will compute the resulting coordinates of each object

        **Example**

        >>> rootLayer = self.document.getroot()                                   # retrieves the root layer of the file
        >>> line1 = inkscapeMadeEasy_Draw.line.relCoords(rootLayer, [[5,0],[0,6]],[0,0])   # creates a line in groupA
        >>> Center = self.getCenter(line1)                                        # gets Center = [2.5, 3.0]

        """

        bboxMin, bboxMax = self.getBoundingBox(element)

        bboxCenter = [(bboxMax[0] + bboxMin[0]) / 2, (bboxMax[1] + bboxMin[1]) / 2]

        return bboxCenter
