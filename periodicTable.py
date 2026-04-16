# -*- coding: utf-8 -*-
"""
@author: Grace Iroagalachi
"""

import csv
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel
import matplotlib.pyplot as plt
from itertools import product
from matplotlib.patches import Rectangle
from matplotlib.pyplot import arrow
from functools import partial


class PeriodicTable(QWidget):
    def __init__(self):
        """ This method initialises the code. Constants are defined here, the figure is set up, and the methods
        to plot the periodic table are called."""
        super().__init__()
        " section 1: declaring constants and setting up the figure"
        self.figureStart = 0
        self.setWindowTitle('Interactive Periodic Table')
        self.dpi = 100
        self.screenWidth = 1920     # screen width in pixels
        self.screenHeight = 900     # screen height in pixels
        self.px = 1/self.dpi        # pixel in inches
        self.setGeometry(self.figureStart, self.figureStart, self.screenWidth//4, self.screenHeight//2)
        self.figure = plt.figure(figsize=(self.screenWidth * self.px, self.screenHeight * self.px), dpi=self.dpi)
        self.ax = self.figure.add_axes([0, 0, 1, 1])
        self.ax.set_axis_off()
        
        # this portion sets up the widget layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.infoLabel = QLabel('Click on an element for more details.')
        self.layout.addWidget(self.infoLabel)

        # design choices for the table appearance
        self.fontsizeLarge = 12
        self.textSpacing = 0.1
        self.fontsizeSmall = 7.5
        self.cellSizeReal = 0
        self.cellSize = 1    # unit cell size
        self.cellSpacing = 0.05
        self.cellSizeReal = self.cellSize - self.cellSpacing
        self.numColsFig = 20     # figure size is wider than the number of element columns
        self.numColsElem = 18
        self.gap = self.numColsFig-self.numColsElem
        # set of randomly chosen RGB alpha values for the colours
        self.colourSet = list(product([0, 1], [0.2, 0.7], [0.4, 0.9], [0.3, 0.8]))
        self.filename = 'periodicTable.csv'
        
        self.dictColour = {}
        self.atmNumLanStart = 56     # last atomic number before first lanthanide
        self.atmNumLanEnd = 72       # first atomic number after last lanthanide
        self.atmNumActStart = 88     # last atomic number before first actinide
        self.atmNumActEnd = 104      # last atomic number before last actinide
        self.elementsList = []
        self.indexatomicNum = 0
        self.indexElementName = 1
        self.indexElementSymbol = 2
        self.indexAtomicWeight = 3
        self.indexElementRow = 7
        self.indexElementColumn = 8
        self.indexElementType = 15
        self.indexElementDensity = 19
        self.indexDiscoverer = 23

        "section 2: calling the methods"
        self.process_data()
        self.process_legend()
        for element in self.elementsList:
            self.add_patches(element, case_="element")
        self.indexExample = 45  # index for example element plotted in the middle
        exampleElement = self.elementsList[self.indexExample]
        self.add_patches(exampleElement, case_="example")
        self.show()

    def process_data(self):
        """This method creates the elements list from a csv file,
         and initialises a dictionary with the different element types as keys."""
        count = 0
        columnCountLan = 4      # first column for lanthanides
        columnCountAct = 4      # first column for actinides

        with open(self.filename, newline='') as csvfile:
            elements = csv.reader(csvfile)
            for element in elements:
                if count > 0:   # skip the header
                    atomicNum = int(element[self.indexatomicNum])
                    
                    # Lanthanides and actinides are assigned row 
                    # and column numbers for later plotting in this section.
                    if (atomicNum > self.atmNumLanStart) and (atomicNum < self.atmNumLanEnd):
                        # 7 rows of elements + 1 row gap between 
                        # the elements and the lanthanides row
                        element[self.indexElementRow] = '9'
                        element[self.indexElementColumn] = str(columnCountLan)
                        columnCountLan += 1
                        
                    elif (atomicNum > self.atmNumActStart) and (atomicNum < self.atmNumActEnd):
                        # 7 rows of elements + 2 row gap between 
                        # the elements and the actinides row
                        element[self.indexElementRow] = '10'
                        element[self.indexElementColumn] = str(columnCountAct)
                        columnCountAct += 1
                    
                    # collect elements and their properties in a list
                    self.elementsList.append(element)
                    
                    # collate element types
                    self.dictColour[element[self.indexElementType]] = 0
                count += 1
                
    def process_legend(self):
        """This method assigns colour points to the different element types. This information is also plotted
        in a legend in the upper right corner of the figure."""
        legendGap = 0.75        # x-axis spacing of the legend. 0.75 separates the last element column from the legend
        columnLegend = self.numColsElem - legendGap        
        legendTextGap = 0.3     # x-axis spacing of the legend text. These numbers are based on personal preference
        columnText = columnLegend + legendTextGap  
        cellSizeLegend = 0.30
        cellSpacingLegend = 0.05
        numElementTypes = len(self.dictColour)

        colourCount = 0   
        for elementType in self.dictColour:
            if colourCount < numElementTypes:
                colourPoint = self.colourSet[colourCount]
                self.dictColour[elementType] = colourPoint
                
                # x- and y- coordinates for the legend
                # colourCount/3 because the legend boxes are 1/3 the size of the element boxes
                positionLegend = [columnLegend, -colourCount/3]
                
                # creating and adding patches for the legend
                boxes = Rectangle((positionLegend[0], positionLegend[1]), cellSizeLegend-cellSpacingLegend,
                                  -cellSizeLegend + cellSpacingLegend, fill=True, color=colourPoint)
                self.ax.add_patch(boxes)
                
                # legend description
                self.ax.text(columnText, positionLegend[1]-cellSizeLegend/2, elementType, horizontalalignment='left',
                             verticalalignment='center', fontsize=8.5)
                colourCount += 1           
            
    def add_patches(self, element, case_):
        """ This  method adds patches for each element to the plot. In the PyQT screen, buttons are added to an
        interactive periodic table."""
        elementType = element[self.indexElementType]
        atomicNum = int(element[self.indexatomicNum])
        colour = self.dictColour[elementType]
        symbol = element[self.indexElementSymbol]
        atomicWeight = element[self.indexAtomicWeight]
        name = element[self.indexElementName]
        cellSizeReal = self.cellSizeReal 
        elemCoords = [0, 0]  
        fontsizeLarge = self.fontsizeLarge
        textSpacing = self.textSpacing
        fontsizeSmall = self.fontsizeSmall 
        
        match case_:
            case "element":
                """ this case adds row anc column numbers to the plot. Asterisks for the lanthanides and actinides
                are added here. The x-, and y- coordinates for the element cells are calculated here."""
                
                # design choices for the table appearance
                rowNum = int(element[7])        
                colNum = int(element[8])
                atmNumFirstLan = 57

                # atomic numbers of elements in the first column and/ or first row
                atomicNumEdgeElemRow = [1, 3, 11, 19, 37, 55, 87]
                atomicNumEdgeElemColumn = [1, 4, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 5, 6, 7, 8, 9, 2]
                
                # x and y coordinates for the patches, and patch size
                elemCoords = [colNum-self.gap, -rowNum]

                # check for the start of transition metals so that asterisks are added to indicate their position.
                is_transition_metal = atomicNum == atmNumFirstLan
                if is_transition_metal:
                    self.is_transition_metal(elemCoords)

                # check for edge elements so that the row and column numbers are plotted
                isEdgeRowElement = atomicNum in atomicNumEdgeElemRow 
                isEdgeColElement = atomicNum in atomicNumEdgeElemColumn
                if isEdgeRowElement:
                    self.is_edge_element(atomicNumEdgeElemRow, atomicNumEdgeElemColumn, atomicNum, elemCoords, 0)
                if isEdgeColElement:
                    self.is_edge_element(atomicNumEdgeElemRow, atomicNumEdgeElemColumn, atomicNum, elemCoords, 1)

                self.add_buttons(symbol, atomicNum, element, rowNum, colNum)
        
            case "example":
                """this case plots an example element at a pre-determined location. This element describes the infor-
                mation that is presented in the periodic table."""
                # design choices for plotting the example element
                rowNum = 2.5
                colNum = 6
                lineLength = 0.9
                arrowGap = 1
                textGap = 2.55
                
                # font and cell sizes are 1.5x that of the regular elements
                textSpacing = self.textSpacing * 1.5
                fontsizeLarge = self.fontsizeLarge * 1.5
                fontsizeSmall = self. fontsizeSmall * 1.5 
                cellSize = self. cellSize * 1.5
                
                elemCoords = [colNum-self.gap, -rowNum]
                cellSizeReal = cellSize
                
                # plotting arrows and descriptions of the numbers in each cell
                arrow(elemCoords[0] + cellSizeReal + arrowGap,
                      elemCoords[1] + 0.5 * cellSizeReal, -lineLength, 0,
                      head_width=0.05, head_length=0.05, fc='k', ec='k')
                self.ax.text(elemCoords[0] + textGap, elemCoords[1] + 0.5 * cellSizeReal, 'Symbol',
                             horizontalalignment='left', verticalalignment='center', fontsize=fontsizeSmall)
    
                arrow(elemCoords[0] - arrowGap, elemCoords[1] + cellSizeReal - textSpacing, lineLength,
                      dy=0, head_width=0.05, head_length=0.05, fc='k', ec='k')
                self.ax.text(elemCoords[0] - textGap, elemCoords[1] + cellSizeReal - textSpacing,
                             'Atomic number', horizontalalignment='left', verticalalignment='center', fontsize=fontsizeSmall)
    
                arrow(elemCoords[0] + cellSizeReal + arrowGap, elemCoords[1] + 2.5 * textSpacing,
                      -lineLength, dy=0, head_width=0.05, head_length=0.05, fc='k', ec='k')
                self.ax.text(elemCoords[0] + textGap, elemCoords[1] + 2.5 * textSpacing, 'Atomic weight',
                             horizontalalignment='left', verticalalignment='center', fontsize=fontsizeSmall)
                
                arrow(elemCoords[0] + cellSizeReal + arrowGap, elemCoords[1] + textSpacing, -lineLength,
                      dy=0, head_width=0.05, head_length=0.05, fc='k', ec='k')
                self.ax.text(elemCoords[0] + textGap, elemCoords[1] + textSpacing, 'Element name',
                             horizontalalignment='left', verticalalignment='center', fontsize=fontsizeSmall)
        
        # adding the element patch to the plot        
        boxes = Rectangle((elemCoords[0], elemCoords[1]), cellSizeReal, cellSizeReal,
                          fill=True, color=colour)
        self.ax.add_patch(boxes)
        
        # including the element info (symbol, atomic number, name, and atomic weight)
        self.ax.text(elemCoords[0] + 0.5 * cellSizeReal, elemCoords[1] + 0.5 * cellSizeReal, symbol,
                     weight='bold', horizontalalignment='center', verticalalignment='center', fontsize=fontsizeLarge)
           
        self.ax.text(elemCoords[0] + textSpacing, elemCoords[1] + cellSizeReal - textSpacing, atomicNum,
                     horizontalalignment='left', verticalalignment='center', fontsize=fontsizeSmall)
           
        self.ax.text(elemCoords[0] + 0.5 * cellSizeReal, elemCoords[1] + 2.5 * textSpacing, atomicWeight,
                     horizontalalignment='center', verticalalignment='center', fontsize=fontsizeSmall)
           
        self.ax.text(elemCoords[0] + 0.5 * cellSizeReal, elemCoords[1] + textSpacing, name,
                     horizontalalignment='center', verticalalignment='center', fontsize=fontsizeSmall)

    def widget_text(self, element_):
        """This method decides the information displayed when the buttons are clicked"""
        symbol = element_[self.indexElementSymbol]
        name = element_[self.indexElementName]
        density = element_[self.indexElementDensity] 
        discoverer = element_[self.indexDiscoverer]
        if density == "":
            density = "unknown"
        else:
            density = density + ' g/cm^3'
        if discoverer == "":
            discoverer = "unknown"
        info = f"Name: {name}\nSymbol: {symbol}\nDensity: {density} \nDiscoverer: {discoverer}"
        self.infoLabel.setText(info)
        
    def add_buttons(self, symbol_, atomicNum_, element_, rowNum_, colNum_):
        """This method adds buttons to the interactive table."""
        button = QPushButton(f'{symbol_}\n{atomicNum_}')
        button.setStyleSheet("background-color: thistle; color: indigo;")
        button.clicked.connect(partial(self.widget_text, element_))  # specifying text to be displayed
        self.layout.addWidget(button, rowNum_ - 1, colNum_, 2, 1)  # positioning button

    def is_transition_metal(self, elemCoords_):
        """This method checks for the first transition metal and adds asterisks to indicate their position
        in the general periodic table."""
        lanthanideRowOG = 6
        actinideRowOG = 7
        # adding asterisks to identify the position of lanthanides and actinides 
        positionAsteriskLan1 = [elemCoords_[0] - 0.5 * self.cellSize, -lanthanideRowOG + 0.5 * self.cellSize]
        positionAsteriskAct1 = [elemCoords_[0] - 0.5 * self.cellSize, -actinideRowOG + 0.5 * self.cellSize]

        positionAsteriskLan2 = [elemCoords_[0] - self.cellSpacing, elemCoords_[1] + 0.5 * self.cellSize]
        positionAsteriskAct2 = [elemCoords_[0] - self.cellSpacing, elemCoords_[1] - 0.5 * self.cellSize]

        self.ax.text(positionAsteriskLan1[0], positionAsteriskLan1[1], '*', horizontalalignment='center',
                     verticalalignment='center', fontsize=self.fontsizeLarge)
        
        self.ax.text(positionAsteriskAct1[0], positionAsteriskAct1[1], '*\n*', horizontalalignment='center',
                     verticalalignment='center', fontsize=self.fontsizeLarge)

        self.ax.text(positionAsteriskLan2[0]-self.textSpacing, positionAsteriskLan2[1], '*',
                     horizontalalignment='center', verticalalignment='center', fontsize=self.fontsizeLarge)
        
        self.ax.text(positionAsteriskAct2[0]-self.textSpacing, positionAsteriskAct2[1], '*\n*',
                     horizontalalignment='center', verticalalignment='center', fontsize=self.fontsizeLarge)
        
    def is_edge_element(self, atomicNumEdgeElemRow_, atomicNumEdgeElemColumn_, atomicNum_, elemCoords_, case_):
        """This method checks whether an element is at the left or top edge so that the row and column
            information can be plotted"""
        match case_:
            case 0:
                row = str(atomicNumEdgeElemRow_.index(atomicNum_)+1)
                self.ax.text(elemCoords_[0] - self.cellSpacing - self.textSpacing, elemCoords_[1] + 0.5 * self.cellSize,
                             row, horizontalalignment='left', verticalalignment='center', fontsize=self.fontsizeSmall)
            case 1:
                # plotting the column numbers for elements in the top row
                col = str(atomicNumEdgeElemColumn_.index(atomicNum_)+1)
                self.ax.text(elemCoords_[0] + 0.5 * self.cellSizeReal, elemCoords_[1] + self.cellSize + self.textSpacing,
                             col, horizontalalignment='center', verticalalignment='center', fontsize=self.fontsizeSmall)
