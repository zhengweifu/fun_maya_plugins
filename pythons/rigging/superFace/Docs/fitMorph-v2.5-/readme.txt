-------------------------------------------------------------------------------------
 	M a y a   	F I T  	 	M O R P H     v 2.5!
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------

Install Instructions:

	1. Copy the mel script (fitMorph.mel) to your local user/scripts folder:
		(win2000 example path to mel scripts folder): 
		C:\Documents and Settings\*USERNAME*\My Documents\maya\#.#\scripts	  
	
	2.  Copy the icon file (fitIcon.bmp) to your user/prefs/icons folder:
		(win2000 example path to icons folder): 
		C:\Documents and Settings\*USERNAME*\My Documents\maya\#.#\prefs\icons	  

   	3. Then type:						  
		source fitMorph.mel;						  
		into the Maya command line.
		
	4. Then, MAKE SURE YOUR SHELF IS VISIBLE, and type:									  								  
 		installFitMorph;						  
 		into the Maya command line.

 	You should now have a new shelf button, click it, and you will get the script's Ui...
 	The buttons all have roll-over annotations, and should be pretty self explanatory,
 	once you press them. Selection order is always the target object last.


-----------------------------------------------------------------------------------
-----------------------------------------------------------------------------------
Updates:
-----------------------------------------------------------------------------------
___
v1.1 
* Added a couple usability fixes/updates, selection order is now consistent. 

* Selection order doesn’t get modified by executing functions anymore, i.e. script
 restores original selection if it ever needs to change it in the code. 
___ 
v1.5 
*Added Entire New feature set, with a whole new set of snapping and flattening 
functions, which can be good to use before you actually perform the "shrink wrap" 
in order to remove any unwanted surface curvature: 

	1) Scale to Zero @ Center of Selection Pivot: 
	This feature will let you quickly flatten out a selected 
	set of vertices, or objects, along the selected axis. This
	is useful if you want to have a "snap to grid" behavior,
	in order to flatten out the vertices (or anything selected) 
	along the same plane, and you want them to be flattened 
	according to the selection's relative axis and location, 
	as opposed to flattened across, onto the grid. 
	
	2) Bounding Box Snap: 
	This feature will snap the selected vertices (or anything selected) 
	on an object to it's own bounding box edge. This is also very useful 
	for flattening vertices onto a single plane, but without having to be 
	forced to snap them to the grid, it still snaps them to the "world's" 
	axis. The script will snap them to the bounding box edge of the object 
	that contains them, options are the min or max of each axis. 
___ 
v2.0 
*Added Entire New feature set, "Interactive Fit". This tab layout of the 
UI will allow you to interactively decide whether or not you want to snap the
components to the surface, one at a time. Define an interactive session by 
first selecting the verts and the target surface last, and then the UI allows 
you to pick walk through your component selection, whether it is polygon, nurbs, 
or subdiv, you can pick walk through the vertices, and snap them one by one, 
deciding for each one if that particular vert should or shouldn’t be snapped 
onto the target surface. 
___ 
v2.1 
*Two small history based bug fixes that caused history to get deleted on the 
component snap function are fixed in this update. 
___ 
v2.2 
*Fixed a couple error checking routines and added an option to clear the 
globals for the "Interactive Fit" session.
___ 
v2.5
*Added 2 New Features: 
	(Polygon Vertex Only) 
	1. Move Along Averaged Vertex Normal.  This moves selection of poly 
	   vertices outward, in the direction of the averaged normal.
	   The vert is moved in the outward direction that it's average
	   normal is pointing, and the amount it is moved is determined
	   by a slider bar that has 3 levels of precision for highly
	   accurate vertex translations.
	2. Relax Vertices. This siply uses the polyAverageVertex command to "smooth"
	   the vertex locations.  The amount (iterations) is determined once
	   again, by a slider bar.  


-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------

Description:
		Several cool functions to fit selected objects or components
		into the shape of other selected objects. Options include 
		snapping to objects, fitting to bounding box, and wrapping one
		shape to another object shape, as sort of a "lite" 3d morphing 
		capability. It uses a tricky way of calculating the closest 
		point on the target surface, which requires no plugins or complex 
		data sturctures, or slow vector / magnitude math calculations :-D

		Example: This script will  move the vertices on a cube,
		and turn it into a sphere, quite easily; making it possible to 
		do things like a resolution independent blend shape from a cube 
		to a sphere! The script	gets less accurate and takes much 
		longer to calculate when working with hires, complex models,
		so beware. This script will *NOT* morph a dog into a beautiful 
		female...  but it would probably morph a dog into a simple
		spaceship pretty well.  Works on polygons much much better than
		nurbs, although it is fine to use nurbs as the target surface.
		I suggest using lowres polygons as the surface to morph. Have fun
		and enjoy!

-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------

Limitations / bugs:

	Maybe a few :-)
	Email me if there are any nasty ones, or with suggestions...

-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------	



