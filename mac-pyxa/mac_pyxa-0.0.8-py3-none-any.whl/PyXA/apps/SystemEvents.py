""".. versionadded:: 0.0.8

Control the macOS System Events application using JXA-like syntax.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Tuple, Union, List, Dict

from PyXA import XABase
from PyXA.XABase import OSType
from PyXA import XABaseScriptable
        

class XASystemEventsApplication(XABaseScriptable.XASBApplication):
    """A class for...
    """
    class SaveOption(Enum):
        """Options for what to do when calling a save event.
        """
        SAVE_FILE   = OSType('yes ') #: Save the file. 
        DONT_SAVE   = OSType('no  ') #: Do not save the file. 
        ASK         = OSType('ask ') #: Ask the user whether or not to save the file. 

    class DynamicStyle(Enum):
        """Options for the dynamic style of the desktop background.
        """
        AUTO    = OSType('atmt') #: automatic (if supported, follows light/dark appearance)
        DYNAMIC = OSType('dynm') #: dynamic (if supported, updates desktop picture based on time and/or location)
        LIGHT   = OSType('lite') #: light style
        DARK    = OSType('dark') #: dark style
        UNKNOWN    = OSType('unk\?') #: unknown style

    class DoubleClickBehavior(Enum):
        """Options for double click behaviors.
        """
        MINIMIZE    = OSType('ddmi') #: Minimize
        OFF         = OSType('ddof') #: Off
        ZOOM        = OSType('ddzo') #: Zoom

    class MinimizeEffect(Enum):
        """Options for the effect to use when minimizing applications.
        """
        GENIE   = OSType('geni') #: Genie effect
        SCALE   = OSType('scal') #: Scale effect

    class ScreenLocation(Enum):
        """Locations on the screen.
        """
        BOTTOM = OSType('bott') #: Bottom of screen
        LEFT   = OSType('left') #: Left side of screen
        RIGHT  = OSType('righ') #: Right side of screen

    def __init__(self, properties):
        super().__init__(properties)

        self.name: str #: The name of the application.
        self.frontmost: bool #: Is this the active application?
        self.version: str #: The version number of the application.
        self.quit_delay: int #: the time in seconds the application will idle before quitting; if set to zero, idle time will not cause the application to quit
        self.script_menu_enabled: bool #: Is the Script menu installed in the menu bar?
        # self.current_user: XASystemEventsUser #: the currently logged in user
        # self.appearance_preferences: XASystemEventsAppearancePreferencesObject #: a collection of appearance preferences
        # self.cd_and_dvd_preferences: XASystemEventsCDAndDVDPreferencesObject #: the preferences for the current user when a CD or DVD is inserted
        # self.current_desktop: XASystemEventsDesktop #: the primary desktop
        # self.dock_preferences: XASystemEventsDockPreferencesObject #: the preferences for the current user's dock
        # self.network_preferences: XASystemEventsNetworkPreferencesObject #: the preferences for the current user's network
        # self.current_screen_saver: XASystemEventsScreenSaver #: the currently selected screen saver
        # self.screen_saver_preferences: XASystemEventsScreenSaverPreferencesObject #: the preferences common to all screen savers
        # self.security_preferences: XASystemEventsSecurityPreferencesObject #: a collection of security preferences
        # self.application_support_folder: XASystemEventsFolder #: The Application Support folder
        # self.applications_folder: XASystemEventsFolder #: The user's Applications folder
        # self.classic_domain: XASystemEventsClassicDomainObject #: the collection of folders belonging to the Classic System
        # self.desktop_folder: XASystemEventsFolder #: The user's Desktop folder
        # self.desktop_pictures_folder: XASystemEventsFolder #: The Desktop Pictures folder
        # self.documents_folder: XASystemEventsFolder #: The user's Documents folder
        # self.downloads_folder: XASystemEventsFolder #: The user's Downloads folder
        # self.favorites_folder: XASystemEventsFolder #: The user's Favorites folder
        # self.folder_action_scripts_folder: XASystemEventsFolder #: The user's Folder Action Scripts folder
        # self.fonts_folder: XASystemEventsFolder #: The Fonts folder
        # self.home_folder: XASystemEventsFolder #: The Home folder of the currently logged in user
        # self.library_folder: XASystemEventsFolder #: The Library folder
        # self.local_domain: XASystemEventsLocalDomainObject #: the collection of folders residing on the Local machine
        # self.movies_folder: XASystemEventsFolder #: The user's Movies folder
        # self.music_folder: XASystemEventsFolder #: The user's Music folder
        # self.network_domain: XASystemEventsNetworkDomainObject #: the collection of folders residing on the Network
        # self.pictures_folder: XASystemEventsFolder #: The user's Pictures folder
        # self.preferences_folder: XASystemEventsFolder #: The user's Preferences folder
        # self.public_folder: XASystemEventsFolder #: The user's Public folder
        # self.scripting_additions_folder: XASystemEventsFolder #: The Scripting Additions folder
        # self.scripts_folder: XASystemEventsFolder #: The user's Scripts folder
        # self.shared_documents_folder: XASystemEventsFolder #: The Shared Documents folder
        # self.sites_folder: XASystemEventsFolder #: The user's Sites folder
        # self.speakable_items_folder: XASystemEventsFolder #: The Speakable Items folder
        # self.startup_disk: XASystemEventsDisk #: the disk from which Mac OS X was loaded
        # self.system_domain: XASystemEventsSystemDomainObject #: the collection of folders belonging to the System
        # self.temporary_items_folder: XASystemEventsFolder #: The Temporary Items folder
        # self.trash: XASystemEventsFolder #: The user's Trash folder
        # self.user_domain: XASystemEventsUserDomainObject #: the collection of folders belonging to the User
        # self.utilities_folder: XASystemEventsFolder #: The Utilities folder
        # self.workflows_folder: XASystemEventsFolder #: The Automator Workflows folder
        # self.folder_actions_enabled: bool #: Are Folder Actions currently being processed?
        # self.ui_elements_enabled: bool #: Are UI element events currently being processed?
        self.scripting_definition: XASystemEventsScriptingDefinitionObject #: The scripting definition of the System Events application

    # @property
    # def name(self) -> str:
    #     return self.xa_elem.name()

    # @property
    # def frontmost(self) -> bool:
    #     return self.xa_elem.frontmost()

    # @property
    # def version(self) -> str:
    #     return self.xa_elem.version()

    # @property
    # def quit_delay(self) -> int:
    #     return self.xa_elem.quitDelay()

    # @property
    # def script_menu_enabled(self) -> bool:
    #     return self.xa_elem.scriptMenuEnabled()

    # @property
    # def current_user(self) -> XASystemEventsUser:
    #     return self.xa_elem.currentUser()

    # @property
    # def appearance_preferences(self) -> XASystemEventsAppearancePreferencesObject:
    #     return self.xa_elem.appearancePreferences()

    # @property
    # def cd_and_dvd_preferences(self) -> XASystemEventsCDAndDVDPreferencesObject:
    #     return self.xa_elem.CDAndDVDPreferences()

    # @property
    # def current_desktop(self) -> XASystemEventsDesktop:
    #     return self.xa_elem.currentDesktop()

    # @property
    # def dock_preferences(self) -> XASystemEventsDockPreferencesObject:
    #     return self.xa_elem.dockPreferences()

    # @property
    # def network_preferences(self) -> XASystemEventsNetworkPreferencesObject:
    #     return self.xa_elem.networkPreferences()

    # @property
    # def current_screen_saver(self) -> XASystemEventsScreenSaver:
    #     return self.xa_elem.currentScreenSaver()

    # @property
    # def screen_saver_preferences(self) -> XASystemEventsScreenSaverPreferencesObject:
    #     return self.xa_elem.screenSaverPreferences()

    # @property
    # def security_preferences(self) -> XASystemEventsSecurityPreferencesObject:
    #     return self.xa_elem.securityPreferences()

    # @property
    # def application_support_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.applicationSupportFolder()

    # @property
    # def applications_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.applicationsFolder()

    # @property
    # def classic_domain(self) -> XASystemEventsClassicDomainObject:
    #     return self.xa_elem.ClassicDomain()

    # @property
    # def desktop_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.desktopFolder()

    # @property
    # def desktop_pictures_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.desktopPicturesFolder()

    # @property
    # def documents_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.documentsFolder()

    # @property
    # def downloads_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.downloadsFolder()

    # @property
    # def favorites_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.favoritesFolder()

    # @property
    # def folder_action_scripts_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.FolderActionScriptsFolder()

    # @property
    # def fonts_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.fontsFolder()

    # @property
    # def home_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.homeFolder()

    # @property
    # def library_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.libraryFolder()

    # @property
    # def local_domain(self) -> XASystemEventsLocalDomainObject:
    #     return self.xa_elem.localDomain()

    # @property
    # def movies_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.moviesFolder()

    # @property
    # def music_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.musicFolder()

    # @property
    # def network_domain(self) -> XASystemEventsNetworkDomainObject:
    #     return self.xa_elem.networkDomain()

    # @property
    # def pictures_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.picturesFolder()

    # @property
    # def preferences_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.preferencesFolder()

    # @property
    # def public_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.publicFolder()

    # @property
    # def scripting_additions_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.scriptingAdditionsFolder()

    # @property
    # def scripts_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.scriptsFolder()

    # @property
    # def shared_documents_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.sharedDocumentsFolder()

    # @property
    # def sites_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.sitesFolder()

    # @property
    # def speakable_items_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.speakableItemsFolder()

    # @property
    # def startup_disk(self) -> XASystemEventsDisk:
    #     return self.xa_elem.startupDisk()

    # @property
    # def system_domain(self) -> XASystemEventsSystemDomainObject:
    #     return self.xa_elem.systemDomain()

    # @property
    # def temporary_items_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.temporaryItemsFolder()

    # @property
    # def trash(self) -> XASystemEventsFolder:
    #     return self.xa_elem.trash()

    # @property
    # def user_domain(self) -> XASystemEventsUserDomainObject:
    #     return self.xa_elem.userDomain()

    # @property
    # def utilities_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.utilitiesFolder()

    # @property
    # def workflows_folder(self) -> XASystemEventsFolder:
    #     return self.xa_elem.workflowsFolder()

    # @property
    # def folder_actions_enabled(self) -> bool:
    #     return self.xa_elem.folderActionsEnabled()

    # @property
    # def ui_elements_enabled(self) -> bool:
    #     return self.xa_elem.UIElementsEnabled()

    @property
    def scripting_definition(self) -> 'XASystemEventsScriptingDefinitionObject':
        return self._new_element(self.xa_scel.scriptingDefinition(), XASystemEventsScriptingDefinitionObject)

    def log_out(self):
        """Logs out the current user.

        .. versionadded:: 0.0.8
        """
        self.xa_scel.logOut()

    def restart(self, state_saving_preference: bool = False):
        """Restarts the computer.

        :param state_saving_preference: Whether the user defined state saving preference is followed, defaults to False (always saved)
        :type state_saving_preference: bool, optional

        .. versionadded:: 0.0.8
        """
        self.xa_scel.restartStateSavingPreference_(state_saving_preference)

    def shut_down(self, state_saving_preference: bool = False):
        """Shuts down the computer.

        :param state_saving_preference: Whether the user defined state saving preference is followed, defaults to False (always saved)
        :type state_saving_preference: bool, optional

        .. versionadded:: 0.0.8
        """
        self.xa_scel.shutDownStateSavingPreference_(state_saving_preference)

    def sleep(self):
        """Puts the computer to sleep.

        .. versionadded:: 0.0.8
        """
        self.xa_scel.sleep()



    def login_items(self, filter: dict = None) -> Union['XASystemEventsLoginItemList', None]:
        """Returns a list of login items, as PyXA-wrapped objects, matching the given filter.

        :param filter: A dictionary specifying property-value pairs that all returned login items will have, or None
        :type filter: Union[dict, None]
        :return: The list of login items
        :rtype: XASystemEventsLoginItemList

        .. versionadded:: 0.0.8
        """
        return self._new_element(self.xa_scel.loginItems(), XASystemEventsLoginItemList, filter)




    def property_list_files(self, filter: dict = None) -> Union['XASystemEventsPropertyListFileList', None]:
        """Returns a list of property list files, as PyXA-wrapped objects, matching the given filter.

        :param filter: A dictionary specifying property-value pairs that all returned property list files will have, or None
        :type filter: Union[dict, None]
        :return: The list of property list files
        :rtype: XASystemEventsPropertyListFileList

        .. versionadded:: 0.0.8
        """
        return self._new_element(self.xa_scel.propertyListFiles(), XASystemEventsPropertyListFileList, filter)

    def property_list_items(self, filter: dict = None) -> Union['XASystemEventsPropertyListItemList', None]:
        """Returns a list of property list items, as PyXA-wrapped objects, matching the given filter.

        :param filter: A dictionary specifying property-value pairs that all returned property list items will have, or None
        :type filter: Union[dict, None]
        :return: The list of property list items
        :rtype: XASystemEventsPropertyListItemList

        .. versionadded:: 0.0.8
        """
        return self._new_element(self.xa_scel.propertyListItems(), XASystemEventsPropertyListItemList, filter)

    def make(self, specifier: str, properties: dict):
        """Creates a new element of the given specifier class without adding it to any list.

        Use :func:`XABase.XAList.push` to push the element onto a list.

        :param specifier: The classname of the object to create
        :type specifier: str
        :param properties: The properties to give the object
        :type properties: dict
        :return: A PyXA wrapped form of the object
        :rtype: XABase.XAObject

        .. versionadded:: 0.0.8
        """
        specifier_map = {
            "login item": "login item"
        }
        specifier = specifier_map.get(specifier) or specifier

        obj = self.xa_scel.classForScriptingClass_(specifier).alloc().initWithProperties_(properties)

        if specifier == "login item":
            return self._new_element(obj, XASystemEventsLoginItem)

# class XASystemEventsDocument(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.name: str #: Its name.
#         self.modified: bool #: Has it been modified since the last save?
#         self.file: XASystemEventsFile #: Its location on disk, if it has one.

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def modified(self) -> bool:
#         return self.xa_elem.modified()

#     @property
#     def file(self) -> XASystemEventsFile:
#         return self.xa_elem.file()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsWindow(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.accessibilityDescription: XAid #: a more complete description of the window and its capabilities
#         self.objectDescription: XAid #: the accessibility description, if available; otherwise, the role description
#         self.enabled: XAid #: Is the window enabled? ( Does it accept clicks? )
#         self.//: XANSArray<SBObject #: a list of every UI element contained in this window and its child UI elements, to the limits of the tree
#         self.focused: XAid #: Is the focus on this window?
#         self.help: XAid #: an elaborate description of the window and its capabilities
#         self.maximumValue: XAid #: the maximum value that the UI element can take on
#         self.minimumValue: XAid #: the minimum value that the UI element can take on
#         self.name: str #: the name of the window, which identifies it within its container
#         self.orientation: XAid #: the orientation of the window
#         self.position: XAid #: the position of the window
#         self.role: str #: an encoded description of the window and its capabilities
#         self.roleDescription: str #: a more complete description of the window's role
#         self.selected: XAid #: Is the window selected?
#         self.size: XAid #: the size of the window
#         self.subrole: XAid #: an encoded description of the window and its capabilities
#         self.title: str #: the title of the window as it appears on the screen
#         self.value: XAid #: the current value of the window

#     @property
#     def accessibilityDescription(self) -> XAid:
#         return self.xa_elem.accessibilityDescription()

#     @property
#     def objectDescription(self) -> XAid:
#         return self.xa_elem.objectDescription()

#     @property
#     def enabled(self) -> XAid:
#         return self.xa_elem.enabled()

#     @property
#     def //(self) -> XANSArray<SBObject:
#         return self.xa_elem.//()

#     @property
#     def focused(self) -> XAid:
#         return self.xa_elem.focused()

#     @property
#     def help(self) -> XAid:
#         return self.xa_elem.help()

#     @property
#     def maximumValue(self) -> XAid:
#         return self.xa_elem.maximumValue()

#     @property
#     def minimumValue(self) -> XAid:
#         return self.xa_elem.minimumValue()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def orientation(self) -> XAid:
#         return self.xa_elem.orientation()

#     @property
#     def position(self) -> XAid:
#         return self.xa_elem.position()

#     @property
#     def role(self) -> str:
#         return self.xa_elem.role()

#     @property
#     def roleDescription(self) -> str:
#         return self.xa_elem.roleDescription()

#     @property
#     def selected(self) -> XAid:
#         return self.xa_elem.selected()

#     @property
#     def size(self) -> XAid:
#         return self.xa_elem.size()

#     @property
#     def subrole(self) -> XAid:
#         return self.xa_elem.subrole()

#     @property
#     def title(self) -> str:
#         return self.xa_elem.title()

#     @property
#     def value(self) -> XAid:
#         return self.xa_elem.value()




class XASystemEventsUser(XABase.XAObject):
    """A user of the system.

    .. versionadded:: 0.0.8
    """
    def __init__(self, properties):
        super().__init__(properties)
        
        self.full_name: str #: user's full name
        self.home_directory: XABase.XAPath #: path to user's home directory
        self.name: str #: user's short name
        self.picture_path: XABase.XAPath #: path to user's picture. Can be set for current user only!

    @property
    def full_name(self) -> str:
        return self.xa_elem.fullName()

    @property
    def home_directory(self) -> XAid:
        return XABase.XAPath(self.xa_elem.homeDirectory())

    @property
    def name(self) -> str:
        return self.xa_elem.name()

    @property
    def picture_path(self) -> XAid:
        return XABase.XAPath(self.xa_elem.picturePath())


    

# class XASystemEventsAppearancePreferencesObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.appearance: XASystemEventsAppearances #: the overall look of buttons, menus and windows
#         self.fontSmoothing: bool #: Is font smoothing on?
#         self.fontSmoothingStyle: XASystemEventsFontSmoothingStyles #: the method used for smoothing fonts
#         self.highlightColor: XAid #: color used for hightlighting selected text and lists
#         self.recentApplicationsLimit: int #: the number of recent applications to track
#         self.recentDocumentsLimit: int #: the number of recent documents to track
#         self.recentServersLimit: int #: the number of recent servers to track
#         self.scrollBarAction: XASystemEventsScrollPageBehaviors #: the action performed by clicking the scroll bar
#         self.smoothScrolling: bool #: Is smooth scrolling used?
#         self.darkMode: bool #: use dark menu bar and dock

#     @property
#     def appearance(self) -> XASystemEventsAppearances:
#         return self.xa_elem.appearance()

#     @property
#     def fontSmoothing(self) -> bool:
#         return self.xa_elem.fontSmoothing()

#     @property
#     def fontSmoothingStyle(self) -> XASystemEventsFontSmoothingStyles:
#         return self.xa_elem.fontSmoothingStyle()

#     @property
#     def highlightColor(self) -> XAid:
#         return self.xa_elem.highlightColor()

#     @property
#     def recentApplicationsLimit(self) -> int:
#         return self.xa_elem.recentApplicationsLimit()

#     @property
#     def recentDocumentsLimit(self) -> int:
#         return self.xa_elem.recentDocumentsLimit()

#     @property
#     def recentServersLimit(self) -> int:
#         return self.xa_elem.recentServersLimit()

#     @property
#     def scrollBarAction(self) -> XASystemEventsScrollPageBehaviors:
#         return self.xa_elem.scrollBarAction()

#     @property
#     def smoothScrolling(self) -> bool:
#         return self.xa_elem.smoothScrolling()

#     @property
#     def darkMode(self) -> bool:
#         return self.xa_elem.darkMode()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsCDAndDVDPreferencesObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.blankCD: XASystemEventsInsertionPreference #: the blank CD insertion preference
#         self.blankDVD: XASystemEventsInsertionPreference #: the blank DVD insertion preference
#         self.blankBD: XASystemEventsInsertionPreference #: the blank BD insertion preference
#         self.musicCD: XASystemEventsInsertionPreference #: the music CD insertion preference
#         self.pictureCD: XASystemEventsInsertionPreference #: the picture CD insertion preference
#         self.videoDVD: XASystemEventsInsertionPreference #: the video DVD insertion preference
#         self.videoBD: XASystemEventsInsertionPreference #: the video BD insertion preference

#     @property
#     def blankCD(self) -> XASystemEventsInsertionPreference:
#         return self.xa_elem.blankCD()

#     @property
#     def blankDVD(self) -> XASystemEventsInsertionPreference:
#         return self.xa_elem.blankDVD()

#     @property
#     def blankBD(self) -> XASystemEventsInsertionPreference:
#         return self.xa_elem.blankBD()

#     @property
#     def musicCD(self) -> XASystemEventsInsertionPreference:
#         return self.xa_elem.musicCD()

#     @property
#     def pictureCD(self) -> XASystemEventsInsertionPreference:
#         return self.xa_elem.pictureCD()

#     @property
#     def videoDVD(self) -> XASystemEventsInsertionPreference:
#         return self.xa_elem.videoDVD()

#     @property
#     def videoBD(self) -> XASystemEventsInsertionPreference:
#         return self.xa_elem.videoBD()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsInsertionPreference(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.customApplication: XAid #: application to launch or activate on the insertion of media
#         self.customScript: XAid #: AppleScript to launch or activate on the insertion of media
#         self.insertionAction: XASystemEventsDhac #: action to perform on media insertion

#     @property
#     def customApplication(self) -> XAid:
#         return self.xa_elem.customApplication()

#     @property
#     def customScript(self) -> XAid:
#         return self.xa_elem.customScript()

#     @property
#     def insertionAction(self) -> XASystemEventsDhac:
#         return self.xa_elem.insertionAction()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    



class XASystemEventsDesktop(XABase.XAObject):
    """The current user's desktop.

    .. versionadded:: 0.0.8
    """
    def __init__(self, properties):
        super().__init__(properties)
        
        self.name: str #: name of the desktop
        self.id: int #: unique identifier of the desktop
        self.change_interval: float #: number of seconds to wait between changing the desktop picture
        self.display_name: str #: name of display on which this desktop appears
        self.picture: XABase.XAPath #: path to file used as desktop picture
        self.picture_rotation: int #: never, using interval, using login, after sleep
        self.pictures_folder: XABase.XAPath #: path to folder containing pictures for changing desktop background
        self.random_order: bool #: turn on for random ordering of changing desktop pictures
        self.translucent_menu_bar: bool #: indicates whether the menu bar is translucent
        self.dynamic_style: XASystemEventsApplication.DynamicStyle #: desktop picture dynamic style

    @property
    def name(self) -> str:
        return self.xa_elem.name()

    @property
    def id(self) -> int:
        return self.xa_elem.id()

    @property
    def change_interval(self) -> float:
        return self.xa_elem.changeInterval()

    @property
    def display_name(self) -> str:
        return self.xa_elem.displayName()

    @property
    def picture(self) -> XABase.XAPath:
        return XABase.XAPath(self.xa_elem.picture())

    @property
    def picture_rotation(self) -> int:
        return self.xa_elem.pictureRotation()

    @property
    def pictures_folder(self) -> XABase.XAPath:
        return XABase.XAPath(self.xa_elem.picturesFolder())

    @property
    def random_order(self) -> bool:
        return self.xa_elem.randomOrder()

    @property
    def translucent_menu_bar(self) -> bool:
        return self.xa_elem.translucentMenuBar()

    @property
    def dynamic_style(self) -> XASystemEventsApplication.DynamicStyle:
        # TODO - check
        return XASystemEventsApplication.DynamicStyle(XABase.OSType(self.xa_elem.dynamicStyle().stringValue()))
    



class XASystemEventsDockPreferencesObject(XABase.XAObject):
    """The current user's dock preferences.

    .. versionadded:: 0.0.8
    """
    def __init__(self, properties):
        super().__init__(properties)
        
        self.animate: bool #: is the animation of opening applications on or off?
        self.autohide: bool #: is autohiding the dock on or off?
        self.dock_size: float #: size/height of the items (between 0.0 (minimum) and 1.0 (maximum))
        self.autohide_menu_bar: bool #: is autohiding the menu bar on or off?
        self.double_click_behavior: XASystemEventsApplication.DoubleClickBehavior #: behaviour when double clicking window a title bar
        self.magnification: bool #: is magnification on or off?
        self.magnification_size: float #: maximum magnification size when magnification is on (between 0.0 (minimum) and 1.0 (maximum))
        self.minimize_effect: XASystemEventsApplication.MinimizeEffect #: minimization effect
        self.minimize_into_application: bool #: minimize window into its application?
        self.screen_edge: XASystemEventsApplication.ScreenLocation #: location on screen
        self.show_indicators: bool #: show indicators for open applications?
        self.show_recents: bool #: show recent applications?

    @property
    def animate(self) -> bool:
        return self.xa_elem.animate()

    @property
    def autohide(self) -> bool:
        return self.xa_elem.autohide()

    @property
    def dock_size(self) -> float:
        return self.xa_elem.dockSize()

    @property
    def autohide_menu_bar(self) -> bool:
        return self.xa_elem.autohideMenuBar()

    @property
    def double_click_behavior(self) -> XASystemEventsApplication.DoubleClickBehavior:
        # TODO - check
        return XASystemEventsApplication.DoubleClickBehavior(XABase.OSType(self.xa_elem.doubleClickBehavior().stringValue()))

    @property
    def magnification(self) -> bool:
        return self.xa_elem.magnification()

    @property
    def magnification_size(self) -> float:
        return self.xa_elem.magnificationSize()

    @property
    def minimize_effect(self) -> XASystemEventsApplication.MinimizeEffect:
        # TODO - check
        return XASystemEventsApplication.MinimizeEffect(XABase.OSType(self.xa_elem.minimizeEffect().stringValue()))

    @property
    def minimize_into_application(self) -> bool:
        return self.xa_elem.minimizeIntoApplication()

    @property
    def screen_edge(self) -> XASystemEventsApplication.ScreenLocation:
        # TODO - check
        return XASystemEventsApplication.ScreenLocation(XABase.OSType(self.xa_elem.screenEdge().stringValue()))

    @property
    def show_indicators(self) -> bool:
        return self.xa_elem.showIndicators()

    @property
    def show_recents(self) -> bool:
        return self.xa_elem.showRecents()




class XASystemEventsLoginItemList(XABase.XAList):
    """A wrapper around lists of login items that employs fast enumeration techniques.

    All properties of property login items can be called as methods on the wrapped list, returning a list containing each login item's value for the property.

    .. versionadded:: 0.0.8
    """
    def __init__(self, properties: dict, filter: Union[dict, None] = None):
        super().__init__(properties, XASystemEventsLoginItem, filter)

    def hidden(self) -> List[bool]:
        """Gets the hidden status of each item in the list.

        :return: A list of property list hidden statuses
        :rtype: List[bool]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("contents"))

    def kind(self) -> List[str]:
        """Gets the kind of each item in the list.

        :return: A list of property list kinds
        :rtype: List[str]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("kind"))

    def name(self) -> List[str]:
        """Gets the name of each item in the list.

        :return: A list of property list names
        :rtype: List[str]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("name"))

    def path(self) -> List[str]:
        """Gets the path of each item in the list.

        :return: A list of property list paths
        :rtype: List[str]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("path"))
        
    def by_hidden(self, hidden: bool) -> Union['XASystemEventsLoginItem', None]:
        """Retrieves the first login item whose hidden status matches the given boolean value, if one exists.

        :return: The desired login item, if it is found
        :rtype: Union[XASystemEventsLoginItem, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("hidden", hidden)

    def by_kind(self, kind: str) -> Union['XASystemEventsLoginItem', None]:
        """Retrieves the first login item whose kind matches the given kind, if one exists.

        :return: The desired login item, if it is found
        :rtype: Union[XASystemEventsLoginItem, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("kind", kind)

    def by_name(self, name: str) -> Union['XASystemEventsLoginItem', None]:
        """Retrieves the first login item whose name matches the given name, if one exists.

        :return: The desired login item, if it is found
        :rtype: Union[XASystemEventsLoginItem, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("name", name)

    def by_path(self, path: str) -> Union['XASystemEventsLoginItem', None]:
        """Retrieves the first login item whose path matches the given path, if one exists.

        :return: The desired login item, if it is found
        :rtype: Union[XASystemEventsLoginItem, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("path", path)

    def __repr__(self):
        return "<" + str(type(self)) + str(self.name()) + ">"

class XASystemEventsLoginItem(XABase.XAObject):
    """An item to be launched or opened at login.add()
    
    .. versionadded:: 0.0.8
    """
    def __init__(self, properties):
        super().__init__(properties)
        
        self.hidden: bool #: Is the Login Item hidden when launched?
        self.kind: str #: the file type of the Login Item
        self.name: str #: the name of the Login Item
        self.path: str #: the file system path to the Login Item

    @property
    def hidden(self) -> bool:
        return self.xa_elem.hidden()

    @property
    def kind(self) -> str:
        return self.xa_elem.kind()

    @property
    def name(self) -> str:
        return self.xa_elem.name()

    @property
    def path(self) -> str:
        return self.xa_elem.path()

    def delete(self):
        """Deletes the login item.

        .. versionadded:: 0.0.8
        """
        return self.xa_elem.delete()




# class XASystemEventsConfiguration(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.accountName: str #: the name used to authenticate
#         self.connected: bool #: Is the configuration connected?
#         self.id: str #: the unique identifier for the configuration
#         self.name: str #: the name of the configuration
#         self.connect: XASystemEventsConfiguration #: connect a configuration or service
#         self.disconnect: XASystemEventsConfiguration #: disconnect a configuration or service

#     @property
#     def accountName(self) -> str:
#         return self.xa_elem.accountName()

#     @property
#     def connected(self) -> bool:
#         return self.xa_elem.connected()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def connect(self) -> XASystemEventsConfiguration:
#         return self.xa_elem.connect()

#     @property
#     def disconnect(self) -> XASystemEventsConfiguration:
#         return self.xa_elem.disconnect()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsInterface(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.automatic: bool #: configure the interface speed, duplex, and mtu automatically?
#         self.duplex: str #: the duplex setting half | full | full with flow control
#         self.id: str #: the unique identifier for the interface
#         self.kind: str #: the type of interface
#         self.MACAddress: str #: the MAC address for the interface
#         self.mtu: int #: the packet size
#         self.name: str #: the name of the interface
#         self.speed: int #: ethernet speed 10 | 100 | 1000

#     @property
#     def automatic(self) -> bool:
#         return self.xa_elem.automatic()

#     @property
#     def duplex(self) -> str:
#         return self.xa_elem.duplex()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def kind(self) -> str:
#         return self.xa_elem.kind()

#     @property
#     def MACAddress(self) -> str:
#         return self.xa_elem.MACAddress()

#     @property
#     def mtu(self) -> int:
#         return self.xa_elem.mtu()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def speed(self) -> int:
#         return self.xa_elem.speed()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsLocation(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.id: str #: the unique identifier for the location
#         self.name: str #: the name of the location

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsNetworkPreferencesObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.currentLocation: XASystemEventsLocation #: the current location

#     @property
#     def currentLocation(self) -> XASystemEventsLocation:
#         return self.xa_elem.currentLocation()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsService(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.active: bool #: Is the service active?
#         self.currentConfiguration: XASystemEventsConfiguration #: the currently selected configuration
#         self.id: str #: the unique identifier for the service
#         self.interface: XASystemEventsInterface #: the interface the service is built on
#         self.kind: int #: the type of service
#         self.name: str #: the name of the service
#         self.connect: XASystemEventsConfiguration #: connect a configuration or service
#         self.disconnect: XASystemEventsConfiguration #: disconnect a configuration or service

#     @property
#     def active(self) -> bool:
#         return self.xa_elem.active()

#     @property
#     def currentConfiguration(self) -> XASystemEventsConfiguration:
#         return self.xa_elem.currentConfiguration()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def interface(self) -> XASystemEventsInterface:
#         return self.xa_elem.interface()

#     @property
#     def kind(self) -> int:
#         return self.xa_elem.kind()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def connect(self) -> XASystemEventsConfiguration:
#         return self.xa_elem.connect()

#     @property
#     def disconnect(self) -> XASystemEventsConfiguration:
#         return self.xa_elem.disconnect()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsScreenSaver(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.displayedName: str #: name of the screen saver module as displayed to the user
#         self.name: str #: name of the screen saver module to be displayed
#         self.path: XASystemEventsAlias #: path to the screen saver module
#         self.pictureDisplayStyle: str #: effect to use when displaying picture-based screen savers (slideshow, collage, or mosaic)
#         self.start: XAvoid) #: start the screen saver
#         self.stop: XAvoid) #: stop the screen saver

#     @property
#     def displayedName(self) -> str:
#         return self.xa_elem.displayedName()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def path(self) -> XASystemEventsAlias:
#         return self.xa_elem.path()

#     @property
#     def pictureDisplayStyle(self) -> str:
#         return self.xa_elem.pictureDisplayStyle()

#     @property
#     def start(self) -> XAvoid):
#         return self.xa_elem.start()

#     @property
#     def stop(self) -> XAvoid):
#         return self.xa_elem.stop()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsScreenSaverPreferencesObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.delayInterval: int #: number of seconds of idle time before the screen saver starts; zero for never
#         self.mainScreenOnly: bool #: should the screen saver be shown only on the main screen?
#         self.running: bool #: is the screen saver running?
#         self.showClock: bool #: should a clock appear over the screen saver?
#         self.start: XAvoid) #: start the screen saver
#         self.stop: XAvoid) #: stop the screen saver

#     @property
#     def delayInterval(self) -> int:
#         return self.xa_elem.delayInterval()

#     @property
#     def mainScreenOnly(self) -> bool:
#         return self.xa_elem.mainScreenOnly()

#     @property
#     def running(self) -> bool:
#         return self.xa_elem.running()

#     @property
#     def showClock(self) -> bool:
#         return self.xa_elem.showClock()

#     @property
#     def start(self) -> XAvoid):
#         return self.xa_elem.start()

#     @property
#     def stop(self) -> XAvoid):
#         return self.xa_elem.stop()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsSecurityPreferencesObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.automaticLogin: bool #: Is automatic login allowed?
#         self.logOutWhenInactive: bool #: Will the computer log out when inactive?
#         self.logOutWhenInactiveInterval: int #: The interval of inactivity after which the computer will log out
#         self.requirePasswordToUnlock: bool #: Is a password required to unlock secure preferences?
#         self.requirePasswordToWake: bool #: Is a password required to wake the computer from sleep or screen saver?
#         self.secureVirtualMemory: bool #: Is secure virtual memory being used?

#     @property
#     def automaticLogin(self) -> bool:
#         return self.xa_elem.automaticLogin()

#     @property
#     def logOutWhenInactive(self) -> bool:
#         return self.xa_elem.logOutWhenInactive()

#     @property
#     def logOutWhenInactiveInterval(self) -> int:
#         return self.xa_elem.logOutWhenInactiveInterval()

#     @property
#     def requirePasswordToUnlock(self) -> bool:
#         return self.xa_elem.requirePasswordToUnlock()

#     @property
#     def requirePasswordToWake(self) -> bool:
#         return self.xa_elem.requirePasswordToWake()

#     @property
#     def secureVirtualMemory(self) -> bool:
#         return self.xa_elem.secureVirtualMemory()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsDiskItem(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.busyStatus: bool #: Is the disk item busy?
#         self.container: XASystemEventsDiskItem #: the folder or disk which has this disk item as an element
#         self.creationDate: XANSDate #: the date on which the disk item was created
#         self.displayedName: str #: the name of the disk item as displayed in the User Interface
#         self.id: str #: the unique ID of the disk item
#         self.modificationDate: XANSDate #: the date on which the disk item was last modified
#         self.name: str #: the name of the disk item
#         self.nameExtension: str #: the extension portion of the name
#         self.packageFolder: bool #: Is the disk item a package?
#         self.path: str #: the file system path of the disk item
#         self.physicalSize: int #: the actual space used by the disk item on disk
#         self.POSIXPath: str #: the POSIX file system path of the disk item
#         self.size: int #: the logical size of the disk item
#         self.URL: str #: the URL of the disk item
#         self.visible: bool #: Is the disk item visible?
#         self.volume: str #: the volume on which the disk item resides
#         self.delete: XAvoid) #: Delete disk item(s).

#     @property
#     def busyStatus(self) -> bool:
#         return self.xa_elem.busyStatus()

#     @property
#     def container(self) -> XASystemEventsDiskItem:
#         return self.xa_elem.container()

#     @property
#     def creationDate(self) -> XANSDate:
#         return self.xa_elem.creationDate()

#     @property
#     def displayedName(self) -> str:
#         return self.xa_elem.displayedName()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def modificationDate(self) -> XANSDate:
#         return self.xa_elem.modificationDate()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def nameExtension(self) -> str:
#         return self.xa_elem.nameExtension()

#     @property
#     def packageFolder(self) -> bool:
#         return self.xa_elem.packageFolder()

#     @property
#     def path(self) -> str:
#         return self.xa_elem.path()

#     @property
#     def physicalSize(self) -> int:
#         return self.xa_elem.physicalSize()

#     @property
#     def POSIXPath(self) -> str:
#         return self.xa_elem.POSIXPath()

#     @property
#     def size(self) -> int:
#         return self.xa_elem.size()

#     @property
#     def URL(self) -> str:
#         return self.xa_elem.URL()

#     @property
#     def visible(self) -> bool:
#         return self.xa_elem.visible()

#     @property
#     def volume(self) -> str:
#         return self.xa_elem.volume()

#     @property
#     def delete(self) -> XAvoid):
#         return self.xa_elem.delete()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> XAid:
#         """Move disk item(s) to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsAlias(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.creatorType: XAid #: the OSType identifying the application that created the alias
#         self.defaultApplication: XAid #: the application that will launch if the alias is opened
#         self.fileType: XAid #: the OSType identifying the type of data contained in the alias
#         self.kind: str #: The kind of alias, as shown in Finder
#         self.productVersion: str #: the version of the product (visible at the top of the "Get Info" window)
#         self.shortVersion: str #: the short version of the application bundle referenced by the alias
#         self.stationery: bool #: Is the alias a stationery pad?
#         self.typeIdentifier: str #: The type identifier of the alias
#         self.version: str #: the version of the application bundle referenced by the alias (visible at the bottom of the "Get Info" window)

#     @property
#     def creatorType(self) -> XAid:
#         return self.xa_elem.creatorType()

#     @property
#     def defaultApplication(self) -> XAid:
#         return self.xa_elem.defaultApplication()

#     @property
#     def fileType(self) -> XAid:
#         return self.xa_elem.fileType()

#     @property
#     def kind(self) -> str:
#         return self.xa_elem.kind()

#     @property
#     def productVersion(self) -> str:
#         return self.xa_elem.productVersion()

#     @property
#     def shortVersion(self) -> str:
#         return self.xa_elem.shortVersion()

#     @property
#     def stationery(self) -> bool:
#         return self.xa_elem.stationery()

#     @property
#     def typeIdentifier(self) -> str:
#         return self.xa_elem.typeIdentifier()

#     @property
#     def version(self) -> str:
#         return self.xa_elem.version()

# class XASystemEventsDisk(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.capacity: XANSNumber #: the total number of bytes (free or used) on the disk
#         self.ejectable: bool #: Can the media be ejected (floppies, CD's, and so on)?
#         self.format: XASystemEventsEdfm #: the file system format of this disk
#         self.freeSpace: XANSNumber #: the number of free bytes left on the disk
#         self.ignorePrivileges: bool #: Ignore permissions on this disk?
#         self.localVolume: bool #: Is the media a local volume (as opposed to a file server)?
#         self.server: XAid #: the server on which the disk resides, AFP volumes only
#         self.startup: bool #: Is this disk the boot disk?
#         self.zone: XAid #: the zone in which the disk's server resides, AFP volumes only

#     @property
#     def capacity(self) -> XANSNumber:
#         return self.xa_elem.capacity()

#     @property
#     def ejectable(self) -> bool:
#         return self.xa_elem.ejectable()

#     @property
#     def format(self) -> XASystemEventsEdfm:
#         return self.xa_elem.format()

#     @property
#     def freeSpace(self) -> XANSNumber:
#         return self.xa_elem.freeSpace()

#     @property
#     def ignorePrivileges(self) -> bool:
#         return self.xa_elem.ignorePrivileges()

#     @property
#     def localVolume(self) -> bool:
#         return self.xa_elem.localVolume()

#     @property
#     def server(self) -> XAid:
#         return self.xa_elem.server()

#     @property
#     def startup(self) -> bool:
#         return self.xa_elem.startup()

#     @property
#     def zone(self) -> XAid:
#         return self.xa_elem.zone()

# class XASystemEventsDomain(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.applicationSupportFolder: XASystemEventsFolder #: The Application Support folder
#         self.applicationsFolder: XASystemEventsFolder #: The Applications folder
#         self.desktopPicturesFolder: XASystemEventsFolder #: The Desktop Pictures folder
#         self.FolderActionScriptsFolder: XASystemEventsFolder #: The Folder Action Scripts folder
#         self.fontsFolder: XASystemEventsFolder #: The Fonts folder
#         self.id: str #: the unique identifier of the domain
#         self.libraryFolder: XASystemEventsFolder #: The Library folder
#         self.name: str #: the name of the domain
#         self.preferencesFolder: XASystemEventsFolder #: The Preferences folder
#         self.scriptingAdditionsFolder: XASystemEventsFolder #: The Scripting Additions folder
#         self.scriptsFolder: XASystemEventsFolder #: The Scripts folder
#         self.sharedDocumentsFolder: XASystemEventsFolder #: The Shared Documents folder
#         self.speakableItemsFolder: XASystemEventsFolder #: The Speakable Items folder
#         self.utilitiesFolder: XASystemEventsFolder #: The Utilities folder
#         self.workflowsFolder: XASystemEventsFolder #: The Automator Workflows folder

#     @property
#     def applicationSupportFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.applicationSupportFolder()

#     @property
#     def applicationsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.applicationsFolder()

#     @property
#     def desktopPicturesFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.desktopPicturesFolder()

#     @property
#     def FolderActionScriptsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.FolderActionScriptsFolder()

#     @property
#     def fontsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.fontsFolder()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def libraryFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.libraryFolder()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def preferencesFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.preferencesFolder()

#     @property
#     def scriptingAdditionsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.scriptingAdditionsFolder()

#     @property
#     def scriptsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.scriptsFolder()

#     @property
#     def sharedDocumentsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.sharedDocumentsFolder()

#     @property
#     def speakableItemsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.speakableItemsFolder()

#     @property
#     def utilitiesFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.utilitiesFolder()

#     @property
#     def workflowsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.workflowsFolder()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsClassicDomainObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.appleMenuFolder: XASystemEventsFolder #: The Apple Menu Items folder
#         self.controlPanelsFolder: XASystemEventsFolder #: The Control Panels folder
#         self.controlStripModulesFolder: XASystemEventsFolder #: The Control Strip Modules folder
#         self.desktopFolder: XASystemEventsFolder #: The Classic Desktop folder
#         self.extensionsFolder: XASystemEventsFolder #: The Extensions folder
#         self.fontsFolder: XASystemEventsFolder #: The Fonts folder
#         self.launcherItemsFolder: XASystemEventsFolder #: The Launcher Items folder
#         self.preferencesFolder: XASystemEventsFolder #: The Classic Preferences folder
#         self.shutdownFolder: XASystemEventsFolder #: The Shutdown Items folder
#         self.startupItemsFolder: XASystemEventsFolder #: The StartupItems folder
#         self.systemFolder: XASystemEventsFolder #: The System folder

#     @property
#     def appleMenuFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.appleMenuFolder()

#     @property
#     def controlPanelsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.controlPanelsFolder()

#     @property
#     def controlStripModulesFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.controlStripModulesFolder()

#     @property
#     def desktopFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.desktopFolder()

#     @property
#     def extensionsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.extensionsFolder()

#     @property
#     def fontsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.fontsFolder()

#     @property
#     def launcherItemsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.launcherItemsFolder()

#     @property
#     def preferencesFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.preferencesFolder()

#     @property
#     def shutdownFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.shutdownFolder()

#     @property
#     def startupItemsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.startupItemsFolder()

#     @property
#     def systemFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.systemFolder()

# class XASystemEventsFile(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.creatorType: XAid #: the OSType identifying the application that created the file
#         self.defaultApplication: XAid #: the application that will launch if the file is opened
#         self.fileType: XAid #: the OSType identifying the type of data contained in the file
#         self.kind: str #: The kind of file, as shown in Finder
#         self.productVersion: str #: the version of the product (visible at the top of the "Get Info" window)
#         self.shortVersion: str #: the short version of the file
#         self.stationery: bool #: Is the file a stationery pad?
#         self.typeIdentifier: str #: The type identifier of the file
#         self.version: str #: the version of the file (visible at the bottom of the "Get Info" window)
#         self.open: XASystemEventsFile #: Open disk item(s) with the appropriate application.

#     @property
#     def creatorType(self) -> XAid:
#         return self.xa_elem.creatorType()

#     @property
#     def defaultApplication(self) -> XAid:
#         return self.xa_elem.defaultApplication()

#     @property
#     def fileType(self) -> XAid:
#         return self.xa_elem.fileType()

#     @property
#     def kind(self) -> str:
#         return self.xa_elem.kind()

#     @property
#     def productVersion(self) -> str:
#         return self.xa_elem.productVersion()

#     @property
#     def shortVersion(self) -> str:
#         return self.xa_elem.shortVersion()

#     @property
#     def stationery(self) -> bool:
#         return self.xa_elem.stationery()

#     @property
#     def typeIdentifier(self) -> str:
#         return self.xa_elem.typeIdentifier()

#     @property
#     def version(self) -> str:
#         return self.xa_elem.version()

#     @property
#     def open(self) -> XASystemEventsFile:
#         return self.xa_elem.open()

# class XASystemEventsFilePackage(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsFolder(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsLocalDomainObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsNetworkDomainObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsSystemDomainObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsUserDomainObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.desktopFolder: XASystemEventsFolder #: The user's Desktop folder
#         self.documentsFolder: XASystemEventsFolder #: The user's Documents folder
#         self.downloadsFolder: XASystemEventsFolder #: The user's Downloads folder
#         self.favoritesFolder: XASystemEventsFolder #: The user's Favorites folder
#         self.homeFolder: XASystemEventsFolder #: The user's Home folder
#         self.moviesFolder: XASystemEventsFolder #: The user's Movies folder
#         self.musicFolder: XASystemEventsFolder #: The user's Music folder
#         self.picturesFolder: XASystemEventsFolder #: The user's Pictures folder
#         self.publicFolder: XASystemEventsFolder #: The user's Public folder
#         self.sitesFolder: XASystemEventsFolder #: The user's Sites folder
#         self.temporaryItemsFolder: XASystemEventsFolder #: The Temporary Items folder

#     @property
#     def desktopFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.desktopFolder()

#     @property
#     def documentsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.documentsFolder()

#     @property
#     def downloadsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.downloadsFolder()

#     @property
#     def favoritesFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.favoritesFolder()

#     @property
#     def homeFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.homeFolder()

#     @property
#     def moviesFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.moviesFolder()

#     @property
#     def musicFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.musicFolder()

#     @property
#     def picturesFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.picturesFolder()

#     @property
#     def publicFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.publicFolder()

#     @property
#     def sitesFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.sitesFolder()

#     @property
#     def temporaryItemsFolder(self) -> XASystemEventsFolder:
#         return self.xa_elem.temporaryItemsFolder()

# class XASystemEventsFolderAction(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.enabled: bool #: Is the folder action enabled?
#         self.name: str #: the name of the folder action, which is also the name of the folder
#         self.path: str #: the path to the folder to which the folder action applies
#         self.volume: str #: the volume on which the folder to which the folder action applies resides

#     @property
#     def enabled(self) -> bool:
#         return self.xa_elem.enabled()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def path(self) -> str:
#         return self.xa_elem.path()

#     @property
#     def volume(self) -> str:
#         return self.xa_elem.volume()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

#     def enableProcessNewChanges(self) -> XAvoid:
#         """Enable a folder action.
#         """
#         return self.xa_elem.enableProcessNewChanges_(...)
    

# class XASystemEventsScript(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.enabled: bool #: Is the script enabled?
#         self.name: str #: the name of the script
#         self.path: str #: the file system path of the disk
#         self.POSIXPath: str #: the POSIX file system path of the disk

#     @property
#     def enabled(self) -> bool:
#         return self.xa_elem.enabled()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def path(self) -> str:
#         return self.xa_elem.path()

#     @property
#     def POSIXPath(self) -> str:
#         return self.xa_elem.POSIXPath()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsAction(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.objectDescription: str #: what the action does
#         self.name: str #: the name of the action
#         self.perform: XASystemEventsAction #: cause the target process to behave as if the action were applied to its UI element

#     @property
#     def objectDescription(self) -> str:
#         return self.xa_elem.objectDescription()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def perform(self) -> XASystemEventsAction:
#         return self.xa_elem.perform()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsAttribute(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.name: str #: the name of the attribute
#         self.settable: bool #: Can the attribute be set?
#         self.value: XAid #: the current value of the attribute

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def settable(self) -> bool:
#         return self.xa_elem.settable()

#     @property
#     def value(self) -> XAid:
#         return self.xa_elem.value()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsUIElement(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.accessibilityDescription: XAid #: a more complete description of the UI element and its capabilities
#         self.objectDescription: XAid #: the accessibility description, if available; otherwise, the role description
#         self.enabled: XAid #: Is the UI element enabled? ( Does it accept clicks? )
#         self.//: XANSArray<SBObject #: a list of every UI element contained in this UI element and its child UI elements, to the limits of the tree
#         self.focused: XAid #: Is the focus on this UI element?
#         self.help: XAid #: an elaborate description of the UI element and its capabilities
#         self.maximumValue: XAid #: the maximum value that the UI element can take on
#         self.minimumValue: XAid #: the minimum value that the UI element can take on
#         self.name: str #: the name of the UI Element, which identifies it within its container
#         self.orientation: XAid #: the orientation of the UI element
#         self.position: XAid #: the position of the UI element
#         self.role: str #: an encoded description of the UI element and its capabilities
#         self.roleDescription: str #: a more complete description of the UI element's role
#         self.selected: XAid #: Is the UI element selected?
#         self.size: XAid #: the size of the UI element
#         self.subrole: XAid #: an encoded description of the UI element and its capabilities
#         self.title: str #: the title of the UI element as it appears on the screen
#         self.value: XAid #: the current value of the UI element
#         self.select: XASystemEventsUIElement #: set the selected property of the UI element

#     @property
#     def accessibilityDescription(self) -> XAid:
#         return self.xa_elem.accessibilityDescription()

#     @property
#     def objectDescription(self) -> XAid:
#         return self.xa_elem.objectDescription()

#     @property
#     def enabled(self) -> XAid:
#         return self.xa_elem.enabled()

#     @property
#     def //(self) -> XANSArray<SBObject:
#         return self.xa_elem.//()

#     @property
#     def focused(self) -> XAid:
#         return self.xa_elem.focused()

#     @property
#     def help(self) -> XAid:
#         return self.xa_elem.help()

#     @property
#     def maximumValue(self) -> XAid:
#         return self.xa_elem.maximumValue()

#     @property
#     def minimumValue(self) -> XAid:
#         return self.xa_elem.minimumValue()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def orientation(self) -> XAid:
#         return self.xa_elem.orientation()

#     @property
#     def position(self) -> XAid:
#         return self.xa_elem.position()

#     @property
#     def role(self) -> str:
#         return self.xa_elem.role()

#     @property
#     def roleDescription(self) -> str:
#         return self.xa_elem.roleDescription()

#     @property
#     def selected(self) -> XAid:
#         return self.xa_elem.selected()

#     @property
#     def size(self) -> XAid:
#         return self.xa_elem.size()

#     @property
#     def subrole(self) -> XAid:
#         return self.xa_elem.subrole()

#     @property
#     def title(self) -> str:
#         return self.xa_elem.title()

#     @property
#     def value(self) -> XAid:
#         return self.xa_elem.value()

#     @property
#     def select(self) -> XASystemEventsUIElement:
#         return self.xa_elem.select()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

#     def clickAt(self) -> XAid:
#         """cause the target process to behave as if the UI element were clicked
#         """
#         return self.xa_elem.clickAt_(...)
    

# class XASystemEventsBrowser(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsBusyIndicator(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsButton(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsCheckbox(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsColorWell(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsColumn(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsComboBox(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsDrawer(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsGroup(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsGrowArea(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsImage(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsIncrementor(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsList(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsMenu(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsMenuBar(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsMenuBarItem(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsMenuButton(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsMenuItem(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsOutline(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsPopOver(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsPopUpButton(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsProcess(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.acceptsHighLevelEvents: bool #: Is the process high-level event aware (accepts open application, open document, print document, and quit)?
#         self.acceptsRemoteEvents: bool #: Does the process accept remote events?
#         self.architecture: str #: the architecture in which the process is running
#         self.backgroundOnly: bool #: Does the process run exclusively in the background?
#         self.bundleIdentifier: str #: the bundle identifier of the process' application file
#         self.Classic: bool #: Is the process running in the Classic environment?
#         self.creatorType: str #: the OSType of the creator of the process (the signature)
#         self.displayedName: str #: the name of the file from which the process was launched, as displayed in the User Interface
#         self.file: XAid #: the file from which the process was launched
#         self.fileType: str #: the OSType of the file type of the process
#         self.frontmost: bool #: Is the process the frontmost process
#         self.hasScriptingTerminology: bool #: Does the process have a scripting terminology, i.e., can it be scripted?
#         self.id: XANSInteger) #: The unique identifier of the process
#         self.name: str #: the name of the process
#         self.partitionSpaceUsed: int #: the number of bytes currently used in the process' partition
#         self.shortName: XAid #: the short name of the file from which the process was launched
#         self.totalPartitionSize: int #: the size of the partition with which the process was launched
#         self.unixId: int #: The Unix process identifier of a process running in the native environment, or -1 for a process running in the Classic environment
#         self.visible: bool #: Is the process' layer visible?

#     @property
#     def acceptsHighLevelEvents(self) -> bool:
#         return self.xa_elem.acceptsHighLevelEvents()

#     @property
#     def acceptsRemoteEvents(self) -> bool:
#         return self.xa_elem.acceptsRemoteEvents()

#     @property
#     def architecture(self) -> str:
#         return self.xa_elem.architecture()

#     @property
#     def backgroundOnly(self) -> bool:
#         return self.xa_elem.backgroundOnly()

#     @property
#     def bundleIdentifier(self) -> str:
#         return self.xa_elem.bundleIdentifier()

#     @property
#     def Classic(self) -> bool:
#         return self.xa_elem.Classic()

#     @property
#     def creatorType(self) -> str:
#         return self.xa_elem.creatorType()

#     @property
#     def displayedName(self) -> str:
#         return self.xa_elem.displayedName()

#     @property
#     def file(self) -> XAid:
#         return self.xa_elem.file()

#     @property
#     def fileType(self) -> str:
#         return self.xa_elem.fileType()

#     @property
#     def frontmost(self) -> bool:
#         return self.xa_elem.frontmost()

#     @property
#     def hasScriptingTerminology(self) -> bool:
#         return self.xa_elem.hasScriptingTerminology()

#     @property
#     def id(self) -> XANSInteger):
#         return self.xa_elem.id()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def partitionSpaceUsed(self) -> int:
#         return self.xa_elem.partitionSpaceUsed()

#     @property
#     def shortName(self) -> XAid:
#         return self.xa_elem.shortName()

#     @property
#     def totalPartitionSize(self) -> int:
#         return self.xa_elem.totalPartitionSize()

#     @property
#     def unixId(self) -> int:
#         return self.xa_elem.unixId()

#     @property
#     def visible(self) -> bool:
#         return self.xa_elem.visible()

# class XASystemEventsApplicationProcess(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.applicationFile: XAid #: a reference to the application file from which this process was launched

#     @property
#     def applicationFile(self) -> XAid:
#         return self.xa_elem.applicationFile()

# class XASystemEventsDeskAccessoryProcess(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.deskAccessoryFile: XASystemEventsAlias #: a reference to the desk accessory file from which this process was launched

#     @property
#     def deskAccessoryFile(self) -> XASystemEventsAlias:
#         return self.xa_elem.deskAccessoryFile()

# class XASystemEventsProgressIndicator(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsRadioButton(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsRadioGroup(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsRelevanceIndicator(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsRow(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsScrollArea(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsScrollBar(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsSheet(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsSlider(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsSplitter(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsSplitterGroup(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsStaticText(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsTabGroup(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsTable(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsTextArea(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsTextField(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsToolbar(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsValueIndicator(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        



class XASystemEventsPropertyListFileList(XABase.XAList):
    """A wrapper around lists of property list files that employs fast enumeration techniques.

    All properties of property list files can be called as methods on the wrapped list, returning a list containing each file's value for the property.

    .. versionadded:: 0.0.8
    """
    def __init__(self, properties: dict, filter: Union[dict, None] = None):
        super().__init__(properties, XASystemEventsPropertyListFile, filter)

    def contents(self) -> 'XASystemEventsPropertyListItemList':
        """Gets the items of each file in the list.

        :return: A list of property list items
        :rtype: XASystemEventsPropertyListItemList
        
        .. versionadded:: 0.0.8
        """
        ls = self.xa_elem.arrayByApplyingSelector_("contents")
        return self._new_element(ls, XASystemEventsPropertyListItemList)

    def by_content(self, contents: 'XASystemEventsPropertyListItemList') -> Union['XASystemEventsPropertyListFile', None]:
        """Retrieves the property list ite whose contents matches the given contents, if one exists.

        :return: The desired property list item, if it is found
        :rtype: Union[XASystemEventsPropertyListFile, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("contents", contents.xa_elem)

    def __repr__(self):
        return "<" + str(type(self)) + str(self.contents()) + ">"

class XASystemEventsPropertyListFile(XABase.XAObject):
    """A file containing data in Property List format
    """
    def __init__(self, properties):
        super().__init__(properties)
        
        self.contents: XASystemEventsPropertyListItem #: the contents of the property list file; elements and properties of the property list item may be accessed as if they were elements and properties of the property list file

    @property
    def contents(self) -> 'XASystemEventsPropertyListItem':
        return self._new_element(self.xa_elem.contents(), XASystemEventsPropertyListItem)




class XASystemEventsPropertyListItemList(XABase.XAList):
    """A wrapper around lists of property list items that employs fast enumeration techniques.

    All properties of property list items can be called as methods on the wrapped list, returning a list containing each item's value for the property.

    .. versionadded:: 0.0.8
    """
    def __init__(self, properties: dict, filter: Union[dict, None] = None):
        super().__init__(properties, XASystemEventsPropertyListItem, filter)

    def kind(self) -> List[str]:
        """Gets the kind of each property list item in the list.

        :return: A list of property list item kinds
        :rtype: List[str]
        
        .. versionadded:: 0.0.8
        """
        # TODO
        return list(self.xa_elem.arrayByApplyingSelector_("kind"))

    def name(self) -> List[str]:
        """Gets the name of each property list item in the list.

        :return: A list of property list item names
        :rtype: List[str]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("name"))

    def text(self) -> List[str]:
        """Gets the text of each property list item in the list.

        :return: A list of property list item texts
        :rtype: List[str]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("text"))

    def value(self) -> List[Union[int, bool, datetime, 'XASystemEventsList', dict, str, 'XASystemEventsData']]:
        """Gets the value of each property list item in the list.

        :return: A list of property list item values
        :rtype: List[Union[int, bool, datetime, XASystemEventsList, dict, str, XASystemEventsData]]
        
        .. versionadded:: 0.0.8
        """
        # TODO: SPECIALIZE TYPE
        return list(self.xa_elem.arrayByApplyingSelector_("value"))

    def by_kind(self, kind: str) -> Union['XASystemEventsPropertyListItem', None]:
        """Retrieves the property list ite whose kind matches the given kind, if one exists.

        :return: The desired property list item, if it is found
        :rtype: Union[XASystemEventsPropertyListItem, None]
        
        .. versionadded:: 0.0.8
        """
        # TODO
        return self.by_property("kind", kind)

    def by_name(self, name: str) -> Union['XASystemEventsPropertyListItem', None]:
        """Retrieves the property list ite whose name matches the given name, if one exists.

        :return: The desired property list item, if it is found
        :rtype: Union[XASystemEventsPropertyListItem, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("name", name)

    def by_text(self, text: str) -> Union['XASystemEventsPropertyListItem', None]:
        """Retrieves the property list ite whose text matches the given text, if one exists.

        :return: The desired property list item, if it is found
        :rtype: Union[XASystemEventsPropertyListItem, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("text", text)

    def by_value(self, value: Union[int, bool, datetime, 'XASystemEventsList', dict, str, 'XASystemEventsData']) -> Union['XASystemEventsPropertyListItem', None]:
        """Retrieves the property list ite whose value matches the given value, if one exists.

        :return: The desired property list item, if it is found
        :rtype: Union[XASystemEventsPropertyListItem, None]
        
        .. versionadded:: 0.0.8
        """
        # TODO
        return self.by_property("value", value)

    def __repr__(self):
        return "<" + str(type(self)) + str(self.name()) + ">"

class XASystemEventsPropertyListItem(XABase.XAObject):
    """A unit of data in Property List format
    """
    def __init__(self, properties):
        super().__init__(properties)
        
        # TODO - type of kind?
        self.kind: str #: the kind of data stored in the property list item: boolean/data/date/list/number/record/string
        self.name: str #: the name of the property list item (if any)
        self.text: str #: the text representation of the property list data
        self.value: Union[int, bool, datetime, XASystemEventsList, dict, str, XASystemEventsData] #: the value of the property list item

    @property
    def kind(self) -> str:
        return self.xa_elem.kind()

    @property
    def name(self) -> str:
        return self.xa_elem.name()

    @property
    def text(self) -> str:
        return self.xa_elem.text()

    # TODO: Specialize to exact type
    @property
    def value(self) -> Union[int, bool, datetime, 'XASystemEventsList', dict, str, 'XASystemEventsData']:
        return self.xa_elem.value()



# class XASystemEventsXMLAttribute(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.name: str #: the name of the XML attribute
#         self.value: XAid #: the value of the XML attribute

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def value(self) -> XAid:
#         return self.xa_elem.value()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsXMLData(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.id: str #: the unique identifier of the XML data
#         self.name: str #: the name of the XML data
#         self.text: str #: the text representation of the XML data

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def text(self) -> str:
#         return self.xa_elem.text()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsXMLElement(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.id: str #: the unique identifier of the XML element
#         self.name: str #: the name of the XML element
#         self.value: XAid #: the value of the XML element

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def value(self) -> XAid:
#         return self.xa_elem.value()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsXMLFile(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.contents: XASystemEventsXMLData #: the contents of the XML file; elements and properties of the XML data may be accessed as if they were elements and properties of the XML file

#     @property
#     def contents(self) -> XASystemEventsXMLData:
#         return self.xa_elem.contents()

# class XASystemEventsPrintSettings(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.copies: int #: the number of copies of a document to be printed
#         self.collating: bool #: Should printed copies be collated?
#         self.startingPage: int #: the first page of the document to be printed
#         self.endingPage: int #: the last page of the document to be printed
#         self.pagesAcross: int #: number of logical pages laid across a physical page
#         self.pagesDown: int #: number of logical pages laid out down a physical page
#         self.requestedPrintTime: XANSDate #: the time at which the desktop printer should print the document
#         self.errorHandling: XASystemEventsEnum #: how errors are handled
#         self.faxNumber: str #: for fax number
#         self.targetPrinter: str #: for target printer

#     @property
#     def copies(self) -> int:
#         return self.xa_elem.copies()

#     @property
#     def collating(self) -> bool:
#         return self.xa_elem.collating()

#     @property
#     def startingPage(self) -> int:
#         return self.xa_elem.startingPage()

#     @property
#     def endingPage(self) -> int:
#         return self.xa_elem.endingPage()

#     @property
#     def pagesAcross(self) -> int:
#         return self.xa_elem.pagesAcross()

#     @property
#     def pagesDown(self) -> int:
#         return self.xa_elem.pagesDown()

#     @property
#     def requestedPrintTime(self) -> XANSDate:
#         return self.xa_elem.requestedPrintTime()

#     @property
#     def errorHandling(self) -> XASystemEventsEnum:
#         return self.xa_elem.errorHandling()

#     @property
#     def faxNumber(self) -> str:
#         return self.xa_elem.faxNumber()

#     @property
#     def targetPrinter(self) -> str:
#         return self.xa_elem.targetPrinter()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsScriptingClass(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.name: str #: The name of the class
#         self.id: str #: The unique identifier of the class
#         self.objectDescription: str #: The description of the class
#         self.hidden: bool #: Is the class hidden?
#         self.pluralName: str #: The plural name of the class
#         self.suiteName: str #: The name of the suite to which this class belongs
#         self.superclass: XASystemEventsScriptingClass #: The class from which this class inherits

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def objectDescription(self) -> str:
#         return self.xa_elem.objectDescription()

#     @property
#     def hidden(self) -> bool:
#         return self.xa_elem.hidden()

#     @property
#     def pluralName(self) -> str:
#         return self.xa_elem.pluralName()

#     @property
#     def suiteName(self) -> str:
#         return self.xa_elem.suiteName()

#     @property
#     def superclass(self) -> XASystemEventsScriptingClass:
#         return self.xa_elem.superclass()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsScriptingCommand(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.name: str #: The name of the command
#         self.id: str #: The unique identifier of the command
#         self.objectDescription: str #: The description of the command
#         self.directParameter: XASystemEventsScriptingParameter #: The direct parameter of the command
#         self.hidden: bool #: Is the command hidden?
#         self.scriptingResult: XASystemEventsScriptingResultObject #: The object or data returned by this command
#         self.suiteName: str #: The name of the suite to which this command belongs

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def objectDescription(self) -> str:
#         return self.xa_elem.objectDescription()

#     @property
#     def directParameter(self) -> XASystemEventsScriptingParameter:
#         return self.xa_elem.directParameter()

#     @property
#     def hidden(self) -> bool:
#         return self.xa_elem.hidden()

#     @property
#     def scriptingResult(self) -> XASystemEventsScriptingResultObject:
#         return self.xa_elem.scriptingResult()

#     @property
#     def suiteName(self) -> str:
#         return self.xa_elem.suiteName()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

class XASystemEventsScriptingDefinitionObject(XABase.XAObject):
    """The scripting definition of the System Events application.

    .. versionadded:: 0.0.8
    """
    def __init__(self, properties):
        super().__init__(properties)

    def scripting_suites(self, filter: dict = None) -> Union['XASystemEventsScriptingSuiteList', None]:
        """Returns a list of scripting suites, as PyXA-wrapped objects, matching the given filter.

        :param filter: A dictionary specifying property-value pairs that all returned scripting suites will have, or None
        :type filter: Union[dict, None]
        :return: The list of scripting suites
        :rtype: XASystemEventsScriptingSuiteList

        .. versionadded:: 0.0.8
        """
        return self._new_element(self.xa_elem.scriptingSuites(), XASystemEventsScriptingSuiteList, filter)
    

# class XASystemEventsScriptingElement(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        

# class XASystemEventsScriptingEnumeration(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.name: str #: The name of the enumeration
#         self.id: str #: The unique identifier of the enumeration
#         self.hidden: bool #: Is the enumeration hidden?

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def hidden(self) -> bool:
#         return self.xa_elem.hidden()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsScriptingEnumerator(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.name: str #: The name of the enumerator
#         self.id: str #: The unique identifier of the enumerator
#         self.objectDescription: str #: The description of the enumerator
#         self.hidden: bool #: Is the enumerator hidden?

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def objectDescription(self) -> str:
#         return self.xa_elem.objectDescription()

#     @property
#     def hidden(self) -> bool:
#         return self.xa_elem.hidden()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsScriptingParameter(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.name: str #: The name of the parameter
#         self.id: str #: The unique identifier of the parameter
#         self.objectDescription: str #: The description of the parameter
#         self.hidden: bool #: Is the parameter hidden?
#         self.kind: str #: The kind of object or data specified by this parameter
#         self.optional: bool #: Is the parameter optional?

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def objectDescription(self) -> str:
#         return self.xa_elem.objectDescription()

#     @property
#     def hidden(self) -> bool:
#         return self.xa_elem.hidden()

#     @property
#     def kind(self) -> str:
#         return self.xa_elem.kind()

#     @property
#     def optional(self) -> bool:
#         return self.xa_elem.optional()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsScriptingProperty(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.name: str #: The name of the property
#         self.id: str #: The unique identifier of the property
#         self.access: XASystemEventsAccs #: The type of access to this property
#         self.objectDescription: str #: The description of the property
#         self.enumerated: bool #: Is the property's value an enumerator?
#         self.hidden: bool #: Is the property hidden?
#         self.kind: str #: The kind of object or data returned by this property
#         self.listed: bool #: Is the property's value a list?

#     @property
#     def name(self) -> str:
#         return self.xa_elem.name()

#     @property
#     def id(self) -> str:
#         return self.xa_elem.id()

#     @property
#     def access(self) -> XASystemEventsAccs:
#         return self.xa_elem.access()

#     @property
#     def objectDescription(self) -> str:
#         return self.xa_elem.objectDescription()

#     @property
#     def enumerated(self) -> bool:
#         return self.xa_elem.enumerated()

#     @property
#     def hidden(self) -> bool:
#         return self.xa_elem.hidden()

#     @property
#     def kind(self) -> str:
#         return self.xa_elem.kind()

#     @property
#     def listed(self) -> bool:
#         return self.xa_elem.listed()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    

# class XASystemEventsScriptingResultObject(XABase.XAObject):
#     """A class for...
#     """
#     def __init__(self, properties):
#         super().__init__(properties)
        
#         self.objectDescription: str #: The description of the property
#         self.enumerated: bool #: Is the scripting result's value an enumerator?
#         self.kind: str #: The kind of object or data returned by this property
#         self.listed: bool #: Is the scripting result's value a list?

#     @property
#     def objectDescription(self) -> str:
#         return self.xa_elem.objectDescription()

#     @property
#     def enumerated(self) -> bool:
#         return self.xa_elem.enumerated()

#     @property
#     def kind(self) -> str:
#         return self.xa_elem.kind()

#     @property
#     def listed(self) -> bool:
#         return self.xa_elem.listed()

#     def closeSaving(self) -> None:
#         """Close a document.
#         """
#         return self.xa_elem.closeSaving_savingIn_(...)
    

#     def saveIn(self) -> None:
#         """Save a document.
#         """
#         return self.xa_elem.saveIn_as_(...)
    

#     def printWithProperties(self) -> None:
#         """Print a document.
#         """
#         return self.xa_elem.printWithProperties_printDialog_(...)
    

#     def delete(self) -> None:
#         """Delete an object.
#         """
#         return self.xa_elem.delete(...)
    

#     def duplicateTo(self) -> None:
#         """Copy an object.
#         """
#         return self.xa_elem.duplicateTo_withProperties_(...)
    

#     def moveTo(self) -> None:
#         """Move an object to a new location.
#         """
#         return self.xa_elem.moveTo_(...)
    



class XASystemEventsScriptingSuiteList(XABase.XAList):
    """A wrapper around lists of property list files that employs fast enumeration techniques.

    All properties of property list files can be called as methods on the wrapped list, returning a list containing each file's value for the property.

    .. versionadded:: 0.0.8
    """
    def __init__(self, properties: dict, filter: Union[dict, None] = None):
        super().__init__(properties, XASystemEventsScriptingSuite, filter)

    def name(self) -> List[str]:
        """Gets the name of each scripting suite in the list.

        :return: A list of scripting suite names
        :rtype: List[str]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("name"))

    def id(self) -> List[str]:
        """Gets the ID of each scripting suite in the list.

        :return: A list of scripting suite IDs
        :rtype: List[str]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("id"))

    def object_description(self) -> List[str]:
        """Gets the object description of each scripting suite in the list.

        :return: A list of scripting suite object descriptions
        :rtype: List[str]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("objectDescription"))

    def hidden(self) -> List[bool]:
        """Gets the hidden status of each scripting suite in the list.

        :return: A list of scripting suite hidden statuses
        :rtype: List[bool]
        
        .. versionadded:: 0.0.8
        """
        return list(self.xa_elem.arrayByApplyingSelector_("hidden"))

    def by_name(self, name: str) -> Union['XASystemEventsScriptingSuite', None]:
        """Retrieves the scripting suite whose name matches the given name, if one exists.

        :return: The desired scripting suite, if it is found
        :rtype: Union[XASystemEventsScriptingSuite, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("name", name)

    def by_id(self, id: str) -> Union['XASystemEventsScriptingSuite', None]:
        """Retrieves the scripting suite whose ID matches the given ID, if one exists.

        :return: The desired scripting suite, if it is found
        :rtype: Union[XASystemEventsScriptingSuite, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("id", id)

    def by_object_description(self, object_description: str) -> Union['XASystemEventsScriptingSuite', None]:
        """Retrieves the scripting suite whose object description matches the given description, if one exists.

        :return: The desired scripting suite, if it is found
        :rtype: Union[XASystemEventsScriptingSuite, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("objectDescription", object_description)

    def by_hidden(self, hidden: bool) -> Union['XASystemEventsScriptingSuite', None]:
        """Retrieves the first scripting suite whose hidden status matches the given boolean value, if one exists.

        :return: The desired scripting suite, if it is found
        :rtype: Union[XASystemEventsScriptingSuite, None]
        
        .. versionadded:: 0.0.8
        """
        return self.by_property("hidden", hidden)

    def __repr__(self):
        return "<" + str(type(self)) + str(self.name()) + ">"

class XASystemEventsScriptingSuite(XABase.XAObject):
    """A class for...
    """
    def __init__(self, properties):
        super().__init__(properties)
        
        self.name: str #: The name of the suite
        self.id: str #: The unique identifier of the suite
        self.objectDescription: str #: The description of the suite
        self.hidden: bool #: Is the suite hidden?

    @property
    def name(self) -> str:
        return self.xa_elem.name()

    @property
    def id(self) -> str:
        return self.xa_elem.id()

    @property
    def objectDescription(self) -> str:
        return self.xa_elem.objectDescription()

    @property
    def hidden(self) -> bool:
        return self.xa_elem.hidden()
    



# TODO ?
class XASystemEventsData(XABase.XAObject):
    """A class for...
    """
    def __init__(self, properties):
        super().__init__(properties)
        


# TODO: REMOVEEEEEE
class XASystemEventsList(XABase.XAObject):
    def __init__(self, properties):
        super().__init__(properties)
        