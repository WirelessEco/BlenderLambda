import boto3
import sys
import bpy
import bmesh

s3 = boto3.client('s3')
bucket = 'blender-lambda-evantobin91384'

#Returns the combined length, or perimeter, of all edges selected 
def get_combined_length(object_data, edge_list):
    edge_length = 0
    for edge in edge_list:
        vert1 = edge.vertices[0]
        vert2 = edge.vertices[1]
        co1 = object_data.vertices[vert1].co  
        co2 = object_data.vertices[vert2].co  
        edge_length += (co1-co2).length
        
    return edge_length


#Deletes all objects in the scene
def delete_all():
    if bpy.context.object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.data.objects:
        ob.select_set(True)
        bpy.ops.object.delete()


#Returns the sum of all interesecting edges if a plane were to bisect the selected object at the given height(inches)
def getCircumference(height):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.active_object.select_set(state=True)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(0, 0, height), plane_no=(0, 0, 1), use_fill=True, clear_inner=False, clear_outer=False, threshold=0.0001, xstart=0, xend=0, ystart=0,  yend=0, flip=False, cursor=5)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    object_data = bpy.context.active_object.data
    selected_edges = [edge for edge in object_data.edges if edge.select]
    summed_length = get_combined_length(object_data, selected_edges)
    print(f"Circumference at {height} inches above the knee: " + str(round(summed_length,3)))
    return(str(round(summed_length,3)))

def getDiameter(height):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.active_object.select_set(state=True)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(0, 0, height), plane_no=(0, 0, 1), use_fill=True, clear_inner=False, clear_outer=False, threshold=0.0001, xstart=0, xend=0, ystart=0,  yend=0, flip=False, cursor=5)

    bpy.ops.object.mode_set(mode='OBJECT')
    vertices = [i.co for i in bpy.context.active_object.data.vertices if i.select]
    #Returns the indices of the two vertices along the closest to the x-axis
    def getXPoints():
        lowestXIndex = 0
        highestXIndex = 0
        
        for i in range(len(vertices)):
            if(abs(vertices[i].y) < abs(vertices[lowestXIndex].y) and vertices[i].x < 0):
                lowestXIndex = i
            if(abs(vertices[i].y) < abs(vertices[lowestXIndex].y) and vertices[i].x > 0):
                highestXIndex = i
        
        return([vertices[lowestXIndex], vertices[highestXIndex]])
        
    diameter = abs(getXPoints()[0].x) + abs(getXPoints()[1].x)
    print(f"Diameter at {height} inches above the knee: " + str(round(diameter,3)))
    return(str(round(diameter,3)))


def handler_return():
    delete_all()
    bpy.ops.import_mesh.stl(filepath="/tmp/Leg.stl", filter_glob="*.stl",  files=[{"name":"Leg.stl", "name":"Leg.stl"}], directory="/tmp/")
    bpy.data.objects['Leg'].select_set(True)

    #Circumferences
    thigh = getCircumference(height=4.00)
    knee_width = getDiameter(height=0.00)
    calf = getCircumference(height=-4.00)
    outputFileName = 'bpyScript_output.txt'

    #Write to a .txt file in the /tmp/ directory the output of the script
    with open('/tmp/' + outputFileName, 'w') as f:
        f.write(str(thigh) + '\n')
        f.write(str(knee_width) + '\n')
        f.write(str(calf) + '\n')

handler_return()
