import os
import numpy as np
from PIL import Image

# Config
allowPrints = True # Allow debug print statements to show up
colSpecThreshold = 0.7 # When generating the exponent texture, this is the threshold for allowing color specularity
skipAlpha = False # Skip processing alpha textures

"""
    Notes:
        - Implement automatic VMT generation(?)
"""

def doPrint(*args, **kwargs):
    if allowPrints:
        print(*args, **kwargs)

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
            if file.endswith('_a.tga') and file[0] == '_': # Alpha textures are usually named with _a_ prefix
                base_name = base_name[3:]
        else:
            base_name = file.rsplit('.', 1)[0]
        
        if base_name not in texture_groups:
            texture_groups[base_name] = {'diffuse': None, 'normal': None, 'specular': None, 'alpha': None}
        
        if file.endswith('_n.tga'):
            texture_groups[base_name]['normal'] = file
            doPrint(f"Found normal texture: {file} for {base_name}")
        elif file.endswith('_bs.tga') or file.endswith('_s.tga'):
            if texture_groups[base_name]['specular'] is None or file.endswith('_s.tga'): # Prioritize the _s over the _bs texture
                texture_groups[base_name]['specular'] = file
                doPrint(f"Found specular texture: {file} for {base_name}")
        elif file.endswith('_a.tga') and not skipAlpha:
            texture_groups[base_name]['alpha'] = file
            doPrint(f"Found alpha texture: {file} for {base_name}")
        else:
            texture_groups[base_name]['diffuse'] = file
            doPrint(f"Found base texture: {file} for {base_name}")
    
    return texture_groups

def processTextures(directory, texture_groups):
    output_dir = os.path.join(directory, 'Converted')
    os.makedirs(output_dir, exist_ok=True)

    for base_name, textures in texture_groups.items():
        if textures['diffuse'] is None or textures['specular'] is None:
            doPrint(f"Skipping incomplete texture group: {base_name}")
            continue

        diffuse_path = os.path.join(directory, textures['diffuse'])
        specular_path = os.path.join(directory, textures['specular'])
        normal_path = os.path.join(directory, textures['normal']) if textures['normal'] else None
        alpha_path = os.path.join(directory, textures['alpha']) if textures['alpha'] else None

        diffuse = loadImage(diffuse_path)
        if diffuse is None:
            doPrint(f"Failed to load diffuse texture: {diffuse_path}")
            continue

        specular = loadImage(specular_path)
        if specular is None:
            doPrint(f"Failed to load specular texture: {specular_path}")
            continue

        if alpha_path:
            # print(f"Alpha path: {alpha_path}")
            alpha = loadImage(alpha_path)
            if alpha is None:
                doPrint(f"Failed to load alpha texture: {alpha_path}")
                continue

            if alpha.shape[:2] != diffuse.shape[:2]:
                alpha = np.array(Image.fromarray(alpha).resize((diffuse.shape[1], diffuse.shape[0]), Image.LANCZOS))
                # print(f"Resized alpha to {diffuse.shape[1]}x{diffuse.shape[0]}")

            if diffuse.shape[2] == 3:
                diffuse = np.dstack([diffuse, np.zeros(diffuse.shape[:2], dtype=np.uint8)])
                # print("Added alpha channel to diffuse texture")
            diffuse[:, :, 3] = np.array(Image.fromarray(alpha).convert("L"))
            # print("Successfully added alpha channel to diffuse texture")

        diffuse_img = Image.fromarray(diffuse)
        diffuse_img.save(os.path.join(output_dir, os.path.basename(diffuse_path)))

        if normal_path:
            normal = loadImage(normal_path)
            if normal is None:
                doPrint(f"Failed to load normal texture: {normal_path}")
            else:
                if specular.shape[:2] != normal.shape[:2]:
                    specular = np.array(Image.fromarray(specular).resize((normal.shape[1], normal.shape[0]), Image.LANCZOS))

                if normal.shape[2] == 3:
                    normal = np.dstack([normal, np.zeros(normal.shape[:2], dtype=np.uint8)])
                normal[:, :, 3] = np.array(Image.fromarray(specular).convert("L"))
                
                normal_img = Image.fromarray(normal)
                normal_img.save(os.path.join(output_dir, os.path.basename(normal_path)))

        exponent = np.zeros((specular.shape[0], specular.shape[1], 3), dtype=np.uint8)
        exponent[:, :, 0] = np.array(Image.fromarray(specular).convert("L"))
        exponent[:, :, 1] = 255 * colSpecThreshold
        # exponent[:, :, 1] = 178 # Albedo tinting, this value allows 70% color specularity
        exponent[:, :, 2] = 255
        
        exponent_img = Image.fromarray(exponent)
        exponent_img.save(os.path.join(output_dir, f"{base_name}_s.tga"))

        doPrint(f"Processed {base_name}")

def main():
    directory = os.getcwd()
    tga_files = [f for f in os.listdir(directory) if f.endswith('.tga')]
    doPrint(f"Found {len(tga_files)} textures in {directory}, processing...")
    # doPrint()
    # doPrint()
    texture_groups = findGroups(tga_files)
    doPrint()
    doPrint("Processing textures...")
    processTextures(directory, texture_groups)
    # doPrint()
    # doPrint()
    print("Finished processing textures!")

if __name__ == "__main__":
    main()
