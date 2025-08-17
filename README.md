
#### **Addon Location: 3D View -> N-Panel -> K-Tools -> Sync | Lock Viewport**

### View Synchronization Panel:
#### Single Match:
Allow the user to Match all the selected view from the Available Views List only once, not a live syncing. (If nothing happens, please refresh the Available View List first)
#### Real-time Sync:
Allow the user to constantly sync all the selected views from the Available View List. All the views will be masked as True by default. While this option is running the View List will be refreshed constantly.
#### Master View control:
This will be the index of the Viewport that will control all the other views marked as True in the Available View List. Note that the index of the view not always is logical. For to know what is the index of the view what you are in, please use the button *Identify View*, or, in the desired Viewport, use the Button *Set Current as Master*.
#### Customizable Refresh Rate:
The Refresh Rate is how often the selected viewports will be updated, the lower the value, the faster they will be updated. 
Note: As it will make a constant update on Blender Viewport the Gizmos of Move, Rotate and Scale will not work as expected, if you want to use the Transform Gizmos while the *Real-Time Sync* is on choose a higher *Refresh Rate*. 
#### Auto Master:
This option when On, will automatically switch the *Master View* index, allowing the user to navigate between the Viewports and Syncing the other ones always.
#### Set Current View as Master:
This option will set the *Master View* index based where this button was pressed.
#### Available Views List:
The list will be Populated with the Available Views, if the user have other windows with 3D Views they will also be shown in the List.
#### Identify View:
This will show a *Text* saying the view index for each 3D View Opened
#### Refresh List:
if for any reason nothing is shown in the *Available Views* List, use this button to force the Refresh for the List.
#### Local View: 
This is an upgraded operator that works as the default one from Blender, the difference is that it will also set the Selected Objects in Local View mode in all Views at once.
If the ***Keep Lights***  Boolean is on, this will keep the *Visible Lights* in the scene while Isolating an object.

---
## Sync Options (Dropdown Menu):

These options control what will be updated in the Synced Views.

Input Fields:
- **Adjust View Distance:** It is a multiplier that allows the user control how much ‘zoom’ will have on the controlled Views, this is useful when the aspect ratio of the controlled view is different from the Master View.    

- **Clip Start | End:** Default Blender view clipping - "Clip Start/End adjusts the minimum and maximum distance range to limit the visible range to the area between two planes that are orthogonal to the viewing direction of the viewport camera. Objects outside this range will not be shown." - Blender Manual*    

- **Focal Length:** Blender's default option - "Control the focal length of the 3D Viewport camera in millimeters, unlike a rendering camera." Blender Manual*    

- **Local View:** This is an upgraded operator that works as the default one from Blender, the difference is that it will also set the Selected Objects in Local View mode in all Views at once.

Boolean Buttons:
- **Distance**: Updates camera distance when true.
- **Location**: Updates camera location when true.
- **Rotation**: Updates camera rotation when true.
- **Camera Zoom**: Updates camera zoom when true.
- **Camera Offset**: Updates camera offset when true.
- **Perspective**: Updates view perspective when true.
- **Clip Start**: Updates view clipping start when true.
- **Clip End**: Updates view clipping end when true.
- **Focal Length**: Updates focal length when true.

### Lock Rotation System:
#### Available Views List:
The list will be Populated with the Available Views, if the user have other windows with 3D Views they will also be shown in the List.
	For each view in the list the user is able to lock the desired Viewport in the Predefined Views as: Top, Bottom, Right, Left Front and Back, Camera or the *Matching View* of the *Master Viewport*
	(same as the default Blender Numerical Pad 1, 3, 7 and etc.) 
#### Identify View:
This will show a *Text* saying the view index for each 3D View Opened
#### Refresh List:
if for any reason nothing is shown in the *Available Views* List, use this button to force the Refresh for the List.
#### Set Clean View:
It will ‘clean’ the view that is Locked, the header, default gizmos and overlays will be disabled, they appear again when you click the button once more.
#### Special Gizmos:
Show in the Locked Viewport the following buttons:  *Toggle Solid Shading*; *Toggle Material Shading*; *Toggle Render Preview*; *Shading Menu Popover*; *Set Camera View*; *Move the View* and *Zoom in/out*.


