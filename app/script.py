import os
import sys
import boto3
import bpy

s3 = boto3.client('s3')

bucket = 'blender-lambda-evantobin91384'
key = 'Leg.stl'

s3.download_file(bucket, key, '/tmp/' + key)


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
def bisect(height):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.active_object.select_set(state=True)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(0, 0, height), 
                        plane_no=(0, 0, 1), #Pointing up
                        use_fill=True, 
                        clear_inner=False, 
                        clear_outer=False, 
                        threshold=0.0001, 
                        xstart=0, 
                        xend=0, 
                        ystart=0, 
                        yend=0, 
                        flip=False, 
                        cursor=5
                    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
    object_data = bpy.context.active_object.data
    selected_edges = [edge for edge in object_data.edges if edge.select]
    summed_length = get_combined_length(object_data, selected_edges)
    return(f"Circumference at {height} inches above the knee: " + str(round(summed_length,3)))



delete_all()
bpy.ops.import_mesh.stl(filepath="/tmp/Leg.stl", filter_glob="*.stl",  files=[{"name":"Leg.stl", "name":"Leg.stl"}], directory="/tmp/")
bpy.data.objects['Leg'].select_set(True)

circumference = bisect(height=4.00)     #Circumference of the leg

outputFileName = 'leg0001_circumference.txt'

with open('/tmp/' + outputFileName, 'w') as f:      #Write to a .txt file in the /tmp/ directory the output of the script
    f.write(str(circumference))

s3.upload_file('/tmp/' + outputFileName, bucket, outputFileName)        #Upload the output of the script to S3