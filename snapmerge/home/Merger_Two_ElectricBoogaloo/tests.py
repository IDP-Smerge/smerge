import unittest
from generator import create_xml_head, pretty_print_xml
import xml.etree.ElementTree as ET

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from merger import *


class TestMergeDoc(unittest.TestCase):
    # If both names and version are the same, it should return no collision and return the left
    def testCollision(self):
        projectName = "project"
        versionName = "Snap! 9.0, https://snap.berkeley.edu"
        xml1 = create_xml_head(projectName, versionName, asTree=True).getroot()
        xml2 = create_xml_head(projectName, versionName, asTree=True).getroot()
        conflict, merged = mergeDoc(xml1, xml2)
        self.assertEqual(conflict, None)
        self.assertEqual(merged, xml1)
        
        # If both names and version are the same, it should return no collision and return the left
    def testCollisionVersion(self):
        projectName = "project"
        versionName = "Snap! 9.0, https://snap.berkeley.edu"
        versionName2 = "Snap! 9.0.1, https://snap.berkeley.edu"
        xml1 = create_xml_head(projectName, versionName, asTree=True).getroot()
        xml2 = create_xml_head(projectName, versionName2, asTree=True).getroot()
        conflict, merged = mergeDoc(xml1, xml2)
        self.assertEqual(conflict, None)
        self.assertEqual(merged, xml2)
        
    def testConflict(self):
        projectName = "project"
        projectName2 = "project_false"
        versionName = "Snap! 9.0, https://snap.berkeley.edu"
        xml1 = create_xml_head(projectName, versionName, asTree=True).getroot()
        xml2 = create_xml_head(projectName2, versionName, asTree=True).getroot()
        conflict, merged = mergeDoc(xml1, xml2)
        self.assertEqual(str(conflict), "Conflict (Text): project <-> project_false")
        self.assertEqual(merged, xml1)
        
        
        
        
        
    # def setUp(self):
    # # Perform setup actions here, if needed

    # def tearDown(self):
    #     # Perform cleanup actions here, if needed

class TestAtomicMerge(unittest.TestCase):
    def testSame(self):
        tagLeft = ET.Element('project', {'name': "tmp", 'app': "123", 'version': '2'})
        tagRight = ET.Element('project', {'name': "tmp", 'app': "123", 'version': '2'})
        conflict, merged = atomicMerge(tagLeft, tagRight)
        self.assertEqual(conflict, None)
        self.assertEqual(merged, tagLeft)
        
    def testDifferentTag(self):
        tagLeft = ET.Element('project', {'name': "tmp", 'app': "123", 'version': '2'})
        tagRight = ET.Element('projects', {'name': "tmp", 'app': "123", 'version': '2'})
        conflict, merged = atomicMerge(tagLeft, tagRight)
        self.assertEqual(type(conflict), type(Conflict("","")))
        self.assertEqual(merged, None)
        
    def testDifferentAttribs(self):
        tagLeft = ET.Element('project', {'name': "tmp", 'app': "123", 'version': '2'})
        tagRight = ET.Element('project', {'name': "tmp", 'app': "123"})
        conflict, merged = atomicMerge(tagLeft, tagRight)
        self.assertEqual(type(conflict), type(Conflict("","")))
        self.assertEqual(merged, None)
        
    def testDifferentAttribValues(self):
        tagLeft = ET.Element('project', {'name': "tmp", 'app': "1"})
        tagRight = ET.Element('project', {'name': "tmp", 'app': "123"})
        conflict, merged = atomicMerge(tagLeft, tagRight)
        self.assertEqual(type(conflict), type(Conflict("","")))
        self.assertEqual(merged, None)

# to run
#python -m unittest tests.py

if __name__ == '__main__':
    unittest.main()