# -*- coding: utf-8 -*-


"""
Created on Fri Oct 29 09:32:34 2021

@author: Marc Boucsein 
"""


import numpy as np
import dask.array as da
import Partial_Aligner.utils as utils
from magicgui import magic_factory
from napari_plugin_engine import napari_hook_implementation
import napari.types
from napari.types import LayerDataTuple
import math 
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    import napari
    
from packaging.version import Version
from concurrent.futures import Future


global img_dim
img_dim= None
global img_shape
img_shape= None
global Tf_layers
Tf_layers={}
global prev_img_name_list
prev_img_name_list=[]
global aff_mat
aff_mat=None


def on_init(widget):
    """
    Initializes widget layout.
    Updates widget layout according to user input.
    """
    widget.native.setStyleSheet("QWidget{font-size: 12pt;}")
    
    
    for x in ['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Trans_z_Slider',
              'Scale_z_Slider', 'Shear_z_Slider', 'Shear_y_Slider',
              'Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
              'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
              'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
              'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box', 'Own_reg', 'label_layer_3D']:
           setattr(getattr(widget, x), 'visible', False)
    if Version(napari.__version__)<=Version('0.4.12'):
       setattr(getattr(widget, 'Drag_Drop_Interactivity'), 'visible', False)        
        
    
    def show_Own_reg(event):
        if img_dim==2:
               setattr(getattr(widget, 'label_layer_2D'), 'visible', True)
               setattr(getattr(widget, 'label_layer_3D'), 'visible', False)
               if getattr(widget, 'label_layer_2D').value=='None':
                   setattr(getattr(widget, 'Own_reg'), 'visible', False)
                   setattr(getattr(widget, 'Own_reg'), 'value', False)
               else:
                   setattr(getattr(widget, 'Own_reg'), 'visible', True)
                   setattr(getattr(widget, 'Own_reg'), 'value', False)
        if img_dim==3: 
               setattr(getattr(widget, 'label_layer_2D'), 'visible', False)
               setattr(getattr(widget, 'label_layer_3D'), 'visible', True)
               if getattr(widget, 'label_layer_3D').value=='None':
                   setattr(getattr(widget, 'Own_reg'), 'visible', False)
                   setattr(getattr(widget, 'Own_reg'), 'value', False)
               else:
                   setattr(getattr(widget, 'Own_reg'), 'visible', True)
                   setattr(getattr(widget, 'Own_reg'), 'value', False)  
                   

    def match_Spin_Slider(event):
        if getattr(widget, 'Absolute_Values').value:
             for x, y in zip(['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider'],[
                     'Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
                     'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
                     'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
                     'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box']):                       
                getattr(widget, y).value=getattr(widget, x).value
        else:
             for x, y in zip(['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider'],[
                     'Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
                     'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
                     'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
                     'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box']):
                getattr(widget, x).value=getattr(widget, y).value
            
    def Reset_Slider_func(event):
             for x in ['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider',
                     'Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
                     'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
                     'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box']:
                getattr(widget, x).value=0
             for x in ['Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                       'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box']:
                getattr(widget, x).value=1
    
    def save_slider_values(event):
        global Tf_layers
        global prev_img_name_list
        Tf_param_list=[]
        prev_img_name_list.append(getattr(widget, 'image').value.name)
        if getattr(widget, 'Absolute_Values').value:
             for x, y in zip(['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider'],[
                     'Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
                     'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
                     'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
                     'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box']):                       
                getattr(widget, x).value=getattr(widget, y).value
        else:
             for x, y in zip(['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider'],[
                     'Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
                     'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
                     'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
                     'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box']):
                getattr(widget, y).value=getattr(widget, x).value
        
        
        for x in ['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider',
                     'Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
                     'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
                     'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
                     'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box']:
                Tf_param_list.append(getattr(widget, x).value)
               
              
        try: 
             Tf_layers[prev_img_name_list[-2]] =  Tf_param_list

           
        except:
             pass 
         
        if str(getattr(widget, 'image').value.name) in Tf_layers: 
            for x, y in zip(['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider',
                     'Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
                     'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
                     'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
                     'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box'], Tf_layers[str(getattr(widget, 'image').value.name)]):
                getattr(widget, x).value=y

          
        

    def Slider_Dim_widget(event): 

        if img_dim==3 and not getattr(widget, 'Absolute_Values').value:
           for x in ['Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
              'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
              'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
              'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box','Drag_Drop_Interactivity']:
              setattr(getattr(widget, x), 'visible', False)
              setattr(getattr(widget, 'Drag_Drop_Interactivity'), 'value', False)
           for x in ['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider']:
               setattr(getattr(widget, x), 'visible', True)
        elif img_dim==3 and getattr(widget, 'Absolute_Values').value:
           for x in ['Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
              'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
              'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
              'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box']:
              setattr(getattr(widget, x), 'visible', True)
            
           for x in ['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider','Drag_Drop_Interactivity']:
               setattr(getattr(widget, x), 'visible', False)
               setattr(getattr(widget, 'Drag_Drop_Interactivity'), 'value', False)
        elif img_dim==2 and not getattr(widget, 'Absolute_Values').value:   
           for x in ['Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
              'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
              'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
              'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box', 'Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Trans_z_Slider',
              'Scale_z_Slider', 'Shear_y_Slider', 'Shear_z_Slider']:
              setattr(getattr(widget, x), 'visible', False)
            
           for x in ['Rot_angle_z_Slider',  
                     'Trans_x_Slider', 'Trans_y_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider',
                     'Shear_x_Slider','Drag_Drop_Interactivity']:
               setattr(getattr(widget, x), 'visible', True)
           setattr(getattr(widget, 'Drag_Drop_Interactivity'), 'value', False)    
           if Version(napari.__version__)<=Version('0.4.12'):
              setattr(getattr(widget, 'Drag_Drop_Interactivity'), 'visible', False)     
        elif img_dim==2 and  getattr(widget, 'Absolute_Values').value:  
           for x in ['Rot_angle_z_Box', 
              'Trans_x_Box', 'Trans_y_Box',
              'Scale_x_Box', 'Scale_y_Box',
              'Shear_x_Box', 'Drag_Drop_Interactivity']:
              setattr(getattr(widget, x), 'visible', True)
            
           for x in ['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider', 
                     'Rot_angle_x_Box', 'Rot_angle_y_Box', 'Trans_z_Box', 'Scale_z_Box', 'Shear_z_Box','Shear_y_Box'
                     ]:
               setattr(getattr(widget, x), 'visible', False)     
           setattr(getattr(widget, 'Drag_Drop_Interactivity'), 'value', False)           
           if Version(napari.__version__)<=Version('0.4.12'):
              setattr(getattr(widget, 'Drag_Drop_Interactivity'), 'visible', False) 
    
    def save_affine_func(event):
        global aff_mat
        if img_dim==2 and not getattr(widget, 'image').value.rgb:
           Outputfile=str(widget.Folder_Brower.value)+'/'+getattr(widget, 'image').value.name+'_Affine_2D'
        elif img_dim==2 and getattr(widget, 'image').value.rgb:
           Outputfile=str(widget.Folder_Brower.value)+'/'+getattr(widget, 'image').value.name+'_Affine_2D_RGB'
        elif img_dim==3:
           Outputfile=str(widget.Folder_Brower.value)+'/'+getattr(widget, 'image').value.name+'_Affine_3D' 
        
        if str(widget.Folder_Brower.value)!='.' and not widget.Drag_Drop_Interactivity.value:
           np.save(Outputfile,aff_mat)       
           
    def Slider_off_Drag(event):
        if widget.Drag_Drop_Interactivity.value:
           for x in ['Rot_angle_z_Box', 
              'Trans_x_Box', 'Trans_y_Box',
              'Scale_x_Box', 'Scale_y_Box',
              'Shear_x_Box','Rot_angle_z_Slider',  
              'Trans_x_Slider', 'Trans_y_Slider',
              'Scale_x_Slider', 'Scale_y_Slider',
              'Shear_x_Slider', 'Reset_Slider']:
              setattr(getattr(widget, x), 'visible', False) 
        else:
         if img_dim==2 and not getattr(widget, 'Absolute_Values').value:   
           for x in ['Rot_angle_x_Box','Rot_angle_y_Box', 'Rot_angle_z_Box', 
              'Trans_x_Box', 'Trans_y_Box', 'Trans_z_Box',
              'Scale_x_Box', 'Scale_y_Box', 'Scale_z_Box',
              'Shear_x_Box', 'Shear_y_Box', 'Shear_z_Box', 'Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Trans_z_Slider',
              'Scale_z_Slider', 'Shear_y_Slider', 'Shear_z_Slider']:
              setattr(getattr(widget, x), 'visible', False)
            
           for x in ['Rot_angle_z_Slider',  
                     'Trans_x_Slider', 'Trans_y_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider',
                     'Shear_x_Slider','Drag_Drop_Interactivity', 'Reset_Slider']:
               setattr(getattr(widget, x), 'visible', True)
           setattr(getattr(widget, 'Drag_Drop_Interactivity'), 'value', False)    
           
         if img_dim==2 and  getattr(widget, 'Absolute_Values').value:   
           for x in ['Rot_angle_z_Box', 
              'Trans_x_Box', 'Trans_y_Box',
              'Scale_x_Box', 'Scale_y_Box',
              'Shear_x_Box', 'Drag_Drop_Interactivity', 'Reset_Slider']:
              setattr(getattr(widget, x), 'visible', True)
            
           for x in ['Rot_angle_x_Slider', 'Rot_angle_y_Slider', 'Rot_angle_z_Slider', 
                     'Trans_x_Slider', 'Trans_y_Slider', 'Trans_z_Slider',
                     'Scale_x_Slider', 'Scale_y_Slider','Scale_z_Slider',
                     'Shear_x_Slider', 'Shear_y_Slider','Shear_z_Slider', 
                     'Rot_angle_x_Box', 'Rot_angle_y_Box', 'Trans_z_Box', 'Scale_z_Box', 'Shear_z_Box','Shear_y_Box'
                     ]:
               setattr(getattr(widget, x), 'visible', False)   
           setattr(getattr(widget, 'Drag_Drop_Interactivity'), 'value', False)
    
    def change_slider_to_drag(event):
        if not widget.Drag_Drop_Interactivity.value:
           from  napari.utils._magicgui import find_viewer_ancestor
           viewer = find_viewer_ancestor(widget) 
           
           if viewer.layers.selection.active.name == widget.image.value.name+'_Affine_2D' or viewer.layers.selection.active.name == widget.image.value.name+'_Affine_2D_RGB':
              Euler_rot=math.atan2(viewer.layers.selection.active.affine.rotate[1][0], viewer.layers.selection.active.affine.rotate[0][0])
              if Euler_rot<0:
                  Euler_rot=Euler_rot+2*np.pi
              Euler_rot_degree=utils.radtoangle(Euler_rot)    
              for x in ['Rot_angle_z_Box', 'Rot_angle_z_Slider']:
                  setattr(getattr(widget, x), 'value',  Euler_rot_degree)
              for x in ['Scale_y_Box', 'Scale_y_Slider']:
                  setattr(getattr(widget, x), 'value', viewer.layers.selection.active.affine.scale[0])   
              for x in ['Scale_x_Box', 'Scale_x_Slider']:
                  setattr(getattr(widget, x), 'value', viewer.layers.selection.active.affine.scale[1])       
              for x in ['Shear_x_Box', 'Shear_x_Slider']:
                  setattr(getattr(widget, x), 'value', viewer.layers.selection.active.affine.shear[0])   
              for x in ['Trans_y_Box', 'Trans_y_Slider']:
                  setattr(getattr(widget, x), 'value', viewer.layers.selection.active.affine.translate[0]/widget.image.value.data.shape[0]) 
              for x in ['Trans_x_Box', 'Trans_x_Slider']:
                  setattr(getattr(widget, x), 'value', viewer.layers.selection.active.affine.translate[1]/widget.image.value.data.shape[1])      
           
    def label_to_None(event): 
        
        setattr(getattr(widget, 'label_layer_2D'), 'value', "None")
        setattr(getattr(widget, 'label_layer_3D'), 'value', "None") 
        
    def translate_to_shape(event):
      if img_dim==2:  
        setattr(getattr(widget, 'Trans_y_Box'), 'step', 1/img_shape[0])  
        setattr(getattr(widget, 'Trans_x_Box'), 'step', 1/img_shape[1])
        setattr(getattr(widget, 'Trans_y_Slider'), 'step', 1/img_shape[0]) 
        setattr(getattr(widget, 'Trans_x_Slider'), 'step', 1/img_shape[1])
      elif img_dim==3:
        setattr(getattr(widget, 'Trans_z_Box'), 'step', 1/img_shape[0])  
        setattr(getattr(widget, 'Trans_y_Box'), 'step', 1/img_shape[1])
        setattr(getattr(widget, 'Trans_x_Box'), 'step', 1/img_shape[2]) 
        setattr(getattr(widget, 'Trans_z_Slider'), 'step', 1/img_shape[0]) 
        setattr(getattr(widget, 'Trans_y_Slider'), 'step', 1/img_shape[1])  
        setattr(getattr(widget, 'Trans_x_Slider'), 'step', 1/img_shape[2]) 
 
          



        
    widget.Drag_Drop_Interactivity.changed.connect(Slider_off_Drag)
    widget.Drag_Drop_Interactivity.changed.connect(change_slider_to_drag)
    widget.label_layer_2D.changed.connect(show_Own_reg)
    widget.label_layer_3D.changed.connect(show_Own_reg)
    widget.Absolute_Values.changed.connect(Slider_Dim_widget)
    widget.Absolute_Values.changed.connect(match_Spin_Slider)
    widget.image.changed.connect(save_slider_values)
    widget.image.changed.connect(label_to_None)
    widget.image.changed.connect(Slider_Dim_widget)
    widget.image.changed.connect(show_Own_reg)
    widget.image.changed.connect(translate_to_shape)
    
    
    #widget.image.changed.connect(match_Spin_Slider)
    widget.Reset_Slider.changed.connect(Reset_Slider_func)
    widget.Save_affine.changed.connect(save_affine_func)
    widget.native.layout().addStretch()
    
def all_label_layers_2D(gui)->List[str]:
     from  napari.utils._magicgui import find_viewer_ancestor
     viewer = find_viewer_ancestor(gui.native)
     if not viewer:
         return []
     possible_label_layers_2D= [x.name  for x in viewer.layers if (isinstance(x, napari.layers.labels.labels.Labels) and len(x.data.shape)==2 and x.data.shape==img_shape)]
     possible_label_layers_2D.append("None")
     
     return possible_label_layers_2D
 
def all_label_layers_3D(gui)->List[str]:
     from  napari.utils._magicgui import find_viewer_ancestor
     viewer = find_viewer_ancestor(gui.native)
     if not viewer:
         return []
     possible_label_layers_3D= [x.name  for x in viewer.layers if (isinstance(x, napari.layers.labels.labels.Labels) and len(x.data.shape)==3 and x.data.shape==img_shape)]
     possible_label_layers_3D.append("None")
     
     return possible_label_layers_3D    

def all_image_layers(gui)->List[napari.layers.Layer]:
     from  napari.utils._magicgui import find_viewer_ancestor
     viewer = find_viewer_ancestor(gui.native)
     if not viewer:
         return []
     possible_image_layers= [x  for x in viewer.layers if (isinstance(x, napari.layers.image.image.Image) and 2<=len(x.data.shape)<=3 
                                                           and not x.name.endswith('_fixed')  and not x.name.endswith('Affine_2D')  
                                                           and not x.name.endswith('Affine_2D_RGB') and not x.name.endswith('Affine_3D'))]
     return possible_image_layers

@magic_factory(widget_init=on_init, layout='vertical', 
               auto_call=True,
               image={"widget_type": "ComboBox", 'label': 'Image', 'choices': all_image_layers, 'tooltip':'The image we work on'},
               label_layer_2D={"widget_type": "ComboBox", 'label': 'Label', 'choices': all_label_layers_2D, 'tooltip':'choose to transform only a labeled part of the image; choice defines which label'},
               label_layer_3D={"widget_type": "ComboBox", 'label': 'Label', 'choices': all_label_layers_3D, 'tooltip':'choose to transform only a labeled part of the image; choice defines which label'},
               Absolute_Values={"widget_type": "CheckBox", 'value': False, 'text': 'Absolute values', 'tooltip':'changes the controls for transformation parameters from sliders to absolute values'},
               Own_reg={"widget_type": "CheckBox", 'value': False, 'text': 'Own Part-Alignment','tooltip':'creates an image without the labeled parts'}, 
               Drag_Drop_Interactivity={"widget_type": "CheckBox", 'value': False, 'text': 'Drag&Drop 2D Interactivity', 'tooltip':'toggles drag&drop based transformation (2D only)'},
               Rot_angle_x_Box={"widget_type": "FloatSpinBox", 'max': 360, 'step': 0.1, 'label': 'Rotation angle x'},
               Rot_angle_y_Box={"widget_type": "FloatSpinBox", 'max': 360, 'step': 0.1, 'label': 'Rotation angle y'},
               Rot_angle_z_Box={"widget_type": "FloatSpinBox", 'max': 360, 'step': 0.1, 'label': 'Rotation angle z'},
               Rot_angle_x_Slider={"widget_type": "FloatSlider", 'max': 360, 'step': 0.1, 'label': 'Rotation angle x'},
               Rot_angle_y_Slider={"widget_type": "FloatSlider", 'max': 360, 'step': 0.1, 'label': 'Rotation angle y'},
               Rot_angle_z_Slider={"widget_type": "FloatSlider", 'max': 360, 'step': 0.1, 'label': 'Rotation angle z'},
               Trans_x_Box={"widget_type": "FloatSpinBox", 'min': -1, 'max': 1, 'step': 0.01, 'label': 'Translation x'},
               Trans_y_Box={"widget_type": "FloatSpinBox", 'min': -1,'max': 1,  'step': 0.01, 'label': 'Translation y'}, 
               Trans_z_Box={"widget_type": "FloatSpinBox", 'min': -1, 'max': 1,  'step': 0.01, 'label': 'Translation z'},
               Trans_x_Slider={"widget_type": "FloatSlider", 'min': -1, 'max': 1, 'step': 0.01, 'label': 'Translation x'},
               Trans_y_Slider={"widget_type": "FloatSlider", 'min': -1,'max': 1,  'step': 0.01, 'label': 'Translation y'}, 
               Trans_z_Slider={"widget_type": "FloatSlider", 'min': -1, 'max': 1,  'step': 0.01, 'label': 'Translation z'},
               Scale_x_Box={"widget_type": "FloatSpinBox", 'value': 1, 'min': 0.01, 'max': 10, 'step': 0.01, 'label': 'Scale x'},
               Scale_y_Box={"widget_type": "FloatSpinBox",'value': 1, 'min': 0.01,'max': 10,  'step': 0.01, 'label': 'Scale y'}, 
               Scale_z_Box={"widget_type": "FloatSpinBox", 'value': 1,'min': 0.01, 'max': 10,  'step': 0.01, 'label': 'Scale z'},
               Scale_x_Slider={"widget_type": "FloatSlider", 'value': 1, 'min': 0.01, 'max': 10, 'step': 0.01, 'label': 'Scale x'},
               Scale_y_Slider={"widget_type": "FloatSlider", 'value': 1, 'min': 0.01,'max': 10,  'step': 0.01, 'label': 'Scale y'}, 
               Scale_z_Slider={"widget_type": "FloatSlider", 'value': 1, 'min': 0.01, 'max': 10,  'step': 0.01, 'label': 'Scale z'},
               Shear_x_Box={"widget_type": "FloatSpinBox", 'min': -1, 'max': 1, 'step': 0.01, 'label': 'Shear x'},
               Shear_y_Box={"widget_type": "FloatSpinBox", 'min': -1,'max': 1,  'step': 0.01, 'label': 'Shear y'}, 
               Shear_z_Box={"widget_type": "FloatSpinBox", 'min': -1, 'max': 1,  'step': 0.01, 'label': 'Shear z'},
               Shear_x_Slider={"widget_type": "FloatSlider", 'min': -1, 'max': 1, 'step': 0.01, 'label': 'Shear x'},
               Shear_y_Slider={"widget_type": "FloatSlider", 'min': -1,'max': 1,  'step': 0.01, 'label': 'Shear y'}, 
               Shear_z_Slider={"widget_type": "FloatSlider", 'min': -1, 'max': 1,  'step': 0.01, 'label': 'Shear z'},
               Reset_Slider={"widget_type": "PushButton", 'text': 'Reset', 'tooltip':'reset transformation values to original'},
               Folder_Brower={"widget_type": "FileEdit", 'label': 'Path', 'mode':'d', 'tooltip':'where to save the transformation matrix?'},
               Save_affine={"widget_type": "PushButton", 'text': 'Save affine matrix', 'tooltip':'only effective if a directory is chosen above'})
def Aligner(viewer: 'napari.viewer.Viewer',
    image: 'napari.layers.Image', label_layer_2D: str, label_layer_3D: str, 
    Rot_angle_x_Slider: float,  
    Rot_angle_y_Slider: float, Rot_angle_z_Slider: float, 
    Trans_x_Slider: float, Trans_y_Slider: float, Trans_z_Slider: float,
    Scale_x_Slider: float, Scale_y_Slider: float, Scale_z_Slider: float, 
    Shear_x_Slider: float, Shear_y_Slider: float, Shear_z_Slider: float,
    Rot_angle_x_Box: float,  
    Rot_angle_y_Box: float, Rot_angle_z_Box: float, 
    Trans_x_Box: float, Trans_y_Box: float, Trans_z_Box: float,
    Scale_x_Box: float, Scale_y_Box: float, Scale_z_Box: float, 
    Shear_x_Box: float, Shear_y_Box: float, Shear_z_Box: float,
    Reset_Slider: bool,
    Folder_Brower: str,
    Save_affine: bool,
    Absolute_Values: bool= False,  Own_reg: bool=False, Drag_Drop_Interactivity : bool= False
) -> Future[LayerDataTuple]:
    

                   
    def on_transform_changed_drag(event):
        global aff_mat

        aff_mat_drag= event.value @ aff_mat
        viewer.layers.selection.active.affine = aff_mat_drag
    
    def on_off_drag_drop(event):
           selection_list=[s for s in viewer.layers.selection]
           if (Drag_Drop_Interactivity and len(selection_list)!=1) or len(selection_list)!=1 :
             viewer.overlays.interaction_box.show = False
             viewer.overlays.interaction_box.show_vertices = False
             viewer.overlays.interaction_box.show_handle = False
             #viewer.overlays.interaction_box.allow_new_selection = False
           

             try: 
              viewer.layers.selection.active.interactive = True
             except:
              pass

            
    
    
    if image is not None:
       from napari.qt import thread_worker
    
       future: Future[LayerDataTuple] = Future()
    
       def _on_done(result, self=Aligner):
           future.set_result(result)  

       global prev_img_name
       prev_img_name=image.name
       
       img=image.data 
       if isinstance(img, da.core.Array):
          img_dask=img
       else:
          img_dask=da.from_array(img) 

       
       global img_dim
       img_dim=len(image.data.shape)
       global img_shape
       img_shape=image.data.shape
       if image.rgb and img_dim==3:
           img_dim=2
           img_shape=img_shape[:2] 
       
       
       if Absolute_Values:
          Rot_angle_x= Rot_angle_x_Box
          Rot_angle_y= Rot_angle_y_Box
          Rot_angle_z= Rot_angle_z_Box
          Trans_x=Trans_x_Box
          Trans_y=Trans_y_Box
          Trans_z=Trans_z_Box
          Scale_x=Scale_x_Box
          Scale_y=Scale_y_Box
          Scale_z=Scale_z_Box
          Shear_x=Shear_x_Box
          Shear_y=Shear_y_Box
          Shear_z=Shear_z_Box
       else:
          Rot_angle_x= Rot_angle_x_Slider
          Rot_angle_y= Rot_angle_y_Slider
          Rot_angle_z= Rot_angle_z_Slider
          Trans_x=Trans_x_Slider
          Trans_y=Trans_y_Slider
          Trans_z=Trans_z_Slider
          Scale_x=Scale_x_Slider
          Scale_y=Scale_y_Slider
          Scale_z=Scale_z_Slider
          Shear_x=Shear_x_Slider
          Shear_y=Shear_y_Slider
          Shear_z=Shear_z_Slider 
        
        

       selection_list=[s for s in viewer.layers.selection]
       Layer_for_Drag=[layer for layer in viewer.layers if (layer.name==image.name+'_Affine_2D' or layer.name==image.name+'_Affine_2D_RGB')]
       viewer.layers.events.inserting.connect(on_off_drag_drop)
       viewer.layers.selection.events.changed.connect(on_off_drag_drop)


       if Drag_Drop_Interactivity:

          
           
           if viewer.layers.ndim==2 and len(selection_list) == 1  and Version(napari.__version__)>Version('0.4.12'):
              if Layer_for_Drag: 
                viewer.layers.selection.active=Layer_for_Drag[0]

              viewer.layers.selection.active.interactive = False
              viewer.overlays.interaction_box.points = viewer.layers.selection.active.extent.world
              viewer.overlays.interaction_box.show = True
              viewer.overlays.interaction_box.show_vertices = True
              viewer.overlays.interaction_box.show_handle = True
              viewer.overlays.interaction_box.events.transform_drag.connect(on_transform_changed_drag)
           else:
             try: 
              viewer.layers.selection.active.interactive = True
              viewer.overlays.interaction_box.show = False
              viewer.overlays.interaction_box.show_vertices = False
              viewer.overlays.interaction_box.show_handle = False
 

              Drag_Drop_Interactivity=False
             except:
              pass   
               
           
       else:
           if len(selection_list) ==1 and Version(napari.__version__)>Version('0.4.12'):
              viewer.layers.selection.active.interactive = True
              viewer.overlays.interaction_box.show = False
              viewer.overlays.interaction_box.show_vertices = False
              viewer.overlays.interaction_box.show_handle = False
              #viewer.overlays.interaction_box.allow_new_selection = False

        

          
          
           
       if  img_dim==2 and not image.rgb:
           @thread_worker
           def affine_2d():
              
               if label_layer_2D=='None' or label_layer_2D is None:
                     img_part=img_dask.copy()
                     
               else:
                     label=viewer.layers[label_layer_2D]
                     lb= label.data
                     img_part=img_dask.copy()
                     img_part[da.ma.getmaskarray(da.ma.masked_equal(lb, 0))]=0
                   
                     if Own_reg:
                        img_remaining=img_dask.copy()
                        img_remaining[da.ma.getmaskarray(da.ma.masked_not_equal(lb, 0))]=0
                        
                     else:
                        pass   
                               
               global aff_mat
         
               Trans_y_full=image.data.shape[0]*Trans_y
               Trans_x_full=image.data.shape[1]*Trans_x
               linear_matrix=napari.utils.transforms.transform_utils.compose_linear_matrix(Rot_angle_z, np.array([Scale_y,Scale_x]), [Shear_x])
               linear_mat_Trans=np.concatenate( (linear_matrix, [[Trans_y_full],[Trans_x_full]]), axis=1, dtype=linear_matrix.dtype)
               aff_mat_reg=np.concatenate( (linear_mat_Trans, [[0,0,1]]), axis=0, dtype=linear_matrix.dtype) 
               scale_mat_res=np.array([[image.scale[0],0,0],[0,image.scale[1],0],[0,0,1]])
               aff_mat=scale_mat_res @ aff_mat_reg
             
               kwargs={'name': image.name+'_Affine_2D', 'affine': aff_mat, 'blending': 'additive'}
               Layerdattup=(img_part, kwargs, 'image')
               if not Own_reg:
                  return Layerdattup
               else:
                  return [(img_remaining, {'name': image.name+'_Affine_2D_fixed', 'visible':True, 'blending': 'additive'}, 'image'),Layerdattup]                     
           worker = affine_2d()
           worker.returned.connect(_on_done)
           worker.start()
           
           return future
       
       elif img_dim==2 and image.rgb:
           @thread_worker
           def affine_2d_RGB():
               if label_layer_2D=='None' or label_layer_2D is None:
                     img_part=img_dask.copy()
               else:
                     label=viewer.layers[label_layer_2D]
                     lb= label.data
                     lb_stack=da.stack(3*[da.from_array(lb)],axis=2)
                     img_part=img_dask.copy()
                     img_part[da.ma.getmaskarray(da.ma.masked_equal(lb_stack, 0))]=0
                     if Own_reg:
                        img_remaining=img_dask.copy()
                        img_remaining[da.ma.getmaskarray(da.ma.masked_not_equal(lb_stack, 0))]=0
                     else:
                        pass 
               
               global aff_mat
                     
               Trans_y_full=image.data.shape[0]*Trans_y
               Trans_x_full=image.data.shape[1]*Trans_x 
               
               linear_matrix=napari.utils.transforms.transform_utils.compose_linear_matrix(Rot_angle_z, np.array([Scale_y,Scale_x]), [Shear_x])
               linear_mat_Trans=np.concatenate( (linear_matrix, [[Trans_y_full],[Trans_x_full]]), axis=1, dtype=linear_matrix.dtype)
               aff_mat_reg=np.concatenate( (linear_mat_Trans, [[0,0,1]]), axis=0, dtype=linear_matrix.dtype) 
               scale_mat_res=np.array([[image.scale[0],0,0],[0,image.scale[1],0],[0,0,1]])
               aff_mat=scale_mat_res @ aff_mat_reg
               
               kwargs={'name':  image.name+'_Affine_2D_RGB',   'rgb':True, 'affine': aff_mat, 'blending': 'additive'} 
               Layerdattup=(img_part, kwargs, 'image')
               if not Own_reg:
                  return Layerdattup
               else:
                  return [(img_remaining, {'name':  image.name+'_Affine_2D_RGB_fixed', 'visible':True, 'blending': 'additive'}, 'image'),Layerdattup] 
           worker = affine_2d_RGB()
           worker.returned.connect(_on_done)
           worker.start()
           
           return future
           
           
           
       elif img_dim==3 and not image.rgb:
           @thread_worker
           def affine_3d():

               if label_layer_3D=='None' or label_layer_3D is None: 
                     img_part=img_dask.copy()
               else:
                     label=viewer.layers[label_layer_3D]
                     lb= label.data
                     img_part=img_dask.copy()
                     img_part[da.ma.getmaskarray(da.ma.masked_equal(lb, 0))]=0
                   
                     if Own_reg:
                        img_remaining=img_dask.copy()
                        img_remaining[da.ma.getmaskarray(da.ma.masked_not_equal(lb, 0))]=0
                        
                     else:
                        pass 
                
               global aff_mat  
                
               Trans_z_full=image.data.shape[0]*Trans_z
               Trans_y_full=image.data.shape[1]*Trans_y
               Trans_x_full=image.data.shape[2]*Trans_x
               
               linear_matrix=napari.utils.transforms.transform_utils.compose_linear_matrix([Rot_angle_x,Rot_angle_y,Rot_angle_z], np.array([Scale_z, Scale_y,Scale_x]), utils.shear_matrix_3D(Shear_x, Shear_y, Shear_z))
               linear_mat_Trans=np.concatenate( (linear_matrix, [[Trans_z_full],[Trans_y_full],[Trans_x_full]]), axis=1, dtype=linear_matrix.dtype)
               aff_mat_reg=np.concatenate( (linear_mat_Trans, [[0,0,0,1]]), axis=0, dtype=linear_matrix.dtype)    
               scale_mat_res=np.array([[image.scale[0],0,0,0],[0,image.scale[1],0,0],[0,0,image.scale[2],0],[0,0,0,1]])
               aff_mat=scale_mat_res @ aff_mat_reg
               
               kwargs={'name':  image.name+'_Affine_3D', 'affine': aff_mat, 'blending': 'additive'}
               Layerdattup=(img_part, kwargs, 'image')
               if not Own_reg:
                  return Layerdattup
               else:
                  return [(img_remaining, {'name':  image.name+'_Affine_3D_fixed', 'visible':True, 'blending': 'additive'}, 'image'), Layerdattup] 
           worker = affine_3d()
           worker.returned.connect(_on_done)
           worker.start()
           
           return future 
           
       else:
           print("Just 2D/3D support")
           return

       
    else:
       return


    

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return Aligner


