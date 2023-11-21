import re
from dataclasses import dataclass

import shulker as mc

################################################################################

models = {
    "gifters_platform": """/summon block_display ~-0.5 ~-0.5 ~-0.5 {Passengers:[{id:"minecraft:block_display",block_state:{Name:"minecraft:pearlescent_froglight",Properties:{axis:"x"}},transformation:[1.4868f,0.0000f,0.0000f,0.1348f,0.0000f,0.5469f,0.0000f,0.2422f,0.0000f,0.0000f,1.8457f,-0.0703f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_platform"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:pearlescent_froglight",Properties:{axis:"x"}},transformation:[1.6919f,0.0000f,0.0000f,0.0322f,0.0000f,0.5469f,0.0000f,0.2422f,0.0000f,0.0000f,1.6406f,0.0322f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_platform"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:pearlescent_froglight",Properties:{axis:"x"}},transformation:[1.8970f,0.0000f,0.0000f,-0.0703f,0.0000f,0.5469f,0.0000f,0.2422f,0.0000f,0.0000f,1.4355f,0.1348f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_platform"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:dark_oak_planks",Properties:{}},transformation:[1.6992f,0.0000f,0.0000f,0.0469f,0.0000f,0.6250f,0.0000f,0.1250f,0.0000f,0.0000f,2.1094f,-0.1875f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_platform"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:dark_oak_planks",Properties:{}},transformation:[1.9336f,0.0000f,0.0000f,-0.0703f,0.0000f,0.6250f,0.0000f,0.1250f,0.0000f,0.0000f,1.8750f,-0.0703f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_platform"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:dark_oak_planks",Properties:{}},transformation:[2.1680f,0.0000f,0.0000f,-0.1875f,0.0000f,0.6250f,0.0000f,0.1250f,0.0000f,0.0000f,1.6406f,0.0469f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_platform"]},{id:"minecraft:text_display",text:'{"text":"GIFTER","color":"#ffd06f","bold":"true","italic":"false","underlined":"false","strikethrough":"false","font":"minecraft:default"}',text_opacity:255,background:0,alignment:"center",line_width:210,default_background:false,transformation:[1.4063f,0.0000f,0.0000f,0.8738f,0.0000f,1.2500f,0.0000f,0.2969f,0.0000f,0.0000f,1.8750f,1.9672f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_platform"]}]}""",
    "gifters_chat": """/summon block_display ~-0.5 ~-0.5 ~-0.5 {Passengers:[{id:"minecraft:block_display",block_state:{Name:"minecraft:dark_oak_planks",Properties:{}},transformation:[4.0000f,0.0000f,0.0000f,0.0000f,0.0000f,1.0000f,0.0000f,0.5625f,0.0000f,0.0000f,0.0625f,0.0000f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_chat"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:snow_block",Properties:{}},transformation:[3.8750f,0.0000f,0.0000f,0.0625f,0.0000f,0.6250f,0.0000f,0.7500f,0.0000f,0.0000f,0.0625f,0.0625f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_chat"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:snow_block",Properties:{}},transformation:[3.7500f,0.0000f,0.0000f,0.1250f,0.0000f,0.7500f,0.0000f,0.6875f,0.0000f,0.0000f,0.0625f,0.0625f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_chat"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:snow_block",Properties:{}},transformation:[3.6250f,0.0000f,0.0000f,0.1875f,0.0000f,0.8750f,0.0000f,0.6250f,0.0000f,0.0000f,0.0625f,0.0625f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_chat"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:snow_block",Properties:{}},transformation:[0.3750f,0.0000f,0.0000f,3.3125f,0.0000f,0.2500f,0.0000f,0.3750f,0.0000f,0.0000f,0.0625f,0.0625f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_chat"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:snow_block",Properties:{}},transformation:[0.3125f,0.0000f,0.0000f,3.3125f,0.0000f,0.1250f,0.0000f,0.2500f,0.0000f,0.0000f,0.0625f,0.0625f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_chat"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:snow_block",Properties:{}},transformation:[0.2500f,0.0000f,0.0000f,3.2500f,0.0000f,0.1250f,0.0000f,0.1250f,0.0000f,0.0000f,0.0625f,0.0625f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_chat"]},{id:"minecraft:block_display",block_state:{Name:"minecraft:snow_block",Properties:{}},transformation:[0.1250f,0.0000f,0.0000f,3.2500f,0.0000f,0.1250f,0.0000f,0.0000f,0.0000f,0.0000f,0.0625f,0.0625f,0.0000f,0.0000f,0.0000f,1.0000f],Tags:["gifters_chat"]}]}"""
}

replacing_default = [
    ("/summon block_display ~-0.5 ~-0.5 ~-0.5 {Passengers:[", ""),
    ("uniform", "default"),
    (".0000f", ".0f"),
    (",Properties:{}", ""),
    ("minecraft:", ""),
    ('{id:"block_display",', "summon block_display $pos {"),
    ('{id:"text_display",', "summon text_display $pos {"),
    ]

test_pos = mc.Coordinates(1, 71, 56)

# Regex that separates each element of the model
regex = r'(summon.+?]})'
    
################################################################################

def get_spawn_commands(tag: str, pos: mc.Coordinates, replacing: list = replacing_default) -> list:
    """
    Returns a list of commands to spawn the model in Minecraft.
    Tag is both the name of the model and what all of its component are tagged as.
    """
    
    cmd = models[tag]
    
    data = cmd.strip()
    for r in replacing:
        data = data.replace(*r)
    data = data.replace("$pos", f"{pos.x} {pos.y} {pos.z}")
    data = re.findall(regex, data)
    return data

def remove_model(tag: str) -> str:
    """
    Removes all entities tagged with the given tag.
    """
    
    cmd = f"kill @e[tag={tag}]"
    return cmd