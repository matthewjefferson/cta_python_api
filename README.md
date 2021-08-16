# Spirent Conformance Test Application Python API

This Python module provides a Python interface to the Spirent TestCenter Conformance Application Tcl API.

Author: Mathew Jefferson (matt.jefferson@spirent.com)

Date: 08/10/2021

**Requirements:**    

    Python 2.7/3.x    
    Spirent TestCenter Conformance Application

**Required Python Modules:**

    Tkinter/tkinter
    sys
    os
    ast
    datetime
    logging
    getpass
    inspect

**Getting started:**
   
To instantiate the CtaPython object in your Python script, you need to provide the Spirent TestCenter Conformance Application installation path.

**Example:**
    
    import CtaPython
    api_path = "C:/Program Files (x86)/Spirent Communications/Spirent TestCenter 5.23/Conformance Application"        
    stc = CtaPython.CtaPython(api_path=api_path)



If you are using AION licensing, you will want to connect to the AION license server.

**Example:**
    
    stc.perform("TemevaSignInCommand", Server="https://spirent.spirentaion.com/", 
                                       username="jonnyboy", 
                                       password="secrets")


Before you load a test suite, you must connect to the chassis (for licensing):

**Example:**
    
    stc.connect("10.1.1.10")

    test_suite = stc.perform("CtsLoadTestSuite", testSuiteName="ELINE")
    session = test_suite["Session"]
