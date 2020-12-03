import os
import unittest
import logging
import vtk, qt, ctk, slicer, math
import numpy as np
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# BoneReconstructionPlanner
#

class BoneReconstructionPlanner(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "BoneReconstructionPlanner"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#BoneReconstructionPlanner">module documentation</a>.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
  """
  Add data sets to Sample Data module.
  """
  # It is always recommended to provide sample data for users to make it easy to try the module,
  # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

  import SampleData
  iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

  # To ensure that the source code repository remains small (can be downloaded and installed quickly)
  # it is recommended to store data sets that are larger than a few MB in a Github release.

  # BoneReconstructionPlanner1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='BoneReconstructionPlanner',
    sampleName='BoneReconstructionPlanner1',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'BoneReconstructionPlanner1.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    fileNames='BoneReconstructionPlanner1.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    # This node name will be used when the data set is loaded
    nodeNames='BoneReconstructionPlanner1'
  )

  # BoneReconstructionPlanner2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='BoneReconstructionPlanner',
    sampleName='BoneReconstructionPlanner2',
    thumbnailFileName=os.path.join(iconsPath, 'BoneReconstructionPlanner2.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
    fileNames='BoneReconstructionPlanner2.nrrd',
    checksums = 'SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
    # This node name will be used when the data set is loaded
    nodeNames='BoneReconstructionPlanner2'
  )

#
# BoneReconstructionPlannerWidget
#

class BoneReconstructionPlannerWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/BoneReconstructionPlanner.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)
    self.ui.fibulaLineSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.mandibularPlane1Selector.setMRMLScene(slicer.mrmlScene)
    self.ui.mandibularPlane2Selector.setMRMLScene(slicer.mrmlScene)

    #Setup the mandibular curve widget
    slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode","mandibuleCurve")
    curveNode = slicer.mrmlScene.GetFirstNodeByName("mandibuleCurve")
    self.ui.mandibularCurvePlaceWidget.setButtonsVisible(False)
    self.ui.mandibularCurvePlaceWidget.placeButton().show()
    self.ui.mandibularCurvePlaceWidget.setMRMLScene(slicer.mrmlScene)
    self.ui.mandibularCurvePlaceWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    self.ui.mandibularCurvePlaceWidget.setCurrentNode(curveNode)
    #self.ui.mandibularCurvePlaceWidget.connect('activeMarkupsFiducialPlaceModeChanged(bool)', self.addFiducials)
    #Setup the fibula line widget
    slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode","fibulaLine")
    lineNode = slicer.mrmlScene.GetFirstNodeByName("fibulaLine")
    self.ui.fibulaLinePlaceWidget.setButtonsVisible(False)
    self.ui.fibulaLinePlaceWidget.placeButton().show()
    self.ui.fibulaLinePlaceWidget.setMRMLScene(slicer.mrmlScene)
    self.ui.fibulaLinePlaceWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    self.ui.fibulaLinePlaceWidget.setCurrentNode(lineNode)
    #self.ui.fibulaLinePlaceWidget.connect('activeMarkupsFiducialPlaceModeChanged(bool)', self.addFiducials)
    #Setup the mandibular planes widget
    slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode","mandibularPlane")
    planeNode = slicer.mrmlScene.GetFirstNodeByName("mandibularPlane")
    self.ui.mandibularPlanesPlaceWidget.setButtonsVisible(False)
    self.ui.mandibularPlanesPlaceWidget.placeButton().show()
    self.ui.mandibularPlanesPlaceWidget.setMRMLScene(slicer.mrmlScene)
    self.ui.mandibularPlanesPlaceWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    self.ui.mandibularPlanesPlaceWidget.setCurrentNode(planeNode)
    #self.ui.mandibularPlanesPlaceWidget.connect('activeMarkupsFiducialPlaceModeChanged(bool)', self.addFiducials)



    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = BoneReconstructionPlannerLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.fibulaLineSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibularPlane1Selector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibularPlane2Selector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)


    # Buttons
    self.ui.createPlanesButton.connect('clicked(bool)', self.onCreatePlanesButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

    # Select default input nodes if nothing is selected yet to save a few clicks for the user
    if not self._parameterNode.GetNodeReference("InputVolume"):
      firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      if firstVolumeNode:
        self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    self.ui.fibulaLineSelector.setCurrentNode(self._parameterNode.GetNodeReference("fibulaLine"))
    self.ui.mandibularPlane1Selector.setCurrentNode(self._parameterNode.GetNodeReference("mandibularPlane1"))
    self.ui.mandibularPlane2Selector.setCurrentNode(self._parameterNode.GetNodeReference("mandibularPlane2"))

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("fibulaLine") and self._parameterNode.GetNodeReference("mandibularPlane1") and self._parameterNode.GetNodeReference("mandibularPlane2"):
      self.ui.createPlanesButton.toolTip = "Create fibula planes from mandibular planes"
      self.ui.createPlanesButton.enabled = True
    else:
      self.ui.createPlanesButton.toolTip = "Select fibula line and mandibular planes"
      self.ui.createPlanesButton.enabled = False

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    self._parameterNode.SetNodeReferenceID("fibulaLine", self.ui.fibulaLineSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibularPlane1", self.ui.mandibularPlane1Selector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibularPlane2", self.ui.mandibularPlane2Selector.currentNodeID)

    self._parameterNode.EndModify(wasModified)

  def onCreatePlanesButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:

      # Compute output
      self.logic.process(self.ui.fibulaLineSelector.currentNode(), self.ui.mandibularPlane1Selector.currentNode(),
        self.ui.mandibularPlane2Selector.currentNode())

    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# BoneReconstructionPlannerLogic
#

class BoneReconstructionPlannerLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "100.0")
    if not parameterNode.GetParameter("Invert"):
      parameterNode.SetParameter("Invert", "false")

  def process(self,fibulaLine,plane1,plane2):
    """
    This is a short test script to create two new planes over the fibula line
    with the same distance and angle between them as the original planes had
    """
    plane1Normal = [0,0,0]
    plane1.GetNormal(plane1Normal)
    plane2Normal = [0,0,0]
    plane2.GetNormal(plane2Normal)

    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    fibulaLine.GetNthControlPointPositionWorld(0, lineStartPos)
    fibulaLine.GetNthControlPointPositionWorld(1, lineEndPos)
    lineDirectionVector = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

    newPlane1 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane1")
    newPlane1.SetNormal(plane1Normal)
    newPlane1.SetOrigin(lineStartPos)
    newPlane2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane2")
    newPlane2.SetNormal(plane2Normal)
    newPlane2.SetOrigin(lineStartPos)


    rotAxis = [0,0,0]
    vtk.vtkMath.Cross(plane1Normal, lineDirectionVector, rotAxis)
    rotAxis = rotAxis/np.linalg.norm(rotAxis)
    angleRad = vtk.vtkMath.AngleBetweenVectors(plane1Normal, lineDirectionVector)
    angleDeg = vtk.vtkMath.DegreesFromRadians(angleRad)


    transformFid1 = slicer.vtkMRMLLinearTransformNode()
    transformFid1.SetName("Mandible2Fibula Transform1")
    slicer.mrmlScene.AddNode(transformFid1)
    transformFid2 = slicer.vtkMRMLLinearTransformNode()
    transformFid2.SetName("Mandible2Fibula Transform2")
    slicer.mrmlScene.AddNode(transformFid2)


    finalTransform1 = vtk.vtkTransform()
    finalTransform1.PostMultiply()
    finalTransform1.Translate(-lineStartPos[0], -lineStartPos[1], -lineStartPos[2])
    finalTransform1.RotateWXYZ(angleDeg,rotAxis)
    finalTransform1.Translate(lineStartPos)

    transformFid1.SetMatrixTransformToParent(finalTransform1.GetMatrix())
    transformFid1.UpdateScene(slicer.mrmlScene)


    or1 = [0,0,0]
    or2 = [0,0,0]
    plane1.GetOrigin(or1)
    plane2.GetOrigin(or2)
    d = np.sqrt(vtk.vtkMath.Distance2BetweenPoints(or1,or2))

    finalTransform2 = vtk.vtkTransform()
    finalTransform2.PostMultiply()
    finalTransform2.Translate(-lineStartPos[0], -lineStartPos[1], -lineStartPos[2])
    finalTransform2.RotateWXYZ(angleDeg,rotAxis)
    finalTransform2.Translate(lineStartPos)
    finalTransform2.Translate(d*lineDirectionVector)

    transformFid2.SetMatrixTransformToParent(finalTransform2.GetMatrix())

    transformFid2.UpdateScene(slicer.mrmlScene)

    newPlane1.SetAndObserveTransformNodeID(transformFid1.GetID())
    newPlane2.SetAndObserveTransformNodeID(transformFid2.GetID())









#
# BoneReconstructionPlannerTest
#

class BoneReconstructionPlannerTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_BoneReconstructionPlanner1()

  def test_BoneReconstructionPlanner1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # Get/create input data

    import SampleData
    registerSampleData()
    inputVolume = SampleData.downloadSample('BoneReconstructionPlanner1')
    self.delayDisplay('Loaded test data set')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 695)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 100

    # Test the module logic

    logic = BoneReconstructionPlannerLogic()

    # Test algorithm with non-inverted threshold
    logic.process(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.process(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')