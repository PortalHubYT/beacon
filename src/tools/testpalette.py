import shulker as mc
import math
import time
import os
import glob


from palette import PaletteGenerator


# palette = PaletteManager.load_palette(0, 0)
mc.connect()


SIZE = 50
petalette = PaletteGenerator.load_palette(100, variety=15, complexity=7)

print(petalette)

palette_full = {
    "acacia_planks": (66, 35, 20),
    "acacia_wood": (40, 38, 34),
    "amethyst_block": (53, 38, 75),
    "andesite": (53, 53, 54),
    "bamboo_planks": (76, 68, 31),
    "bamboo_mosaic": (75, 67, 31),
    "birch_planks": (75, 69, 47),
    "birch_wood": (85, 84, 82),
    "black_concrete": (3, 4, 6),
    "black_glazed_terracotta": (27, 12, 13),
    "black_terracotta": (15, 9, 6),
    "black_wool": (8, 9, 10),
    "blue_concrete": (18, 18, 56),
    "blue_glazed_terracotta": (18, 25, 55),
    "blue_terracotta": (29, 24, 36),
    "blue_wool": (21, 22, 62),
    "bricks": (59, 38, 33),
    "brown_concrete": (38, 25, 13),
    "brown_glazed_terracotta": (47, 42, 34),
    "brown_mushroom_block": (58, 44, 32),
    "brown_terracotta": (30, 20, 14),
    "brown_wool": (45, 28, 16),
    "calcite": (87, 88, 87),
    "cherry_planks": (89, 70, 68),
    "cherry_wood": (22, 13, 17),
    "chiseled_deepslate": (21, 21, 22),
    "chiseled_nether_bricks": (18, 9, 11),
    "chiseled_polished_blackstone": (21, 20, 22),
    "chiseled_stone_bricks": (47, 48, 47),
    "clay": (63, 65, 70),
    "coal_block": (6, 6, 6),
    "coal_ore": (42, 42, 41),
    "coarse_dirt": (47, 34, 23),
    "cobbled_deepslate": (30, 30, 32),
    "cobblestone": (50, 50, 50),
    "copper_ore": (49, 49, 47),
    "cracked_deepslate_bricks": (25, 25, 25),
    "cracked_deepslate_tiles": (21, 21, 21),
    "cracked_nether_bricks": (16, 8, 9),
    "cracked_polished_blackstone_bricks": (17, 15, 17),
    "cracked_stone_bricks": (46, 47, 46),
    "crimson_hyphae": (36, 10, 12),
    "crimson_planks": (40, 19, 28),
    "cyan_concrete": (8, 48, 53),
    "cyan_glazed_terracotta": (20, 47, 49),
    "cyan_terracotta": (34, 36, 36),
    "cyan_wool": (8, 54, 57),
    "dark_oak_planks": (26, 18, 8),
    "dark_oak_wood": (25, 17, 8),
    "dark_prismarine": (20, 36, 30),
    "deepslate_bricks": (28, 28, 28),
    "deepslate_coal_ore": (29, 29, 30),
    "deepslate_copper_ore": (36, 36, 35),
    "deepslate_diamond_ore": (33, 42, 42),
    "deepslate_emerald_ore": (31, 41, 35),
    "deepslate_gold_ore": (45, 40, 31),
    "deepslate_iron_ore": (42, 39, 37),
    "deepslate_lapis_ore": (31, 36, 45),
    "deepslate_redstone_ore": (41, 29, 29),
    "deepslate_tiles": (22, 22, 22),
    "diamond_block": (38, 93, 89),
    "diamond_ore": (47, 55, 55),
    "diorite": (74, 74, 74),
    "dirt": (53, 38, 26),
    "dripstone_block": (53, 42, 36),
    "emerald_block": (16, 80, 35),
    "emerald_ore": (46, 54, 49),
    "end_stone": (86, 87, 62),
    "end_stone_bricks": (85, 88, 64),
    "gilded_blackstone": (22, 17, 15),
    "gold_block": (96, 82, 24),
    "gold_ore": (57, 53, 42),
    "granite": (58, 40, 34),
    "gray_concrete": (22, 24, 24),
    "gray_glazed_terracotta": (33, 35, 37),
    "gray_terracotta": (23, 16, 14),
    "gray_wool": (25, 27, 28),
    "green_concrete": (29, 36, 14),
    "green_glazed_terracotta": (46, 56, 26),
    "green_terracotta": (30, 33, 16),
    "green_wool": (33, 43, 11),
    "honeycomb_block": (90, 58, 12),
    "iron_block": (86, 86, 86),
    "iron_ore": (53, 51, 48),
    "jungle_planks": (63, 45, 32),
    "jungle_wood": (33, 27, 10),
    "lapis_block": (12, 26, 55),
    "lapis_ore": (42, 46, 55),
    "light_blue_concrete": (14, 54, 78),
    "light_blue_glazed_terracotta": (37, 65, 82),
    "light_blue_terracotta": (44, 43, 54),
    "light_blue_wool": (23, 69, 85),
    "light_gray_concrete": (49, 49, 45),
    "light_gray_glazed_terracotta": (56, 65, 66),
    "light_gray_terracotta": (53, 42, 38),
    "light_gray_wool": (56, 56, 53),
    "lime_concrete": (37, 66, 10),
    "lime_glazed_terracotta": (64, 78, 22),
    "lime_terracotta": (41, 46, 21),
    "lime_wool": (44, 73, 10),
    "magenta_concrete": (66, 19, 62),
    "magenta_glazed_terracotta": (82, 39, 75),
    "magenta_terracotta": (59, 35, 43),
    "magenta_wool": (75, 27, 71),
    "mangrove_wood": (33, 26, 16),
    "mangrove_planks": (46, 21, 19),
    "moss_block": (35, 43, 18),
    "mossy_cobblestone": (43, 47, 37),
    "mossy_stone_bricks": (45, 47, 41),
    "mud": (24, 22, 24),
    "mud_bricks": (54, 40, 31),
    "mushroom_stem": (80, 77, 73),
    "nether_bricks": (17, 9, 10),
    "nether_gold_ore": (45, 22, 16),
    "nether_quartz_ore": (46, 26, 24),
    "nether_wart_block": (45, 1, 1),
    "netherite_block": (26, 24, 25),
    "netherrack": (38, 15, 15),
    "note_block": (35, 23, 16),
    "oak_planks": (64, 51, 31),
    "oak_wood": (43, 33, 20),
    "obsidian": (6, 4, 10),
    "orange_concrete": (88, 38, 0),
    "orange_glazed_terracotta": (61, 58, 36),
    "orange_terracotta": (64, 33, 15),
    "orange_wool": (95, 46, 8),
    "packed_mud": (56, 42, 31),
    "pink_concrete": (84, 40, 56),
    "pink_glazed_terracotta": (92, 61, 71),
    "pink_terracotta": (64, 31, 31),
    "pink_wool": (93, 55, 67),
    "polished_andesite": (52, 53, 53),
    "polished_blackstone": (21, 19, 22),
    "polished_blackstone_bricks": (19, 17, 20),
    "polished_deepslate": (28, 29, 29),
    "polished_diorite": (76, 76, 76),
    "polished_granite": (60, 42, 35),
    "powder_snow": (97, 99, 99),
    "prismarine": (39, 61, 59),
    "prismarine_bricks": (39, 67, 62),
    "purple_concrete": (39, 13, 61),
    "purple_glazed_terracotta": (43, 19, 60),
    "purple_terracotta": (46, 27, 34),
    "purple_wool": (44, 16, 68),
    "purpur_block": (67, 49, 67),
    "quartz_block": (93, 90, 87),
    "quartz_bricks": (92, 91, 87),
    "raw_copper_block": (60, 42, 31),
    "raw_gold_block": (87, 66, 18),
    "raw_iron_block": (65, 53, 42),
    "red_concrete": (56, 13, 13),
    "red_glazed_terracotta": (71, 24, 21),
    "red_mushroom_block": (78, 18, 18),
    "red_nether_bricks": (27, 3, 4),
    "red_terracotta": (56, 24, 18),
    "red_wool": (63, 15, 14),
    "redstone_block": (69, 10, 2),
    "redstone_lamp": (37, 22, 12),
    "redstone_ore": (55, 43, 43),
    "rooted_dirt": (56, 41, 30),
    "sculk": (5, 11, 14),
    "slime_block": (44, 75, 36),
    "smooth_basalt": (29, 28, 31),
    "smooth_quartz": (93, 90, 88),
    "smooth_red_sandstone": (71, 38, 12),
    "smooth_sandstone": (88, 84, 67),
    "smooth_stone": (62, 62, 62),
    "snow_block": (98, 100, 100),
    "soul_sand": (32, 24, 20),
    "soul_soil": (30, 23, 18),
    "sponge": (77, 75, 29),
    "spruce_planks": (45, 34, 19),
    "spruce_wood": (23, 15, 7),
    "stone": (49, 50, 49),
    "stone_bricks": (48, 49, 48),
    "stripped_acacia_wood": (69, 36, 24),
    "stripped_birch_wood": (77, 69, 46),
    "stripped_cherry_wood": (84, 57, 58),
    "stripped_crimson_hyphae": (54, 22, 35),
    "stripped_dark_oak_wood": (28, 22, 14),
    "stripped_jungle_wood": (67, 52, 33),
    "stripped_mangrove_wood": (47, 21, 18),
    "stripped_oak_wood": (69, 57, 34),
    "stripped_spruce_wood": (45, 35, 20),
    "stripped_warped_hyphae": (23, 59, 58),
    "terracotta": (60, 37, 27),
    "tuff": (42, 43, 40),
    "warped_hyphae": (23, 23, 31),
    "warped_planks": (17, 41, 39),
    "warped_wart_block": (9, 47, 47),
    "waxed_copper_block": (75, 42, 31),
    "waxed_cut_copper": (75, 42, 32),
    "waxed_exposed_copper": (63, 49, 41),
    "waxed_exposed_cut_copper": (61, 48, 40),
    "waxed_oxidized_copper": (32, 64, 52),
    "waxed_oxidized_cut_copper": (31, 60, 49),
    "waxed_weathered_copper": (42, 60, 43),
    "waxed_weathered_cut_copper": (43, 57, 42),
    "wet_sponge": (67, 71, 27),
    "white_concrete": (81, 84, 84),
    "white_glazed_terracotta": (74, 83, 80),
    "white_terracotta": (82, 70, 63),
    "white_wool": (92, 93, 93),
    "yellow_concrete": (95, 69, 8),
    "yellow_glazed_terracotta": (92, 75, 35),
    "yellow_terracotta": (73, 52, 14),
    "yellow_wool": (98, 78, 16),
    "dirt_path": (58, 48, 25),
    "jukebox": (37, 25, 18),
    "mycelium": (44, 39, 40),
    "podzol": (36, 25, 9),
    "respawn_anchor": (13, 13, 20),
    "ancient_debris": (38, 25, 22),
    "ancient_debris": (37, 26, 23),
    "ancient_debris": (37, 26, 23),
    "blackstone": (16, 15, 16),
    "blackstone": (16, 14, 16),
    "blackstone": (16, 14, 16),
    "chiseled_quartz_block": (91, 90, 85),
    "chiseled_quartz_block": (91, 89, 85),
    "chiseled_quartz_block": (91, 89, 85),
    "lodestone": (47, 47, 48),
    "lodestone": (58, 58, 60),
    "lodestone": (58, 58, 60),
    "melon": (45, 57, 12),
    "melon": (44, 57, 12),
    "melon": (44, 57, 12),
    "pumpkin": (77, 45, 9),
    "pumpkin": (78, 47, 9),
    "pumpkin": (78, 47, 9),
    "red_sandstone": (73, 39, 11),
    "red_sandstone": (73, 38, 11),
    "red_sandstone": (73, 38, 11),
    "sandstone": (85, 81, 61),
    "sandstone": (85, 79, 60),
    "sandstone": (85, 79, 60),
    "target": (90, 69, 66),
    "target": (89, 67, 62),
    "target": (89, 67, 62),
    "acacia_log": (59, 35, 22),
    "acacia_log": (59, 35, 22),
    "birch_log": (76, 70, 53),
    "birch_log": (76, 70, 53),
    "crimson_stem": (44, 19, 27),
    "crimson_stem": (44, 19, 27),
    "dark_oak_log": (26, 18, 9),
    "dark_oak_log": (26, 18, 9),
    "jungle_log": (59, 43, 28),
    "jungle_log": (59, 43, 28),
    "mangrove_log": (40, 19, 16),
    "mangrove_log": (40, 19, 16),
    "oak_log": (59, 48, 29),
    "oak_log": (59, 48, 29),
    "spruce_log": (43, 31, 18),
    "spruce_log": (43, 31, 18),
    "stripped_acacia_log": (65, 36, 20),
    "stripped_acacia_log": (65, 36, 20),
    "stripped_birch_log": (75, 67, 45),
    "stripped_birch_log": (75, 67, 45),
    "stripped_cherry_log": (87, 65, 62),
    "stripped_cherry_log": (87, 65, 62),
    "stripped_crimson_stem": (48, 22, 33),
    "stripped_crimson_stem": (48, 22, 33),
    "stripped_dark_oak_log": (26, 17, 9),
    "stripped_dark_oak_log": (26, 17, 9),
    "stripped_jungle_log": (65, 48, 32),
    "stripped_jungle_log": (65, 48, 32),
    "stripped_mangrove_log": (43, 17, 17),
    "stripped_mangrove_log": (43, 17, 17),
    "stripped_oak_log": (63, 51, 30),
    "stripped_oak_log": (63, 51, 30),
    "stripped_spruce_log": (42, 31, 18),
    "stripped_spruce_log": (42, 31, 18),
    "stripped_warped_stem": (20, 51, 49),
    "stripped_warped_stem": (20, 51, 49),
    "stripped_bamboo_block": (70, 62, 29),
    "stripped_bamboo_block": (70, 62, 29),
    "bamboo_block": (50, 56, 23),
    "bamboo_block": (55, 56, 24),
    "bamboo_block": (55, 56, 24),
    "basalt": (29, 29, 31),
    "basalt": (32, 32, 34),
    "basalt": (32, 32, 34),
    "bone_block": (90, 89, 82),
    "bone_block": (82, 81, 69),
    "bone_block": (82, 81, 69),
    "deepslate": (31, 30, 31),
    "deepslate": (34, 34, 34),
    "deepslate": (34, 34, 34),
    "muddy_mangrove_roots": (27, 23, 19),
    "muddy_mangrove_roots": (27, 23, 18),
    "muddy_mangrove_roots": (27, 23, 18),
    "polished_basalt": (35, 35, 36),
    "polished_basalt": (39, 39, 40),
    "polished_basalt": (39, 39, 40),
    "purpur_pillar": (67, 51, 67),
    "purpur_pillar": (67, 50, 67),
    "purpur_pillar": (67, 50, 67),
    "quartz_pillar": (93, 91, 88),
    "quartz_pillar": (92, 90, 87),
    "quartz_pillar": (92, 90, 87),
    "hay_block": (65, 53, 15),
    "hay_block": (65, 55, 5),
    "hay_block": (65, 55, 5),
    "carved_pumpkin": (59, 33, 7),
    "beehive": (71, 57, 35),
    "beehive": (71, 57, 35),
    "beehive": (62, 50, 31),
    "blast_furnace": (32, 31, 32),
    "blast_furnace": (32, 31, 32),
    "blast_furnace": (42, 43, 42),
    "furnace": (43, 43, 43),
    "furnace": (43, 43, 43),
    "furnace": (36, 36, 36),
    "bee_nest": (79, 63, 29),
    "bee_nest": (63, 50, 35),
    "bee_nest": (72, 56, 30),
    "loom": (56, 47, 36),
    "loom": (30, 24, 14),
    "loom": (58, 47, 32),
    "smoker": (33, 33, 32),
    "smoker": (42, 41, 40),
    "smoker": (35, 29, 23),
    "bookshelf": (46, 37, 24),
    "chiseled_red_sandstone": (72, 38, 11),
    "chiseled_sandstone": (85, 80, 61),
    "cut_red_sandstone": (74, 40, 13),
    "cut_sandstone": (85, 81, 42),
    "crying_obsidian": (13, 4, 24),
    "glowstone": (67, 51, 33),
    "jack_o_lantern": (84, 60, 21),
    "magma_block": (56, 25, 13),
    "shroomlight": (95, 58, 28),
    "composter": (46, 28, 13),
    "composter": (44, 27, 13),
    "crafting_table": (51, 42, 27),
    "crafting_table": (47, 29, 16),
    "observer": (28, 27, 27),
    "observer": (38, 39, 38),
    "observer": (38, 39, 38),
    "piston": (43, 41, 38),
    "piston": (43, 41, 38),
    "piston": (60, 50, 33),
    "sticky_piston": (48, 58, 36),
    "dispenser": (31, 31, 31),
    "dropper": (48, 48, 48),
    "bedrock": (33, 33, 33),
    "reinforced_deepslate": (31, 33, 31),
    "reinforced_deepslate": (40, 43, 39),
    "reinforced_deepslate": (32, 32, 31),
    "dried_kelp_block": (20, 24, 15),
    "dried_kelp_block": (20, 23, 15),
    "dried_kelp_block": (15, 19, 12),
    "honey_block": (98, 73, 21),
    "honey_block": (95, 57, 7),
    "honey_block": (98, 74, 23),
    "smithing_table": (22, 23, 28),
    "smithing_table": (25, 11, 9),
    "smithing_table": (22, 14, 14),
}

palette_small = {
    "bedrock": (33, 33, 33),
    "acacia_planks": (66, 35, 20),
    "acacia_wood": (40, 38, 34),
    "amethyst_block": (53, 38, 75),
    "andesite": (53, 53, 54),
    "bamboo_planks": (76, 68, 31),
    "bamboo_mosaic": (75, 67, 31),
    "birch_planks": (75, 69, 47),
    "birch_wood": (85, 84, 82),
    "black_concrete": (3, 4, 6),
    "black_glazed_terracotta": (27, 12, 13),
    "black_terracotta": (15, 9, 6),
    "black_wool": (8, 9, 10),
    "blue_concrete": (18, 18, 56),
    "blue_glazed_terracotta": (18, 25, 55),
    "blue_terracotta": (29, 24, 36),
    "blue_wool": (21, 22, 62),
    "bricks": (59, 38, 33),
    "brown_concrete": (38, 25, 13),
    "brown_glazed_terracotta": (47, 42, 34),
    "brown_mushroom_block": (58, 44, 32),
    "brown_terracotta": (30, 20, 14),
    "brown_wool": (45, 28, 16),
    "calcite": (87, 88, 87),
    "cherry_planks": (89, 70, 68),
    "cherry_wood": (22, 13, 17),
    "chiseled_deepslate": (21, 21, 22),
    "chiseled_nether_bricks": (18, 9, 11),
    "chiseled_polished_blackstone": (21, 20, 22),
    "chiseled_stone_bricks": (47, 48, 47),
    "clay": (63, 65, 70),
    "coal_block": (6, 6, 6),
    "coal_ore": (42, 42, 41),
    "coarse_dirt": (47, 34, 23),
    "cobbled_deepslate": (30, 30, 32),
    "cobblestone": (50, 50, 50),
    "copper_ore": (49, 49, 47),
    "cracked_deepslate_bricks": (25, 25, 25),
    "cracked_deepslate_tiles": (21, 21, 21),
    "cracked_nether_bricks": (16, 8, 9),
    "cracked_polished_blackstone_bricks": (17, 15, 17),
    "cracked_stone_bricks": (46, 47, 46),
    "crimson_hyphae": (36, 10, 12),
    "crimson_planks": (40, 19, 28),
    "cyan_concrete": (8, 48, 53),
    "cyan_glazed_terracotta": (20, 47, 49),
    "cyan_terracotta": (34, 36, 36),
    "cyan_wool": (8, 54, 57),
    "dark_oak_planks": (26, 18, 8),
    "dark_oak_wood": (25, 17, 8),
    "dark_prismarine": (20, 36, 30),
    "deepslate_bricks": (28, 28, 28),
    "deepslate_coal_ore": (29, 29, 30),
    "deepslate_copper_ore": (36, 36, 35),
    "deepslate_diamond_ore": (33, 42, 42),
    "deepslate_emerald_ore": (31, 41, 35),
    "deepslate_gold_ore": (45, 40, 31),
    "deepslate_iron_ore": (42, 39, 37),
    "deepslate_lapis_ore": (31, 36, 45),
    "deepslate_redstone_ore": (41, 29, 29),
    "deepslate_tiles": (22, 22, 22),
    "diamond_block": (38, 93, 89),
    "diamond_ore": (47, 55, 55),
    "diorite": (74, 74, 74),
    "dirt": (53, 38, 26),
    "dripstone_block": (53, 42, 36),
    "emerald_block": (16, 80, 35),
    "emerald_ore": (46, 54, 49),
    "end_stone": (86, 87, 62),
    "end_stone_bricks": (85, 88, 64),
    "gilded_blackstone": (22, 17, 15),
    "gold_block": (96, 82, 24),
    "gold_ore": (57, 53, 42),
    "granite": (58, 40, 34),
    "gray_concrete": (22, 24, 24),
    "gray_glazed_terracotta": (33, 35, 37),
    "gray_terracotta": (23, 16, 14),
    "gray_wool": (25, 27, 28),
    "green_concrete": (29, 36, 14),
    "green_glazed_terracotta": (46, 56, 26),
    "green_terracotta": (30, 33, 16),
    "green_wool": (33, 43, 11),
    "honeycomb_block": (90, 58, 12),
    "iron_block": (86, 86, 86),
    "iron_ore": (53, 51, 48),
    "jungle_planks": (63, 45, 32),
    "jungle_wood": (33, 27, 10),
    "lapis_block": (12, 26, 55),
    "lapis_ore": (42, 46, 55),
    "light_blue_concrete": (14, 54, 78),
    "light_blue_glazed_terracotta": (37, 65, 82),
    "light_blue_terracotta": (44, 43, 54),
    "light_blue_wool": (23, 69, 85),
    "light_gray_concrete": (49, 49, 45),
    "light_gray_glazed_terracotta": (56, 65, 66),
    "light_gray_terracotta": (53, 42, 38),
    "light_gray_wool": (56, 56, 53),
    "lime_concrete": (37, 66, 10),
    "lime_glazed_terracotta": (64, 78, 22),
    "lime_terracotta": (41, 46, 21),
    "lime_wool": (44, 73, 10),
    "magenta_concrete": (66, 19, 62),
    "magenta_glazed_terracotta": (82, 39, 75),
    "magenta_terracotta": (59, 35, 43),
    "magenta_wool": (75, 27, 71),
    "mangrove_wood": (33, 26, 16),
    "mangrove_planks": (46, 21, 19),
    "moss_block": (35, 43, 18),
    "mossy_cobblestone": (43, 47, 37),
    "mossy_stone_bricks": (45, 47, 41),
    "mud": (24, 22, 24),
    "mud_bricks": (54, 40, 31),
    "mushroom_stem": (80, 77, 73),
    "nether_bricks": (17, 9, 10),
    "nether_gold_ore": (45, 22, 16),
    "nether_quartz_ore": (46, 26, 24),
    "nether_wart_block": (45, 1, 1),
    "netherite_block": (26, 24, 25),
    "netherrack": (38, 15, 15),
    "note_block": (35, 23, 16),
    "oak_planks": (64, 51, 31),
    "oak_wood": (43, 33, 20),
    "obsidian": (6, 4, 10),
    "orange_concrete": (88, 38, 0),
    "orange_glazed_terracotta": (61, 58, 36),
    "orange_terracotta": (64, 33, 15),
    "orange_wool": (95, 46, 8),
    "packed_mud": (56, 42, 31),
    "pink_concrete": (84, 40, 56),
    "pink_glazed_terracotta": (92, 61, 71),
    "pink_terracotta": (64, 31, 31),
    "pink_wool": (93, 55, 67),
    "polished_andesite": (52, 53, 53),
    "polished_blackstone": (21, 19, 22),
    "polished_blackstone_bricks": (19, 17, 20),
    "polished_deepslate": (28, 29, 29),
    "polished_diorite": (76, 76, 76),
    "polished_granite": (60, 42, 35),
    "powder_snow": (97, 99, 99),
    "prismarine": (39, 61, 59),
    "prismarine_bricks": (39, 67, 62),
    "purple_concrete": (39, 13, 61),
    "purple_glazed_terracotta": (43, 19, 60),
    "purple_terracotta": (46, 27, 34),
    "purple_wool": (44, 16, 68),
    "purpur_block": (67, 49, 67),
    "quartz_block": (93, 90, 87),
    "quartz_bricks": (92, 91, 87),
    "raw_copper_block": (60, 42, 31),
    "raw_gold_block": (87, 66, 18),
    "raw_iron_block": (65, 53, 42),
    "red_concrete": (56, 13, 13),
    "red_glazed_terracotta": (71, 24, 21),
    "red_mushroom_block": (78, 18, 18),
    "red_nether_bricks": (27, 3, 4),
    "red_terracotta": (56, 24, 18),
    "red_wool": (63, 15, 14),
    "redstone_block": (69, 10, 2),
    "redstone_lamp": (37, 22, 12),
    "redstone_ore": (55, 43, 43),
    "rooted_dirt": (56, 41, 30),
    "sculk": (5, 11, 14),
    "slime_block": (44, 75, 36),
    "smooth_basalt": (29, 28, 31),
    "smooth_quartz": (93, 90, 88),
    "smooth_red_sandstone": (71, 38, 12),
    "smooth_sandstone": (88, 84, 67),
    "smooth_stone": (62, 62, 62),
    "snow_block": (98, 100, 100),
    "soul_sand": (32, 24, 20),
    "soul_soil": (30, 23, 18),
    "sponge": (77, 75, 29),
    "spruce_planks": (45, 34, 19),
    "spruce_wood": (23, 15, 7),
    "stone": (49, 50, 49),
    "stone_bricks": (48, 49, 48),
    "stripped_acacia_wood": (69, 36, 24),
    "stripped_birch_wood": (77, 69, 46),
    "stripped_cherry_wood": (84, 57, 58),
    "stripped_crimson_hyphae": (54, 22, 35),
    "stripped_dark_oak_wood": (28, 22, 14),
    "stripped_jungle_wood": (67, 52, 33),
    "stripped_mangrove_wood": (47, 21, 18),
    "stripped_oak_wood": (69, 57, 34),
    "stripped_spruce_wood": (45, 35, 20),
    "stripped_warped_hyphae": (23, 59, 58),
    "terracotta": (60, 37, 27),
    "tuff": (42, 43, 40),
    "warped_hyphae": (23, 23, 31),
    "warped_planks": (17, 41, 39),
    "warped_wart_block": (9, 47, 47),
    "waxed_copper_block": (75, 42, 31),
    "waxed_cut_copper": (75, 42, 32),
    "waxed_exposed_copper": (63, 49, 41),
    "waxed_exposed_cut_copper": (61, 48, 40),
    "waxed_oxidized_copper": (32, 64, 52),
    "waxed_oxidized_cut_copper": (31, 60, 49),
    "waxed_weathered_copper": (42, 60, 43),
    "waxed_weathered_cut_copper": (43, 57, 42),
    "wet_sponge": (67, 71, 27),
    "white_concrete": (81, 84, 84),
    "white_glazed_terracotta": (74, 83, 80),
    "white_terracotta": (82, 70, 63),
    "white_wool": (92, 93, 93),
    "yellow_concrete": (95, 69, 8),
    "yellow_glazed_terracotta": (92, 75, 35),
    "yellow_terracotta": (73, 52, 14),
    "yellow_wool": (98, 78, 16),
}


from PIL import ImageOps, Image


def get_pixels(path):
    i = Image.open(path)
    i = i.resize((100, 100))
    i = ImageOps.flip(i)
    i = ImageOps.mirror(i)
    pixels = i.load()
    width, height = i.size

    return [[pixels[x, y] for x in range(width)] for y in range(height)]


def draw_picture(x_offset, path, picker):
    pos1 = (x_offset, 60, -5)
    pos2 = (x_offset + 100, 160, -5)
    zone = mc.BlockZone(pos1, pos2)
    mc.set_zone(zone, "air")

    pixels = get_pixels(path)
    for y, row in enumerate(pixels):
        for x, p in enumerate(row):
            pos = (x + x_offset, y + 60, -5)
            closest_color = find_closest_color(p, picker=picker)

            ret = mc.set_block(pos, closest_color)
            if "Could not" in ret:
                print(ret)
            # print(closest_color, pos)


def find_closest_color(pixel, picker):
    if picker == "old":
        pixel = (pixel[0], pixel[1], pixel[2])
        return mc.color_picker(pixel, mc.get_palette("side"))
    elif picker == "alex":
        closest = math.inf
        palette = petalette
        for p in palette:
            r = palette[p][0]
            g = palette[p][1]
            b = palette[p][2]

            distance = math.sqrt(
                (pixel[0] - r) ** 2 + (pixel[1] - g) ** 2 + (pixel[2] - b) ** 2
            )

            if distance < closest:
                closest = distance
                closest_color = p

        return closest_color

    elif picker == "full" or picker == "small":
        closest = math.inf
        if picker == "full":
            palette = palette_full
        else:
            palette = palette_small
        for p in palette:
            mult = 255 / 100
            r = palette[p][0] * mult
            g = palette[p][1] * mult
            b = palette[p][2] * mult

            distance = math.sqrt(
                (pixel[0] - r) ** 2 + (pixel[1] - g) ** 2 + (pixel[2] - b) ** 2
            )

            if distance < closest:
                closest = distance
                closest_color = p

        return closest_color


def print_palette(x_offset, picker=False):
    print(mc.post(f"sudo StarlightmOB //pos1 {x_offset},0,0"))
    print(mc.post(f"sudo StarlightmOB //pos2 {x_offset + 100},100,100"))
    print(mc.post(f"sudo StarlightmOB //cut"))
    time.sleep(1)

    for x in range(SIZE):
        for y in range(SIZE):
            for z in range(SIZE):
                mult = 255 / SIZE
                color_to_match = (
                    math.floor(x * mult),
                    math.floor(y * mult),
                    math.floor(z * mult),
                )
                pixel = (x * 2 + x_offset, y * 2, z * 2)
                closest_color = find_closest_color(color_to_match, picker=picker)
                mc.set_block(pixel, closest_color)
                light_pos = (pixel[0], pixel[1] + 1, pixel[1])
                mc.set_block(light_pos, "light")


def remove_shulkers():
    cmd = "kill @e[type=minecraft:shulker]"
    print(mc.post(cmd))


def print_original_palette(palette, x_offset):
    for k in palette:
        x, y, z = palette[k]
        cmd = f"""summon shulker {x + x_offset} {y} {z} {{Invulnerable:1b,Glowing:1b,CustomNameVisible:1b,NoAI:1b,AttachFace:0b,CustomName:'{{"text":"{k}"}}',ActiveEffects:[{{Id:14,Amplifier:1b,Duration:2000000}}]}}"""
        mc.post(cmd)


SPACE_BETWEEN = 120


# print_original_palette(palette_small, 0)
# print_original_palette(palette_full, 120)
# remove_shulkers()
import random

pickers = ["old", "small", "full", "alex"]
# pickers_to_try = ["old", "small", "full", "alex"]
pickers_to_try = ["alex"]


while True:
    png_file_paths = glob.glob(os.path.join("png/", "*"))
    path = random.choice(png_file_paths)
    print("next_image:", path)

    for p in pickers_to_try:
        for i, _ in enumerate(pickers):
            if p == _:
                x_offset = (1 + i) * SPACE_BETWEEN
                print("picker=", p)
                # print_palette(x_offset, picker=p)
                draw_picture(x_offset, path, picker=p)

    # time.sleep(10)
    input("Press Enter for next image...")
