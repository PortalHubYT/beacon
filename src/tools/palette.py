import json
import numpy as np
import cv2
import os
from PIL import Image
import math
import time

from scipy.spatial.distance import euclidean
from collections import Counter

import shulker as mc
from shulker.components.Block import blocks as mc_block_list
from skimage.color import rgb2lab, deltaE_cie76
from sklearn.cluster import KMeans

"""
Precision of a palette is the spectrum between Flat textures and Complex textures.
Consistency of a palette is the spectrum between Consistency and Variety amongst the block choice.
"""

DEFAULT_TEXTURES_PATH = "palette_cache/texture_pack/assets/minecraft/textures/block"

  
class TextureManager:
    
    @staticmethod
    def has_transparency(image_path: str) -> bool:
        try:
            with Image.open(image_path) as img:
                # Check if the image has an alpha channel and if any pixel is partially transparent
                if img.mode == "RGBA":
                    alpha_channel = img.split()[3]
                    for pixel in alpha_channel.getdata():
                        if pixel < 255:
                            return True
        except Exception as e:
            print(f"Error checking transparency for {image_path}: {str(e)}")
        return False

    @staticmethod
    def get_texture_info(texture_path: str = DEFAULT_TEXTURES_PATH, n_clusters: int = 3) -> dict[str, list[int]]:
        image_file = ColorParser.path_to_image(texture_path)
        dominant_color = ColorParser.get_dominant_color(image_file, n_clusters)
        average_color, stddev_color = ColorParser.get_average_color(image_file)
        
        return {
            "dominant_color": dominant_color,
            "average_color": average_color.tolist(),
            "stddev_color": stddev_color.tolist()
        }
        
    @staticmethod
    def get_textures_path(texture_folder_path: str = DEFAULT_TEXTURES_PATH) -> list[str]:
        textures_path = []
        
        for texture_name in os.listdir(texture_folder_path):
            texture_path = os.path.join(texture_folder_path, texture_name)
            textures_path.append(texture_path)
            
        return textures_path
    
    @staticmethod
    def get_all_block_info(texture_folder_path: str = DEFAULT_TEXTURES_PATH, texture_filter=None, n_clusters: int = 3) -> list[dict]:
        
        try:
            with open("palette_cache/filtered_block_info.json", "r+") as f:
                filtered_block_info = json.load(f)
                if filtered_block_info != []:
                    return filtered_block_info
        except FileNotFoundError:
            print("filtered_block_info cache not found. Generating filtered_block_info...")
        
        textures_path = TextureManager.get_textures_path(texture_folder_path)
        
        skipped = []
        not_png = []
        block_info = []
        
        excluded_block_tags = [
            "shulker",
            "sand",
            "powder",
            "glass",
            "front",
            "coral",
            "dead",
            "trapdoor",
            "chorus",
            "_ore",
        ]

        excluded_blocks = [
            "ice",
            "beacon",
            "crimson_nylium",
            "warped_nylium",
            "dragon_egg"
        ]
        
        for index, texture in enumerate(textures_path):
            
            if not texture.endswith(".png"):
                not_png.append(texture + "(not a png)")
                continue
            
            
            block_name = texture.split("/")[-1].split(".")[0]

            print(block_name)
            
            if any(to_exclude in block_name for to_exclude in excluded_block_tags):
                skipped.append(block_name + f"(excluded manually)")
                continue

            if any(to_exclude == block_name for to_exclude in excluded_blocks):
                skipped.append(block_name + f"(excluded manually)")
                continue
            
 
            if TextureManager.has_transparency(texture):
                skipped.append(block_name + f"(has transparency)")
                continue
                     
            block = TextureManager.get_texture_info(texture, n_clusters)
            block['name'] = block_name
            
            if block["stddev_color"] == [0, 0, 0]:
                skipped.append(block_name + f"(stddev_color is 0)")
                continue
            
            block_info.append(block)
            if block_name not in mc_block_list:
                print(f"Block {block_name} was skipped")
            
        print(f"Len de mc_block_list: {len(mc_block_list)}")
        print(f"Len de block_info: {len(block_info)}")
        print("+++++++++++++++++++++++++++++++++++++++++++++++")
        filtered_block_info, skipped2 = TextureManager.filter_palette(block_info, texture_filter)
        
        skipped.extend(skipped2)
        
        data = {
            "skipped": skipped,
            "not_png": not_png
        }
        
        with open("palette_cache/skipped_blocks.json", "w+") as f:
            json.dump(data, f)
            print(f"Skipped {len(skipped) + len(not_png)} blocks")
        
        # Save block_info to cache
        with open("palette_cache/filtered_block_info.json", "w+") as f:
            json.dump(filtered_block_info, f)
            print("filtered_block_info.json saved!")
    
        print(f"Len de mc_block_list: {len(mc_block_list)}")
        print(f"Len de block_info: {len(block_info)}")
        print(f"Filtered block info: {len(filtered_block_info)} blocks")
        print("+++++++++++++++++++++++++++++++++++++++++++++++")
        return filtered_block_info
    
    @staticmethod
    def is_multistate(block_name):
        return block_name[-1].isdigit()

    @staticmethod
    def has_variable_texture(block_name):
        return any(sub in block_name for sub in ['_top', '_bottom', '_side'])

    @staticmethod
    def is_valid_block(block_name, block_info):

        if block_info is None:  # Handle the case when block_info is None
            return f"(block_info is None)"
        if TextureManager.is_multistate(block_name) or TextureManager.has_variable_texture(block_name):
            return f"(multistate or variable texture)"
        if 'properties' in block_info and block_info['properties']:
            return f"(has properties)"
        return True

    @staticmethod
    def filter_palette(raw_palette, texture_filter=None):
        filtered_palette = []
        suffixes_to_include = texture_filter if texture_filter else []
        skipped = []
        
        for block in raw_palette:
            name = block.get('name', '')
            
            if suffixes_to_include:
                if not any(name.endswith(f'_{suffix}') for suffix in suffixes_to_include): 
                    skipped.append(name + f"(not in texture_filter)")
                    continue
            
            reason = TextureManager.is_valid_block(name, mc_block_list.get(f"minecraft:{name}"))

            
            # If there's a reason it's not valid, skip it
            if type(reason) is str:
                skipped.append(name + reason)
                continue
            
            if name:
                filtered_palette.append(block)
                
        return (filtered_palette, skipped)
    
class ColorParser:
    
    @staticmethod
    def path_to_image(image_path: str) -> cv2.imread:
        image = cv2.imread(image_path)
        if image is None:
            return None
        return image
    
    @staticmethod
    def get_average_color(image: cv2.imread) -> tuple[np.ndarray, np.ndarray]:

        # Convert from BGR to RGB (OpenCV loads images in BGR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Calculate the average and stddev
        average_color = np.mean(image, axis=(0, 1))
        stddev_color = np.std(image, axis=(0, 1))
        
        return average_color, stddev_color
    
    @staticmethod
    def create_rgb_space(complexity: int = 5):
        
        if complexity > 256:
            complexity = 256
        elif complexity < 1:
            complexity = 1
        
        target_colors = []
        step_size = int(256 / complexity)
        
        for r in range(0, 256, step_size):
            for g in range(0, 256, step_size):
                for b in range(0, 256, step_size):
                    if (r, g, b) not in target_colors:
                        target_colors.append((r, g, b))
                    else:
                        print(f"Duplicate color: {(r, g, b)}")
        
        print(f"Created RGB space with {len(target_colors)} colors!")
        return target_colors
    
    @staticmethod
    def get_dominant_color(image: cv2.imread, n_clusters: int = 3) -> list[int]:

        # Convert the image from BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Reshape the image to be a list of pixels
        pixels = image.reshape(-1, 3)

        # Perform k-means clustering
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(pixels)
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_

        # Find the most frequent cluster
        counter = Counter(labels)
        dominant_cluster = counter.most_common(1)[0][0]
        dominant_color = centers[dominant_cluster]

        # Convert to integers
        dominant_color = np.round(dominant_color).astype(int)

        return dominant_color.tolist()

    @staticmethod        
    def calculate_score(target_rgb: list[int], block: dict, precision: float = 0.5, variety: float = 0.5, used_blocks: dict = None) -> float:
        
        used_blocks = used_blocks if used_blocks else {}
        
        target_lab = rgb2lab(np.uint8(np.asarray([[target_rgb]])))
        block_lab = rgb2lab(np.uint8(np.asarray([[block["dominant_color"][:3]]])))
        
        color_distance = deltaE_cie76(target_lab, block_lab)
        color_distance = color_distance[0][0]

        # The influence of color_deviation increases as precision increases.
        # When precision is 0, we just have color_distance.
        
        # If each channel's standard deviation is important:
        if False:
            color_deviation = np.array(block["stddev_color"])
            weighted_deviation = np.sum(precision * color_deviation)
            score = color_distance - weighted_deviation
        
        # If the standard deviations for each color channel are not equally important and can be averaged:
        if True:
            color_deviation = np.array(block["stddev_color"])
            average_deviation = np.mean(color_deviation)
            score = color_distance - precision * average_deviation

        # If block is already used and variety is high, increase score to avoid it.
        
        if block["name"] in used_blocks:
            score += variety * used_blocks[block["name"]]

        return score
    
    @staticmethod
    def get_best_match(target_rgb: list[int, int, int] = None, block_info: list[dict] = None, precision: float = 0.5, variety: float = 0.5, rgb_complexity: int = 5, used_blocks: set = None) -> str:
        block_info = block_info if block_info else TextureManager.get_all_block_info()
        target_rgb = target_rgb if target_rgb else ColorParser.create_rgb_space(rgb_complexity)
        used_blocks = used_blocks if used_blocks else set()
        
        best_score = float('inf')
        best_match = None
        
        for block in block_info:
            score = ColorParser.calculate_score(target_rgb, block, precision, variety, used_blocks)
            if score < best_score:
                best_score = score
                best_match = block["name"]
                
        return best_match
    
    @staticmethod
    def get_closest_color(block_name, complexity: int = 10):
        block_info = ColorParser.get_block_info(block_name)
        
        block_rgb = block_info["dominant_color"][:3]
        target_rgb_space = ColorParser.create_rgb_space(complexity)

        closest_color = None
        closest_distance = float("inf")

        for target_rgb in target_rgb_space:
            distance = euclidean(target_rgb, block_rgb)
            if distance < closest_distance:
                closest_distance = distance
                closest_color = target_rgb

        return closest_color

    @staticmethod
    def get_closest_block(rgb, precision=0.5, variety=0.5):
        return ColorParser.get_best_match(target_rgb=rgb, precision=precision, variety=variety)

    @staticmethod
    def get_block_info(block_name: str):
        all_block_info = TextureManager.get_all_block_info()
        block_info = next(b for b in all_block_info if b["name"] == block_name)
        return block_info

   
    def distance(a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
  
class PaletteGenerator:

    def __init__(self, precision: int = 0.5, variety: int = 0.5):
        
        self.precision = precision
        self.variety = variety
        
        self.best_matches = {}
        self.used_blocks = set()
        
    def generate_palette(self, precision, variety, block_textures_info: list = None, target_rgb_space: list[tuple[int, int, int, int]] = None, force_recreate: bool = False, complexity: int = 5):
        print(f"- > Starting palette generation...")
        print()
        self.target_rgb_space = ColorParser.create_rgb_space(complexity) if not target_rgb_space else target_rgb_space  
        self.block_textures_info = block_textures_info if block_textures_info else TextureManager.get_all_block_info()
        self.precision = precision
        self.variety = variety
        
        print(f"- > Target RGB space: {len(self.target_rgb_space)} colors")
        print(f"- > Block textures info: {len(self.block_textures_info)} blocks")
        data = {}
        preliminary_matches = None
        try:
            if not force_recreate:
                with open("palette_cache/preliminary_matches.json", "r") as f:
                    data = json.load(f)
                    if f"{self.precision}_{self.variety}" in data:
                        preliminary_matches = data[f"{self.precision}_{self.variety}"]
                    else:
                        preliminary_matches = None
        except FileNotFoundError:
            print("No preliminary_matches.json found. Generating preliminary_matches...")
        except json.decoder.JSONDecodeError:
            print("preliminary_matches.json is corrupted. Generating preliminary_matches...")
            
        
        used_blocks = {}
        no_match = []
        if not preliminary_matches or force_recreate:
            # Step 1: Get the preliminary matches
            print("Step 1: Preliminary matches")
            
            preliminary_matches = {}
            for index, color in enumerate(self.target_rgb_space):
                best_match = ColorParser.get_best_match(color, self.block_textures_info, self.precision, self.variety, used_blocks=used_blocks)
                if best_match is not None:
                    
                    if best_match in used_blocks:
                        used_blocks[best_match] += 1  # Increment the count
                    else:
                        used_blocks[best_match] = 1  # Initialize the count
                        
                        preliminary_matches[best_match] = color
                else:
                    no_match.append(color)
                    print(f"No match found for color {color}")
        
        try:
            with open("palette_cache/no_match.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        # Update the data dictionary
        data[f"{self.precision}_{self.variety}"] = no_match

        # Write the updated data back to the file
        with open("palette_cache/no_match.json", "w") as f:
            json.dump(data, f)
            
        # Save preliminary_matches to cache
        with open("palette_cache/preliminary_matches.json", "w+") as f:
            data[f"{self.precision}_{self.variety}"] = preliminary_matches
            json.dump(data, f)
            print("preliminary_matches.json saved!")
        
        # Step 2: Resolve any conflicts
        print("Step 2: Resolving conflicts")

        self.best_matches = preliminary_matches
        # self.best_matches = self.resolve_conflicts(self.target_rgb_space, preliminary_matches, self.block_textures_info, self.precision, self.variety, used_blocks)
    
        palette = PaletteGenerator.save_palette(self.precision, self.variety, self.best_matches)
        return palette
        
    def resolve_conflicts(self, target_rgb: list[int], preliminary_matches: dict, block_palette: list[dict], precision: float, variety: float, used_blocks: dict):
        block_to_color = {} 

        for block, color in preliminary_matches.items():
            if block in used_blocks.keys():
                continue  # Skip blocks that are already used
            else:
                print('using')
                
            color_tuple = tuple(color)  # Convert the list to a tuple for use as a dict key

            best_score = float('inf')
            best_color = None

            try:
                block_data = next(b for b in block_palette if b["name"] == block)
            except StopIteration:
                print(f"No block data found for block: {block}")
                continue

            score = ColorParser.calculate_score(
                color_tuple,
                block_data,
                precision,
                variety,
                used_blocks
            )

            if score < best_score:
                best_score = score
                best_color = color_tuple

            if best_color:
                if block not in used_blocks:  # If the block hasn't been used yet
                    block_to_color[block] = best_color  # Map the block to its color
                    used_blocks[block] = 1  # Initialize the count for this block
                else:  # If the block has been used before
                    used_blocks[block] += 1

        return block_to_color
    
    @staticmethod
    def save_palette(precision, variety, best_matches):
        if os.path.exists("palette_cache/palettes.json"):
            try:
                with open("palette_cache/palettes.json", "r") as f:
                    palettes = json.load(f)
            except Exception as e:
                palettes = {}
        else:
            palettes = {}
        
        key = f"{precision}_{variety}"

        palette = {}

        for v, k in best_matches.items():
            palette[v] = [k[0], k[1], k[2]]
            
        palettes[key] = palette

        with open("palette_cache/palettes.json", "w") as f:
            print(f"Saving a palette with {key} with {len(palette.items())} blocks")
            json.dump(palettes, f, indent=4)
            
        return palettes[key]
    
    @staticmethod
    def load_palette(precision, variety, path="palette_cache/palettes.json", complexity=7):
        try:
            with open(path, "r") as f:
                palettes = json.load(f)
        except Exception as e:
            print(f"Error loading palettes.json: {str(e)}")
            palettes = {}
            
        key = f"{precision}_{variety}"
        if key in palettes:
            print(f"- > Found! Loading palettes.json with {len(palettes[key].items())} blocks !...")
            return palettes[key]
        else:
            print(f"- > Palette not found, generating a new palette...")
            generator = PaletteGenerator()
            palette = generator.generate_palette(precision, variety, complexity=complexity)
            print(f"- > Palette generated with {len(palette.items())} blocks ! Saving to palettes.json...")
            return palette
    
    @staticmethod
    def dictionnaire_as_palette(precision: float = 0.5, variety: float = 50, complexity: int = 5):
        from collections import defaultdict
        import random
        
        candidate_blocks_for_color = defaultdict(list)
        
        # Step 1: Create a dictionary to store candidate blocks for each color
        target_rgb_space = ColorParser.create_rgb_space(complexity)
        block_textures_info = TextureManager.get_all_block_info()
        
        for index, color in enumerate(target_rgb_space):
            best_match = ColorParser.get_best_match(color, block_textures_info, precision, variety)
            if best_match is not None:
                candidate_blocks_for_color[tuple(color)].append(best_match)
            print(f"Color {index}/{len(target_rgb_space)}")

        final_matches = {}
        for color, candidates in candidate_blocks_for_color.items():
            if len(candidates) == 1:
                final_matches[color] = candidates[0]
                continue
                
            weighted_candidates = []
            for candidate in candidates:
                weight = int((1 - variety) * candidates.count(candidate) + variety * (len(candidates) - candidates.count(candidate)))
                weight = max(1, weight)  # set a minimum weight
                weighted_candidates.extend([candidate] * weight)

            if weighted_candidates:
                final_matches[color] = random.choice(weighted_candidates)
            else:
                final_matches[color] = None  # or some default value

        
        reversed = {v: k for k, v in final_matches.items()}
        return reversed
    
class PaletteManager:
    
    def __init__(self):
        self.existing_palettes = {}  # key is (precision, variety), value is Palette instance
        self.palette_settings = {}
        self.default_texture_path = DEFAULT_TEXTURES_PATH

    def get_closest_palettes(self, precision, variety, num_closest=3):
        closest_palettes = sorted(
            self.existing_palettes.keys(), 
            key=lambda x: self.distance((precision, variety), x)
        )[:num_closest]
        
        return [self.existing_palettes[key] for key in closest_palettes]

    def get_palette(self, precision, variety, force_create=False):
        key = f"{precision}_{variety}"
        if key in self.existing_palettes:
            return self.existing_palettes[key]
        
        if not force_create:
            return None
        else:
            return self.create_palette(precision, variety)
       
    def save_all_palettes(self, path="palette_cache/palettes.json"):
        all_palettes = {}
        for key, palette in self.existing_palettes.items():
            all_palettes[key] = palette.best_matches
        with open(path, "w+") as f: 
            json.dump(all_palettes, f, indent=4)
            
    def load_all_palettes(self, path="palette_cache/palettes.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                all_palettes = json.load(f)
            for key, best_matches in all_palettes.items():
                precision, variety = key.split("_")
                palette = PaletteGenerator(precision=precision, variety=variety)
                palette.best_matches = best_matches
                self.existing_palettes[key] = palette
    
    def explore_palette(self, target_rgb_space: list[tuple[int, int, int, int]], step: int = 10, save_path: str = "palette_cache/palettes.json"):
    
        if os.path.exists(save_path):
            with open(save_path, "r") as f:
                palettes = json.load(f)
        else:
            palettes = {}
            
        for precision in np.linspace(0, 1, step):
            for variety in np.linspace(0, 1, step):
                if (precision, variety) not in palettes:
                    palettes[(precision, variety)] = self.create_palette(precision, variety, target_rgb_space)
        
        
        with open(save_path, "w") as f:
            json.dump(palettes, f, indent=4)

class PaletteVisualization:
    """Visualizes Minecraft block palettes in various layouts."""

    def __init__(self, viewer_username, tp_coords):
        self.viewer_username = viewer_username
        self.tp_coords = tp_coords

    def teleport_viewer(self, coords):
        """Teleport the viewer to specified coordinates."""
        return f"tp {self.viewer_username} {coords[0]} {coords[1]} {coords[2]}"
    
    @staticmethod
    def print_palette_2D(palette, x_offset=-400):
        total_colors = len(palette.items())
        grid_size = int(math.ceil(math.sqrt(total_colors)))
        WIDTH = grid_size *10  # Number of colors in each row of the square grid
        HEIGHT = grid_size *10
        
        def find_closest_color(target):
            min_distance = float("inf")
            closest = None
            for color in palette:
                distance = sum((a - b) ** 2 for a, b in zip(target, palette[color]))
                if distance < min_distance:
                    min_distance = distance
                    closest = palette[color]
            return closest

        x_offset = -576  # If you want to keep the x_offset
        y_offset = 8  # Set a base y_offset if needed

        for x in range(WIDTH):
            for y in range(HEIGHT):
                mult = 255 / WIDTH
                color_to_match = (
                    math.floor(x * mult),
                    math.floor(y * mult),
                    128  # You can adjust the Z-coordinate as needed
                )
                pixel = (x * 2 + x_offset, y * 2 + y_offset, 0)  # Adjust the Y and Z coordinates as needed
                closest_color = find_closest_color(color_to_match)
                # Find the key that corresponds to the value
                block = list(palette.keys())[list(palette.values()).index(closest_color)]
                mc.set_block(pixel, block)
                mc.post(f"tp PortalHub {pixel[0]} {pixel[1]} {pixel[2] + 20}")
                print(f"Setting block {block} at position {pixel}")
                
    def print_palette_3D(palette):
        
        start_x = 480
        start_y = 120
        SIZE = 50
        
        mc.post(f"sudo PortalHub //pos1 {start_x},{start_y},0")
        mc.post(f"sudo PortalHub //pos2 {start_x + SIZE * 2},{start_y + SIZE * 2},{SIZE * 2}")
        mc.post(f"sudo PortalHub //cut")
        
        closest_cache = {}
        
        def find_closest_color(target):
            if target in closest_cache:
                return closest_cache[target]

            min_distance = float("inf")
            closest = None
            
            for color in palette:
                distance = sum((a - b) ** 2 for a, b in zip(target, palette[color]))
                if distance < min_distance:
                    min_distance = distance
                    closest = palette[color]
                    
            closest_cache[target] = closest
            return closest

        for x in range(SIZE):
            for y in range(SIZE):
                for z in range(SIZE):
                    mult = 255 / SIZE
                    color_to_match = (
                        math.floor(x * mult),
                        math.floor(y * mult),
                        math.floor(z * mult),
                    )
                    pixel = (x * 2 + start_x, start_y + (y * 2), z * 2)
                    closest_color = find_closest_color(color_to_match)
                    block = list(palette.keys())[list(palette.values()).index(closest_color)] 
                    mc.set_block(pixel, block)
                    print(f"Setting block {block} at position {pixel}", end="\r")       
                    
    def benchmark():
        from collections import defaultdict
        import time
        import random
        
        # Simulated palette
        palette = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(512)]

        # Cache dictionary
        cache = {}

        # Precomputed RGB space
        precomputed_rgb_space = {(r, g, b): "some_block" for r in range(0, 256, 8) for g in range(0, 256, 8) for b in range(0, 256, 8)}

        def find_closest_color(target, palette):
            min_distance = float("inf")
            closest = None
            for color in palette:
                distance = sum((a - b) ** 2 for a, b in zip(target, color))
                if distance < min_distance:
                    min_distance = distance
                    closest = color
            return closest

        def find_with_cache(target):
            if target in cache:
                return cache[target]
            closest = find_closest_color(target, palette)
            cache[target] = closest
            return closest

        def find_with_precomputation(target):
            return precomputed_rgb_space.get(target, "default_block")

        # Number of iterations
        iterations = 100000

        # Test find_closest_color
        start_time = time.time()
        for _ in range(iterations):
            find_closest_color((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), palette)
        print("Without caching:", time.time() - start_time, "seconds")

        # Test with caching
        start_time = time.time()
        for _ in range(iterations):
            find_with_cache((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        print("With caching:", time.time() - start_time, "seconds")

        # Test with precomputation
        start_time = time.time()
        for _ in range(iterations):
            find_with_precomputation((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        print("With precomputation:", time.time() - start_time, "seconds")

    
if __name__ == "__main__":
    mc.connect()
    generator = PaletteGenerator()
    palette = generator.generate_palette(0, 15, force_recreate=True, complexity=7)
    print(len(palette))
    exit()
    PaletteVisualization.print_palette_3D(palette)

    