import os
import numpy as np
import open3d as o3d
import json
import pyviz3d.visualizer as viz

from plyfile import *
import numpy as np

scenes = ['office_0', 'office_1', 'office_2', 'office_3', 'office_4', 'room_0', 'room_1', 'room_2']
# scenes = ['office_0']

invalid_class_names = ''

def show_individual_objects(objects, points, colors, info_semantic):
    v = viz.Visualizer()
    for id, faces in sorted(objects.items()):
        class_label = ''
        class_id = 999
        for obj in info_semantic['objects']:
            if obj['id'] == id:
                class_label = obj['class_name']
                class_id = obj['class_id']
                break
        point_ids = np.unique(np.concatenate([f[0] for f in faces]))
        object_positions = points[point_ids]
        object_colors = colors[point_ids]
        print(object_positions.shape)
        v.add_points(f'{id}_{class_id}_{class_label}', object_positions, object_colors, point_size=25, visible=False)
    v.save('example_point_clouds/asd')


def export_to_scannet_format(objects, info_semantic, scene_name):
    per_point_labels = np.zeros(points.shape[0])
    for id, faces in sorted(objects.items(), key=lambda item: len(item[1]), reverse=True):
        class_id = 0
        for obj in info_semantic['objects']:
            if obj['id'] == id:
                class_id = obj['class_id']
                break
        if class_id == -1:
            class_id = 0
        point_ids = np.unique(np.concatenate([f[0] for f in faces]))
        per_point_labels[point_ids] = 1000 * class_id + id
        # print(len(faces), class_id)
        print(1000 * class_id + id)
    
    lines = [f'{int(i)}\n' for i in per_point_labels.tolist()]
    with open(f'{scene_name}.txt', 'w') as f:
        f.writelines(lines)

if __name__ == '__main__':

    # Generate text file with class_id class_name
    all_semantic_classes = {}  # id to name
    for scene in scenes:
        print(scene)
        with open(os.path.join(scene, 'habitat', 'info_semantic.json')) as f:
            info_semantic = json.load(f)
        for obj in info_semantic['objects']:
            class_name = obj['class_name']
            class_id = obj['class_id']
            all_semantic_classes[class_id] = class_name
    
    lines = [f'{key} {value}\n' for key, value in sorted(all_semantic_classes.items())]
    with open('class_id_to_names.txt', 'w') as f:
        f.writelines(lines)

    for scene in scenes:
        print(scene)
        with open(os.path.join(scene, 'habitat', 'info_semantic.json')) as f:
            info_semantic = json.load(f)

        file_in = PlyData.read(os.path.join(scene, 'habitat', 'mesh_semantic.ply'))
        vertices_in = file_in.elements[0]
        faces_in = file_in.elements[1]

        points = np.concatenate([vertices_in[c].reshape([-1, 1]) for c in 'xyz'], axis=1)
        colors = np.concatenate([vertices_in[c].reshape([-1, 1]) for c in ['red', 'green', 'blue']], axis=1)

        print('Number of points: ', points.shape)


        # Collect faces with specific object id
        objects = {}  # dict with key = instance_id, value = list of faces (tuple of 4 point ids)
        for f in faces_in:
            object_id = f[1]
            if not object_id in objects:
                objects[object_id] = []
            objects[object_id].append((f[0],))
        
        show_individual_objects(objects, points, colors, info_semantic)

        export_to_scannet_format(objects, info_semantic, scene)
