from __future__ import absolute_import, division, print_function, unicode_literals
# This may help with Python 2/3 compatibility.

# The next line is intentionally blank.

__author__ = "Matthew Jefferson"
__version__ = "0.0.1"

# The previous line is intentionally blank.

"""
     Spirent TestCenter Conformance Test Application
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module provides a Python front-end for the Spirent TestCenter Conformance Test Application's Tcl API.
   
    Modification History:
    0.0.1 : 08/10/2021 - Matthew Jefferson
        -The initial code.

    :copyright: (c) 2021 by Matthew Jefferson.
"""
    
import sys
import os
import ast              # Used to convert strings to dict.
import datetime
import logging
import getpass
import inspect

if sys.hexversion >= 0x03000000:
   from tkinter import *
else:
   from Tkinter import *

#from shutil import copyfile     # Used for copying files.

class CtaPython:

    def __init__(self, api_path=None, log_path=None, log_level="DEBUG"):
        """
        Load the Conformance  API and initialize the Python environment.

        'api_path' optionally specifies the location of the Spirent TestCenter Conformance Test Application API installation.
        'log_path' optionally specifies the location where the logs are to be stored.

        Returns None.
        """

        # Construct the log path.            
        if log_path:
            self.log_path = log_path
        else:
            defaultlog_path = "~/Spirent/CTA/Logs/"

            now = datetime.datetime.now()
            defaultlog_path += now.strftime("%Y-%m-%d-%H-%M-%S")
            defaultlog_path += "_PID"
            defaultlog_path += str(os.getpid())
            defaultlog_path = os.path.expanduser(defaultlog_path)
            
            # The environment variable overwrites the default path.    
            self.log_path = os.getenv("CTA_LOG_OUTPUT_DIRECTORY", defaultlog_path)        

        self.log_path = os.path.abspath(self.log_path)
        self.logfile = os.path.join(self.log_path, "cta_python.log")        

        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        # NOTE: Consider limiting the number of log directories that are created.
        #       It would mean deleting older directories.

        #16/05/18 11:03:53.717 INFO  3078268608 - user.scripting       - stc::get automationoptions -suppressTclErrors
        #16/05/18 11:03:53.717 INFO  3078268608 - user.scripting       - return  false
        #2016-05-19 14:05:56,382 UserID   =mjefferson
        #2016-05-19 14:05:56,382 Log Level=INFO

        if log_level == "CRITICAL":
            log_level = logging.CRITICAL
        elif log_level == "ERROR":
            log_level = logging.ERROR
        elif log_level == "WARNING":
            log_level = logging.WARNING
        elif log_level == "INFO":            
            log_level = logging.INFO
        else:
            # DEBUG is the default log level.
            log_level = logging.DEBUG        
            
        logging.basicConfig(filename=self.logfile, filemode="w", level=log_level, format="%(asctime)s %(levelname)s %(message)s")
        #logging.Formatter(fmt='%(asctime)s.%(msecs)03d',datefmt='%Y/%m/%d %H:%M:%S')
        # Add timestamps to each log message.
        #logging.basicConfig()
        # The logger is now ready.        

        logging.info("Spirent TestCenter Conformance Application Python API is starting up...")
        logging.info("OS Type      = " + os.name)
        logging.info("API Path     = " + api_path)
        logging.info("UserID       = " + getpass.getuser())
        logging.info("Log Level    = " + logging.getLevelName(log_level))     
        logging.info("Current Path = " + os.path.abspath(os.getcwd()))   
        logging.info("Log Path     = " + self.log_path)

        # Instantiate the Tcl interpreter.
        self.tcl = Tcl()

        self.tcl.eval("lappend ::auto_path {" + api_path + "}")

        logging.info("Tcl Version  = " + self.tcl.eval("info patchlevel"))
        logging.info("Tcl ::auto_path = " + self.tcl.eval('set ::auto_path'))
        logging.info("Loading the Spirent TestCenter Conformance Application in the Tcl interpreter...")
        self.Exec("package require SpirentTestCenterConformance")

        return


    ###############################################################################
    ####
    ####    Public Methods
    ####
    ###############################################################################

    def config(self, objecthandle, **kwargs):
        """ 
        Description
            Updates the attribute of an object with a new value, if it meets the validation rules.

        Syntax
            cta.config objectHandle attrName=value [, [attrName=value] ...]
            cta.config objectHandle DANPath=value [, [DANPath=value] ...]
            cta.config DDNPath attrName=value [, [attrName=value] ...]
            cta.config DDNPath DANPath=value [, [DANPath=value] ...]            

        Comments
            The stc::config command modifies the value of one or more object attributes, if it meets 
            the validation rules. Note: If you attempt to modify an attribute for a read-only object,
            or a specified value does not meet the validation rules, the stc::config command raises 
            an exception.
            -When you modify object attributes, use attrName/value pairs. 
             For example: stc::config project1 -name Project1
            -You can use Direct Descendant Notation (DDN) to identify the object and Descendant 
             Attribute Notation (DAN) to identify the attribute. 
             For example:
                A DAN path is a dotted path name beginning with a sequence of one or more object types, 
                and ending with an attribute name. CTA Automation combines the handle (or the 
                DDNPath) with the DANPath to resolve the attribute reference. The path must identify 
                a valid sequence of objects in the CTA Automation data model hierarchy.
                  stc::config $project.test -name Test1
                  stc::config $project -userprofile.name SSLv3                    
             In both DDN and DAN paths, an object type name may have an index suffix (an integer in 
             parentheses) to reference one of multiple children of the same type.
             For more information about these notations, see Referencing Objects: Object Paths. 

        Return Value
            None. Errors are raised as exceptions, encoded as string values that describe the error condition.

        Example            
            cta.config("userprofile1", dnsRetries=10)
            cta.config("userprofile1", cifsng.cifsngDataRandomization=true)
            cta.config(project + ".test.userprofile", sipng.firstRTPPort=1026)
        """
        self.LogCommand()
        tclcode = 'stc::config ' + objecthandle + ' '

        for key in kwargs:
            #tclcode = tclcode + ' ' + '-' + key + ' "' + str(kwargs[key]) + '"'
            reg = re.compile("\[")
            if reg.match(str(kwargs[key])):
                # This is a Tcl command (eg: [NULL]).
                tclcode = tclcode + ' ' + '-' + key + " " + str(kwargs[key])
            else:
                tclcode = tclcode + ' ' + '-' + key + ' {' + str(kwargs[key]) + '}'

        result = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(result))                    
        return result

    #==============================================================================
    def get(self, objecthandle, *args):
        """
        Description:
            Returns the value(s) of one or more object attributes, or a set of 
            object handles.
            Returns a single value if a single attribute is specified, otherwise,
            a dictionary is returned.

        Syntax:
            cta.get handle [attributeName]
            cta.get handle [DANPath]
            cta.get DDNPath [attributeName]
            cta.get DDNPath [DANPath]
            cta.get handle | DDNPath [relationName]   

        Comments
            The cta.get command returns the value of one or more object attributes, or, 
            in the case of relation references, one or more object handles.
                -The handle identifies the object from which data will be retrieved. 
                 If you do not specify any attributes, CTA Automation returns the 
                 values for all attributes and all relations defined for the object.
                -attributeName identifies an attribute for the specified object.
                -The DANPath (Descendant Attribute Notation path) is a dotted path name 
                 beginning with a sequence of one or more relation names, and ending with 
                 an attribute name. A relation name may have an index suffix (an integer 
                 in parenthesis) to reference one of multiple children of the same type. 
                 CTA Automation combines the handle (or the DDNPath) with the DANPath 
                 to resolve the attribute reference. The path must identify a valid 
                 sequence of objects in the test hierarchy. For example:
                      cta.get(project, "test(1).name")
                -CTA Automation combines the object and attribute specifications to 
                 retrieve the value of the attribute for the first Test object child of the 
                 project.
                -The DDNPath (Direct Descendant Notation path) is a dotted path name sequence. 
                 The sequence begins with an object handle, followed by one or more relation 
                 names. The path must identify a valid sequence of objects in the data model 
                 hierarchy. CTA Automation returns data for the object identified by 
                 the last name in the sequence. For example:
                      cta.get("project1.test", "name")
                 In this case, CTA Automation returns the value of the name attribute 
                 for the first Test child of the specified Project object.
                -If there is more than one instance of a particular object type, as children
                 of the specified object, use an index notation. (In the example above, the 
                 index value 1 is implied.) CTA Automation assigns index values in the 
                 order of object creation. For example:
                      cta.get(project + ".test(2)")
            CTA Automation returns the attributes and all relations for the second
            Test object child of the specified Project object.
            When you use a relation reference with the get method, it provides access 
            to one or more objects connected to the object identified by a handle (or DDNPath). 
            Specify a name for the relation reference, using relationName. 
            For example:
                cta.get(project, "Tests")
            This method call returns the handle(s) for the Test child object(s) of the 
            Project object.

        Return Value
            When you retrieve one or more attributes, cta.get returns the single attribute 
            value or a dictionary. If you do not specify any attributes, the get method 
            can return either a single value or a dictionary.
            Errors are raised as exceptions, encoded as string values that describe the 
            error condition.

        Example
            cta.get(project, "path")
            cta.get(test, "netrworkprofile.tcpoptions.tcptimeout")
            cta.get(project + "userprofile(2)", "nfs.dataRandomization")
        """
        self.LogCommand()
        tclcode = "stc::get " + objecthandle

        for key in args:
            tclcode += " -" + key

        result = self.Exec(tclcode)

        # Determine if we need to return a dictionary or just the result of the command.
        if len(args) == 0:
            result = self.List2Dict(result)

        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def perform(self, command, **kwargs):
        """        
        Description
            Executes a custom command.

        Syntax
            cta.perform(<command>, [[<argument>], [...])
        Comments
            The cta.perform method executes a command. See the CTA Automation 
            Object Reference document (Spirent_TestCenter_Automation_Conf_Obj_Ref.pdf) 
            for a complete list of commands.

        Return Value
            Dictionary
            Errors are raised as exceptions, encoded as string values that describe the 
            error condition.

        Example       
            cta.perform("AttachPorts")
            cta.perform("CtsLoadTestParams", session=session, fileName=filename)
        """
        self.LogCommand()

        tclcode = "stc::perform " + command

        for key in kwargs:
            #tclcode = tclcode + " " + "-" + key + ' "' + str(kwargs[key]) + '"'
            tclcode = tclcode + " " + "-" + key + r" {" + str(kwargs[key]) + r"}"

        result = self.Exec(tclcode)
        result_dict = self.List2Dict(result)
        logging.debug(" - Python result  - " + str(result_dict))
        return result_dict

    #==============================================================================
    def connect(self, ipAddress):
        """
        Description
            Connects to the specified device.
        
        Syntax
            cta.connect(<ipAddress>)
        
        Comments
            After this command call is completed, the device will be added to the device 
            list under the PhysicalChassisManager object. If CTA Automation is already 
            connected to this device, then it gets the latest state from the device and returns 
            the existent handle.
        
        Return Value
            ?
        
        Example        
            cta.connect("10.72.55.80")
        """
        self.LogCommand()
        tclcode = "stc::connect " + ipAddress

        result = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def create(self, objecttype, under, **kwargs):
        """
        Description
            Creates a new object of the specified type, under the specified parent.

        Syntax
            cta.create(<objecttype>, [attr=<value>] ...])
        
        Comments
            The cta.create command creates one or more CTA Automation objects under the 
            specified parent object. When you call the create method, you specify the type(s) 
            of one or more objects to be created. You can specify:
                -An object type name (such as the Project object or the Test object). For example: 
                 cta.create("project", under="system1", name="Project1")
                -When you create an object, you must specify the handle of the parent object 
                 under which the new object is to be created.
                -When you create an object, you can also set the object attributes at the same 
                 time. To set attributes, specify one or more attribute name/value pairs.
                -If you specify attribute name/value pairs, together with an object type path, 
                 CTA Automation applies the attribute values to the object associated 
                 with the last name specified in the object type path.
                -You can specify a Descendant Attribute Notation (DAN) path as part of the attribute
                 reference. CTA Automation uses the specified object type to create the primary
                 object, and the DAN path to create any additional objects. For information about path 
                 name specification, see Object, Attribute, and Relation References.
        
        Return Value
            The cta.create command returns a unique string value that is the object handle 
            for the object specified in the method call. (The cta.create method returns only 
            the handle for the primaryobject that is created. To obtain the handles for any 
            descendent objects that are created, use the get method to retrieve the child objects.)
        
        Example        
            project = cta.create("project", under="system1", name="Project1")
            test = cta.create("tests", under=project, name="Test1", testType="deviceComplex")
            sp = cta.create("ServerProfiles", under=project, name="ServerProfile", applicationProtocol="HTTP", http.keepAlive="on")        
        """
        self.LogCommand()
        tclcode = "stc::create " + objecttype + " -under " + under

        for key in kwargs:
            tclcode = tclcode + " " + "-" + key + " " + str(kwargs[key])

        objecthandle = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(objecthandle))
        return objecthandle        

    #==============================================================================
    def delete(self, handle):
        """
        Description
            Deletes a node from the data model.

       Syntax
            cta.delete(<handle>)
            cta.delete(<DDNPath>)

        Comments
            Deletes the object identified by the objectHandle or DDNPath from the 
            data model. CTA Automation also deletes all descendants of the 
            specified object (if any).
        
        Return Value 
            None. 
            Errors are raised as exceptions, encoded as string values that 
            describe the error condition.
            
        Example            
            cta.delete(projectHandle)
        """
        self.LogCommand()
        tclcode = "stc::delete " + handle

        result = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def disconnect(self, ipAddress):
        """
        Description
            Disconnects from the specified device and removes it from the device 
            list under the PhysicalDevicesManager object.

        Syntax
            cta.disconnect(<ipAddress>)
    
        Comments
            Does nothing, if CTA Automation was not connected to specified device.
        
        Return Value
            None. Errors are raised as exceptions, encoded as string values that 
            describe the error condition.
    
        Example
            cta.disconnect("10.50.20.77")
        """
        self.LogCommand()
        tclcode = "stc::disconnect " + ipAddress
        result = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(result))
        return result


    #==============================================================================
    def release(self, location):
        """
        Description
            Releases the specified port.

        Syntax
            cta.release(<location>)
    
        Comments
            You can only release ports that you have reserved. For information about 
            port reservations, and the syntax for identifying ports, see the description 
            of the reserve function.
        
        Return Value
            None. Errors are raised as exceptions, encoded as string values that 
            describe the error condition.
            
        Example
            cta.release("10.50.70.82/1/1")
        """       
        self.LogCommand()     
        tclcode = "stc::release " + location

        result = self.Exec(tclcode)         
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def reserve(self, location):
        """
        Description
            Reserves the specified port.
        
        Syntax
            cta.reserve(<location>)

        Comments
            Reserves the specified port for the username that was specified/determined
            upon the cta.login command. You must be connected to the chassis (or appliance)
            before you can reserve ports. The port can only be reserved if it is available 
            (that is, if not disabled or reserved by another user). To force reserve a 
            port, use the cta.perform("reservePort") command.

        Return Value
            Handle to the PhysicalPort object.
            Errors are raised as exceptions, encoded as string values that describe 
            the error condition.
            
        Example
            cta.reserve("10.50.70.82/2/1")
        """
        self.LogCommand()
        tclcode = "stc::reserve " + location

        porthandle = self.Exec(tclcode)         
        logging.debug(" - Python result  - " + str(porthandle))
        return porthandle

    # #==============================================================================
    # def subscribe(self, side, viewAttributesList):
    #     """
    #     Description
    #         Subscribes to view the list of runtime statistics that users specify.
            
    #     Syntax
    #         cta.subscribe(<side>, <viewAttributesList>)
            
    #     Comments
    #         Subscribes to view runtime statistics for those that user specifies as 
    #         viewAttributesList. The attribute names should be one of the supported 
    #         statistics names, for example, http,successfulConns or http,attemptedConns. 
    #         Wildcards are also supported, such as http*. Please refer to Appendix A. 
    #         List of Runtime Statistics for full list of runtime statistics.
        
    #     Return Value
    #         Returns the handle to the ResultDataSet object, which consists of the 
    #         ResultDataObject with statistics values. By default, the returned 
    #         ResultDataSet will only contain the latest actual values. In order to 
    #         obtain the values from a specific point in time during the test run, user
    #         must add the 'all' keyword to the list of viewAttributesList. See Runtime 
    #         statistics for more information.

    #     Example            
    #         cta.subscribe("client", ["http,successfulConns", "http,attemptedConns"])
    #         cta.subscribe("server", "http*")
    #     """      
    #     self.LogCommand()
    #     tclcode = "stc::subscribe " + side + " [list " + " ".join(viewAttributesList) + "]"

    #     resultdataset = self.Exec(tclcode)         
    #     logging.debug(" - Python result  - " + str(resultdataset))
    #     return resultdataset

    # #==============================================================================
    # def unsubscribe(self, handle):
    #     """
    #     Description
    #         Removes a subscription for the specified ResultDataSet.
            
    #     Syntax
    #         cta.unsubscribe(<handle>)
            
    #     Comments
    #         The cta.unsubscribe command removes a subscription for the specified handle 
    #         of the ResultDataSet object that was returned by the subscribe function.
            
    #     Return Value
    #         None. Errors are raised as exceptions, encoded as string values that 
    #         describe the error condition.
            
    #    Example
    #         cta.unsubscribe(rdsHandle)
    #     """
    #     self.LogCommand()
    #     tclcode = "stc::unsubscribe " + handle

    #     result = self.Exec(tclcode)         
    #     logging.debug(" - Python result  - " + str(result))
    #     return result
    
    # #==============================================================================
    # def waitUntilDone(self):
    #     """
    #     Description
    #         Waits until the command specified by the request id is complete.
            
    #     Syntax
    #         cta.waitUntilCommandIsDone(<requestId>)
            
    #     Comments
    #         This function waits until the command, specified by request id, is out 
    #         of the PENDING state and completes its job. This is useful for asynchronous 
    #         commands. If the requestId is not specified, then it waits until any 
    #         command is completed.
            
    #     Return Value
    #         Result of an asynchronous command.
    #         Errors are raised as exceptions, encoded as string values that describe the error condition.
        
    #     Example
    #         cta.waitUntilCommandIsDone(cta.connect("10.50.70.82", executesynchronous=False))

    #         CAUTION: "cta.waitUntilCommandIsDone" will time out if the command it waits for does
    #         not complete in a certain time.        
    #     """
    #     self.LogCommand()
    #     tclcode = "stc::waitUntilCommandIsDone"


    #     # NOTE: Not yet tested!


    #     if requestId != "":
    #          tclcode += " " + requestId

    #     tclresult = self.Exec(tclcode)         
    #     logging.debug(" - Python result  - " + str(tclresult))
    #     return tclresult

    ###############################################################################
    ####
    ####    Private Methods
    ####
    ###############################################################################

    def Exec(self, command):
        logging.debug(" - Tcl command - " + command)
        
        try:
            result = self.tcl.eval(command)

        except Exception as errmsg:
            logging.error(errmsg)            
            raise
        
        logging.debug(" - Tcl result  - " + result)
        return result

    #==============================================================================
    def List2Dict(self, result):
        # Converts a Tcl list (which is a string) into a Python dictionary.       

        # Use Tcl to convert the list into a Python-friendly dict string.
        tclcode =  "proc isnumeric value {                           \n\
                        if {![catch {expr {abs($value)}}]} {         \n\
                            return 1                                 \n\
                        }                                            \n\
                        set value [string trimleft $value 0]         \n\
                        if {![catch {expr {abs($value)}}]} {         \n\
                            return 1                                 \n\
                        }                                            \n\
                        return 0                                     \n\
                    }                                                \n\
                    proc tclList2Dict { args } {                     \n\
                        set result $args                             \n\
                        set output {}                                \n\
                        foreach {key value} $result {                \n\
                            regsub {^-} $key {} key                  \n\
                            if { [isnumeric $value] } {              \n\
                                append output \"'$key': $value, \"   \n\
                            } else {                                 \n\
                                regsub -all {'} $value {\\'} value   \n\
                                regsub -all {\"} $value {\\\"} value \n\
                                append output \"'$key': '$value', \" \n\
                            }                                        \n\
                        }                                            \n\
                                                                     \n\
                        regsub {, $} $output {} output               \n\
                        set output [list $output]                    \n\
                        return $output                               \n\
                    }"

        # This eval instantiates the Tcl procedures.
        self.tcl.eval(tclcode)
        # This eval executes the Tcl procedure and returns the result.
        tclresult = self.tcl.eval("tclList2Dict " + result)

        # This command converts the Tcl string into a dict object.
        return ast.literal_eval(tclresult)

    #==============================================================================
    def LogCommand(self):
        """
        Log the calling method to the log, including its arguments.
        """        
        # Retrieve the args for the command.
        posname, kwname, args = inspect.getargvalues(inspect.stack()[1][0])[-3:]
        posargs = args.pop(posname, [])
        args.update(args.pop(kwname, []))

        methodname = inspect.currentframe().f_back.f_code.co_name       

        # Output the command in a format that looks like normal Python syntax.
        logmsg = " - Python command - " + methodname
        arguments = ""
        for key in args:            
            if key != "self":                
                value = args[key]
                if value == "":
                    value = '""'

                arguments += key + "=\"" + str(value) + "\", "

        if arguments != "":
            # Remove the final comma and space (", ").
            arguments = arguments[:-2]

        logmsg += "(" + arguments + ")"

        logging.debug(logmsg)
        return                

###############################################################################
####
####    Main
####
###############################################################################
