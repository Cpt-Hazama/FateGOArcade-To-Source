import os
import numpy as np
from PIL import Image

"""
    Notes:
        - Alpha texture stuff sometimes fails, need to figure that out
        - _BS textures are still a bit of a mystery, I honestly can't tell if it's a type of ambient occlusion or actually just a specular map

    Example VMTs for Source Engine:
        Normal:
            "VertexLitGeneric"
            {
                "$basetexture" 				"models/cpthazama/fgoa/svt0113/SVT_0113_S03_body"
                "$bumpmap"					"models/cpthazama/fgoa/svt0113/SVT_0113_S03_body_n"
                "$phongexponenttexture"		"models/cpthazama/fgoa/svt0113/SVT_0113_S03_body_s"

                "$color2"                    "[1.3 1.3 1.3]"
                "$nodecal"                   "1"
                "$ambientocclusion"          "1"

                "$phong"                     "1"
                "$phongboost"                "1"
                "$phongfresnelranges"        "[0.1 0.356 0.525]"
                "$phongalbedotint"           "1"
                "$phongalbedoboost"          "30"

                "$rimlight"                  "1"
                "$rimlightexponent"          "5000"
                "$rimlightboost"             "2"

                "$lightwarptexture"          "models/cpthazama/fgoa/shader2"
            }

        Transparent:
            "VertexLitGeneric"
            {
                "$basetexture" 				"models/cpthazama/fgoa/svt0113/SVT_0113_S03_mark"
                "$bumpmap"					"vj_base/flat"
                "$phongexponenttexture"		"models/cpthazama/fgoa/svt0113/SVT_0113_S03_mark_s"

                "$color2"                    "[1.3 1.3 1.3]"
                "$nodecal"                   "1"
                "$ambientocclusion"          "1"
                "$alphatest"                 "1"
                "$allowalphatocoverage"      "1"

                "$phong"                     "1"
                "$phongboost"                "1"
                "$phongfresnelranges"        "[0.1 0.356 0.525]"
                "$phongalbedotint"           "1"
                "$phongalbedoboost"          "30"

                "$rimlight"                  "1"
                "$rimlightexponent"          "5000"
                "$rimlightboost"             "2"

                "$lightwarptexture"          "models/cpthazama/fgoa/shader2"
            }

        Metals:
            "VertexLitGeneric"
            {
                "$basetexture" 				"models/cpthazama/fgoa/svt0001/SVT_0001_S02_chestarm"
                "$bumpmap"					"models/cpthazama/fgoa/svt0001/SVT_0001_S02_chestarm_n"
                "$phongexponenttexture"		"models/cpthazama/fgoa/svt0001/SVT_0001_S02_chestarm_s"

                "$color2"                    "[1.3 1.3 1.3]"
                "$nodecal"                   "1"
                "$ambientocclusion"          "1"

                "$phong"                     "1"
                "$phongboost"                "10"
                "$phongfresnelranges"        "[0.1 0.356 0.525]"
                "$phongalbedotint"           "1"
                "$phongalbedoboost"          "30"
                "$phongwarptexture" 		 "models/cpthazama/fgoa/phongwarp_steel"

                "$envmap"                    "env_cubemap"
                "$envmaptint" 				 "[0.4 0.4 0.4]"
                "$envmapfresnel"             "0.5"
                "$normalmapalphaenvmapmask"  "1"

                "$rimlight"                  "1"
                "$rimlightexponent"          "5000"
                "$rimlightboost"             "2"

                "$DEM_TintScale" 			"[1 1 1]"
                "$DEM_Multiplier" 			"1"

                "Proxies" 
                {
                    "DynamicEnvMap"
                    {
                        resultVar	"$envmaptint"
                    }
                }

                "$lightwarptexture"          "models/cpthazama/fgoa/shader2"
            }
"""

def loadImage(image_path):
    try:
        img = Image.open(image_path)
        return np.array(img)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def findGroups(files):
    texture_groups = {}
    
    for file in files:
        if 'envmap' in file:
            continue
        if file.endswith('_n.tga') or file.endswith('_bs.tga') or file.endswith('_s.tga') or file.endswith('_a.tga'):
            base_name = file.rsplit('_', 1)[0]
        else:
            base_name = file.rsplit('.', 1)[0]
        
        if base_name not in texture_groups:
            texture_groups[base_name] = {'diffuse': None, 'normal': None, 'specular': None, 'alpha': None}
        
        if file.endswith('_n.tga'):
            texture_groups[base_name]['normal'] = file
            print(f"Found normal texture: {file} for {base_name}")
        elif file.endswith('_bs.tga') or file.endswith('_s.tga'):
            if texture_groups[base_name]['specular'] is None or file.endswith('_s.tga'): # Prioritize the _s over the _bs texture
                texture_groups[base_name]['specular'] = file
                print(f"Found specular texture: {file} for {base_name}")
        elif file.endswith('_a.tga'):
            texture_groups[base_name]['alpha'] = file
            print(f"Found alpha texture: {file} for {base_name}")
        else:
            texture_groups[base_name]['diffuse'] = file
            print(f"Found base texture: {file} for {base_name}")
    
    return texture_groups

def processTextures(directory, texture_groups):
    output_dir = os.path.join(directory, 'Converted')
    os.makedirs(output_dir, exist_ok=True)
    
    for base_name, textures in texture_groups.items():
        if textures['diffuse'] is None or textures['specular'] is None:
            print(f"Skipping incomplete texture group: {base_name}")
            continue
        print()

        diffuse_path = os.path.join(directory, textures['diffuse'])
        specular_path = os.path.join(directory, textures['specular'])
        normal_path = os.path.join(directory, textures['normal']) if textures['normal'] else None
        alpha_path = os.path.join(directory, textures['alpha']) if textures['alpha'] else None

        diffuse = loadImage(diffuse_path)
        if diffuse is None:
            print(f"Failed to load diffuse texture: {diffuse_path}")
            continue

        specular = loadImage(specular_path)
        if specular is None:
            print(f"Failed to load specular texture: {specular_path}")
            continue

        if alpha_path:
            alpha = loadImage(alpha_path)
            if alpha is None:
                print(f"Failed to load alpha texture: {alpha_path}")
                continue

            if alpha.shape[:2] != diffuse.shape[:2]:
                alpha = np.array(Image.fromarray(alpha).resize((diffuse.shape[1], diffuse.shape[0]), Image.LANCZOS))

            if diffuse.shape[2] == 3:
                diffuse = np.dstack([diffuse, np.zeros(diffuse.shape[:2], dtype=np.uint8)])
            diffuse[:, :, 3] = np.array(Image.fromarray(alpha).convert("L"))

        diffuse_img = Image.fromarray(diffuse)
        diffuse_img.save(os.path.join(output_dir, os.path.basename(diffuse_path)))

        if normal_path:
            normal = loadImage(normal_path)
            if normal is None:
                print(f"Failed to load normal texture: {normal_path}")
            else:
                if specular.shape[:2] != normal.shape[:2]:
                    specular = np.array(Image.fromarray(specular).resize((normal.shape[1], normal.shape[0]), Image.LANCZOS))

                if normal.shape[2] == 3:
                    normal = np.dstack([normal, np.zeros(normal.shape[:2], dtype=np.uint8)])
                normal[:, :, 3] = np.array(Image.fromarray(specular).convert("L"))
                
                normal_img = Image.fromarray(normal)
                normal_img.save(os.path.join(output_dir, os.path.basename(normal_path)))

        new_tga = np.zeros((specular.shape[0], specular.shape[1], 3), dtype=np.uint8)
        new_tga[:, :, 0] = np.array(Image.fromarray(specular).convert("L"))
        new_tga[:, :, 1] = 178 # Albedo tinting, this value allows 70% color specularity
        new_tga[:, :, 2] = 255
        
        new_tga_image = Image.fromarray(new_tga)
        new_tga_image.save(os.path.join(output_dir, f"{base_name}_s.tga"))

        print(f"Processed {base_name}")

def main():
    directory = os.getcwd()
    tga_files = [f for f in os.listdir(directory) if f.endswith('.tga')]
    print(f"Found {len(tga_files)} textures in {directory}, processing...")
    # print()
    # print()
    texture_groups = findGroups(tga_files)
    # print()
    print("Processing textures...")
    processTextures(directory, texture_groups)
    # print()
    # print()
    print("Finished processing textures!")

if __name__ == "__main__":
    main()
