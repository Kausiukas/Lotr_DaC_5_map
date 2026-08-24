import os, sys, re, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"D:\Steam\steamapps\common\Medieval II Total War\mods\Divide_and_Conquer\data\world\maps\base"
camp_dir = r"D:\Steam\steamapps\common\Medieval II Total War\mods\Divide_and_Conquer\data\world\maps\campaign\imperial_campaign"
text_dir = r"D:\Steam\steamapps\common\Medieval II Total War\mods\Divide_and_Conquer\data\text"
out_dir = r"D:\m2tw_mod\rendered_maps"
os.makedirs(out_dir, exist_ok=True)

# 1. Parse official region and settlement names from imperial_campaign_regions_and_settlement_names.txt
print("1. Parsing official localized settlement and province names...")
loc_names = {}
fpath_loc = f"{text_dir}/imperial_campaign_regions_and_settlement_names.txt"
if os.path.exists(fpath_loc):
    with open(fpath_loc, "r", encoding="utf-16", errors="ignore") as f:
        for line in f:
            m = re.match(r"^\{([^}]+)\}\s*(.*)", line.strip())
            if m:
                loc_names[m.group(1).strip()] = m.group(2).strip()

def get_prov_name(tag):
    if tag in loc_names: return loc_names[tag]
    return tag.replace("_Province", "").replace("_", " ")

def get_sett_name(tag):
    if tag in loc_names: return loc_names[tag]
    return tag.replace("_", " ")

# Official DaC 5 Faction Names
faction_display_titles = {
    'sicily': 'Kingdom of Gondor',
    'denmark': 'Principality of Dol Amroth',
    'milan': 'Kingdom of Rohan',
    'normans': 'Bree-land & The Shire',
    'turks': 'Northern Dúnedain',
    'scotland': 'Kingdom of Dale',
    'timurids': 'Anduin Vale (Beornings)',
    'byzantium': 'Vale of Dorwinion',
    'moors': 'Dwarves of Erebor',
    'hungary': 'Dwarves of Ered Luin',
    'norway': 'Dwarves of Khazad-dûm',
    'saxons': 'High Elves (Lindon & Rivendell)',
    'ireland': 'Realm of Lothlórien',
    'mongols': 'Woodland Realm (Thranduil)',
    'teutonic_order': 'Clans of Enedwaith',
    'venice': 'Easterlings of Rhûn',
    'england': 'Mordor',
    'poland': 'Dol Guldur',
    'france': 'Dominion of Isengard',
    'aztecs': 'Dunlendings',
    'hre': 'Goblins of Moria',
    'gundabad': 'Orcs of Gundabad',
    'portugal': 'Remnants of Angmar',
    'spain': 'Haradrim Tribes',
    'khand': 'Variags of Khand',
    'russia': 'Ar-Adûnâim (Horde Start)',
    'papal_states': 'Dark Lord of Mordor',
    'slave': 'Independent Realms'
}

# Distinctive, Lore-Accurate Faction Colors
faction_palette = {
    "sicily": (220, 235, 255),       # Gondor (Silver/White-Blue)
    "denmark": (30, 90, 190),        # Dol Amroth (Swan Blue)
    "milan": (40, 155, 55),          # Rohan (Rohan Green)
    "normans": (185, 155, 95),       # Bree-land & Shire (Gold/Tan)
    "turks": (65, 110, 165),         # Northern Dúnedain (Ranger Blue)
    "scotland": (50, 140, 180),      # Dale (Lake-town Blue)
    "timurids": (170, 120, 55),      # Anduin Vale (Beornings Wood Brown)
    "byzantium": (155, 75, 120),     # Dorwinion (Grape/Purple)
    "moors": (160, 40, 45),          # Erebor Dwarves (Royal Crimson)
    "hungary": (70, 115, 175),       # Ered Luin Dwarves (Steel Blue)
    "norway": (105, 115, 130),       # Khazad-dûm Dwarves (Iron Gray)
    "saxons": (120, 180, 235),       # High Elves (Elven Azure)
    "ireland": (145, 190, 65),       # Lothlórien (Mallorn Gold-Green)
    "mongols": (75, 145, 45),        # Woodland Realm (Silvan Moss Green)
    "teutonic_order": (185, 145, 60),# Enedwaith (Ochre)
    "venice": (215, 155, 30),        # Rhûn (Easterling Gold)
    "england": (195, 20, 20),        # Mordor (Eye of Sauron Red)
    "poland": (35, 95, 45),          # Dol Guldur (Dark Poison Green)
    "france": (115, 75, 75),         # Isengard (White Hand Iron Gray)
    "aztecs": (155, 100, 55),        # Dunland (Clay Brown)
    "hre": (110, 65, 80),            # Moria Goblins (Dark Plum)
    "gundabad": (165, 35, 35),       # Gundabad (Blood Red)
    "portugal": (75, 60, 95),        # Angmar (Shadow Violet)
    "spain": (205, 55, 35),          # Harad (Scarlet)
    "khand": (235, 115, 25),         # Khand (Sunburst Orange)
    "russia": (45, 45, 55),          # Umbar (Obsidian Black)
    "papal_states": (195, 20, 20),   # Mordor Dark Lord
    "slave": (175, 175, 175)         # Independent / Rebels (Neutral Gray)
}

# 2. Parse descr_regions.txt
print("2. Parsing descr_regions.txt...")
with open(f"{base_dir}/descr_regions.txt", "r", encoding="latin-1") as f:
    text = f.read()

lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith(";")]
regions = {}
rgb_to_region = {}

idx = 0
while idx < len(lines):
    reg_tag = lines[idx]
    idx += 1
    if idx >= len(lines): break
    if lines[idx].startswith("legion:"):
        idx += 1
        if idx >= len(lines): break
    set_tag = lines[idx]
    idx += 1
    creator = lines[idx] if idx < len(lines) else ""
    idx += 1
    rebel_type = lines[idx] if idx < len(lines) else ""
    idx += 1
    rgb_str = lines[idx] if idx < len(lines) else ""
    idx += 1
    
    resources = ""
    if idx < len(lines) and not lines[idx].isdigit() and not lines[idx].startswith("religions"):
        resources = lines[idx]
        idx += 1
    
    while idx < len(lines) and not re.match(r"^\d+\s+\d+\s+\d+$", lines[idx]):
        if lines[idx].startswith("religions"):
            idx += 1
            break
        idx += 1
    
    parts = [int(p) for p in rgb_str.split() if p.isdigit()]
    if len(parts) == 3:
        rgb = tuple(parts)
        reg_info = {
            "region_tag": reg_tag,
            "region_display": get_prov_name(reg_tag),
            "settlement_tag": set_tag,
            "settlement_display": get_sett_name(set_tag),
            "creator": creator,
            "rgb": rgb,
            "resources": resources,
            "owner": "slave",
            "owner_display": "Independent Realms",
            "settlement_pos": None,
            "port_pos": None
        }
        regions[reg_tag] = reg_info
        rgb_to_region[rgb] = reg_info

# 3. Parse descr_strat.txt for exact starting faction ownership
print("3. Parsing descr_strat.txt for starting faction ownership...")
with open(f"{camp_dir}/descr_strat.txt", "r", encoding="latin-1") as f:
    strat_text = f.read()

strat_lines = strat_text.splitlines()
current_faction = None

for i, line in enumerate(strat_lines):
    line_clean = line.split(";")[0].strip()
    m_fac = re.match(r"^faction\s+([a-zA-Z0-9_]+)", line_clean)
    if m_fac:
        current_faction = m_fac.group(1)
        continue
    if line_clean.startswith("settlement"):
        reg = None
        for j in range(i+1, min(i+15, len(strat_lines))):
            lj = strat_lines[j].split(";")[0].strip()
            m_reg = re.match(r"^region\s+([a-zA-Z0-9_\-]+)", lj)
            if m_reg:
                reg = m_reg.group(1)
                break
        if reg and current_faction and reg in regions:
            if reg == "Umbar_Province" and current_faction == "russia":
                regions[reg]["owner"] = "slave"
                regions[reg]["owner_display"] = "Independent Realms"
            else:
                regions[reg]["owner"] = current_faction
                regions[reg]["owner_display"] = faction_display_titles.get(current_faction, current_faction.replace("_", " ").title())

# 4. Load map_regions.tga & map settlements/ports
print("4. Locating all settlements and ports on map_regions.tga...")
img_reg = Image.open(f"{base_dir}/map_regions.tga").convert("RGB")
w_reg, h_reg = img_reg.size
arr_reg = np.array(img_reg)

black_mask = (arr_reg[:, :, 0] == 0) & (arr_reg[:, :, 1] == 0) & (arr_reg[:, :, 2] == 0)
white_mask = (arr_reg[:, :, 0] == 255) & (arr_reg[:, :, 1] == 255) & (arr_reg[:, :, 2] == 255)

settlement_locs = []
for y, x in np.argwhere(black_mask):
    found_rgb = None
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h_reg and 0 <= nx < w_reg:
                c = tuple(arr_reg[ny, nx])
                if c in rgb_to_region:
                    found_rgb = c
                    break
        if found_rgb: break
    if found_rgb:
        reg_info = rgb_to_region[found_rgb]
        reg_info["settlement_pos"] = (int(x), int(y))
        settlement_locs.append((int(x), int(y), reg_info))

port_locs = []
for y, x in np.argwhere(white_mask):
    found_rgb = None
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h_reg and 0 <= nx < w_reg:
                c = tuple(arr_reg[ny, nx])
                if c in rgb_to_region:
                    found_rgb = c
                    break
        if found_rgb: break
    if found_rgb:
        port_locs.append((int(x), int(y)))

print(f"Located {len(settlement_locs)} settlements and {len(port_locs)} ports.")

# 5. Load map_heights, ground_types, climates
print("5. Loading topography, heights, ground types, and climates...")
img_h = Image.open(f"{base_dir}/map_heights.tga").convert("RGBA")
arr_h = np.array(img_h)[:, :, 0].astype(float)
h_h, w_h = arr_h.shape

img_gt = Image.open(f"{base_dir}/map_ground_types.tga").convert("RGB")
arr_gt = np.array(img_gt)

img_cl = Image.open(f"{base_dir}/map_climates.tga").convert("RGB")
arr_cl = np.array(img_cl)

# Strict 3-channel Sea Mask (Only pure ocean/deep/shallow sea: R>0, G=0, B=0 AND height==0)
is_ocean = (arr_gt[:, :, 0] == 64) & (arr_gt[:, :, 1] == 0) & (arr_gt[:, :, 2] == 0)
is_deep = (arr_gt[:, :, 0] == 128) & (arr_gt[:, :, 1] == 0) & (arr_gt[:, :, 2] == 0)
is_shallow = (arr_gt[:, :, 0] == 196) & (arr_gt[:, :, 1] == 0) & (arr_gt[:, :, 2] == 0)
is_sea = (arr_h == 0) & (is_ocean | is_deep | is_shallow)

# 6. Compute Hillshading with NW solar lighting
scale_z = 0.28
dx = np.gradient(arr_h, axis=1) * scale_z
dy = np.gradient(arr_h, axis=0) * scale_z

az = np.radians(315.0)
alt = np.radians(45.0)

nx = -dx; ny = -dy; nz = np.ones_like(arr_h)
norm = np.sqrt(nx*nx + ny*ny + nz*nz)
nx /= norm; ny /= norm; nz /= norm

lx = np.sin(az) * np.cos(alt)
ly = -np.cos(az) * np.cos(alt)
lz = np.sin(alt)

diffuse = np.clip(nx * lx + ny * ly + nz * lz, 0, 1)
shade = 0.35 + 0.65 * diffuse

# 7. Rivers from map_features.tga
img_feat = Image.open(f"{base_dir}/map_features.tga").convert("RGB")
arr_feat = np.array(img_feat)
river_mask = (arr_feat[:, :, 0] == 0) & (arr_feat[:, :, 1] == 0) & (arr_feat[:, :, 2] == 255)
river_source = (arr_feat[:, :, 0] == 0) & (arr_feat[:, :, 1] == 255) & (arr_feat[:, :, 2] == 255)
crossing_mask = (arr_feat[:, :, 0] == 0) & (arr_feat[:, :, 1] == 255) & (arr_feat[:, :, 2] == 0)
all_rivers = river_mask | river_source | crossing_mask

# 8. RENDER PHYSICAL TERRAIN MAP
print("6. Rendering Physical Topographic Map with accurate Settlement & Province labels...")
out_w, out_h = 2040, 1948
scale_x = out_w / w_reg
scale_y = out_h / h_reg

topo_base = np.zeros((h_h, w_h, 3), dtype=np.float32)

for y in range(h_h):
    for x in range(w_h):
        if is_sea[y, x]:
            if is_ocean[y, x]: topo_base[y, x] = [18, 38, 75]
            elif is_deep[y, x]: topo_base[y, x] = [24, 50, 95]
            else: topo_base[y, x] = [32, 68, 120]
            continue
            
        h = arr_h[y, x]
        gt = tuple(arr_gt[y, x])
        cl = tuple(arr_cl[y, x])
        
        # Biomes & Lore:
        if cl == (102, 45, 145):
            if gt in [(0, 64, 0), (0, 128, 0)]: base_c = [65, 80, 50] # Nurn crops
            elif h > 70 or gt in [(64, 64, 64), (98, 65, 65), (196, 128, 128)]: base_c = [38, 34, 36]
            else: base_c = [52, 45, 43] # Gorgoroth plains
        elif cl in [(146, 39, 143), (0, 114, 188)] or gt == (255, 255, 255):
            if cl == (0, 114, 188): base_c = [185, 165, 110]
            else: base_c = [215, 185, 125]
        elif gt == (0, 64, 0):
            if 420 <= y <= 460 and 510 <= x <= 550 and cl == (242, 101, 34):
                base_c = [85, 120, 35] # Lothlórien
            else:
                base_c = [25, 65, 28]
        elif gt == (0, 128, 0): base_c = [45, 95, 45]
        elif gt == (0, 255, 128): base_c = [68, 85, 55]
        elif gt in [(196, 128, 128), (64, 64, 64), (98, 65, 65)] or h > 115:
            if h > 160 and y < 650: base_c = [235, 240, 245]
            elif h > 90: base_c = [118, 114, 110]
            else: base_c = [135, 130, 115]
        elif cl == (237, 20, 91):
            if gt in [(101, 124, 0), (96, 160, 64)]: base_c = [105, 160, 60]
            else: base_c = [95, 145, 58]
        elif cl == (237, 28, 36): base_c = [160, 150, 85]
        elif gt in [(101, 124, 0), (96, 160, 64)]: base_c = [95, 150, 60]
        elif cl == (141, 198, 63) or gt == (128, 128, 64): base_c = [120, 135, 80]
        elif cl == (247, 148, 29): base_c = [75, 118, 60]
        else: base_c = [85, 135, 60]
            
        s = shade[y, x]
        topo_base[y, x] = [base_c[0] * s, base_c[1] * s, base_c[2] * s]

topo_base = np.clip(topo_base, 0, 255).astype(np.uint8)
topo_hires = Image.fromarray(topo_base).resize((out_w, out_h), Image.BILINEAR)

# Add Rivers
river_img = Image.fromarray((all_rivers * 255).astype(np.uint8)).resize((out_w, out_h), Image.NEAREST)
river_arr = np.array(river_img) > 100
topo_arr_final = np.array(topo_hires)
topo_arr_final[river_arr] = [38, 90, 165]
final_topo = Image.fromarray(topo_arr_final)

draw_topo = ImageDraw.Draw(final_topo)

try:
    font_settlement = ImageFont.truetype("arialbd.ttf", 15)
    font_region = ImageFont.truetype("arial.ttf", 11)
    font_title = ImageFont.truetype("arialbd.ttf", 36)
    font_legend = ImageFont.truetype("arialbd.ttf", 18)
    font_legend_sub = ImageFont.truetype("arial.ttf", 14)
except:
    font_settlement = font_region = font_title = font_legend = font_legend_sub = ImageFont.load_default()

for x, y, reg in settlement_locs:
    sx = int((x + 0.5) * scale_x)
    sy = int((y + 0.5) * scale_y)
    
    # Gold / Black Pin for Settlement
    draw_topo.ellipse([sx-5, sy-5, sx+5, sy+5], fill=(255, 220, 80), outline=(10, 10, 10), width=1)
    
    s_name = reg["settlement_display"]
    r_name = reg["region_display"]
    
    tx = sx + 8 if sx < out_w - 200 else sx - len(s_name)*9 - 8
    ty = sy - 10 if sy > 35 else sy + 10
    
    # Settlement Name in bold
    for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,1), (0,-1), (1,0), (-1,0)]:
        draw_topo.text((tx+ox, ty+oy), s_name, font=font_settlement, fill=(0, 0, 0))
    draw_topo.text((tx, ty), s_name, font=font_settlement, fill=(255, 255, 240))
    
    # Province Name underneath in brackets
    r_text = f"[{r_name}]"
    r_ty = ty + 16
    for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        draw_topo.text((tx+ox, r_ty+oy), r_text, font=font_region, fill=(0, 0, 0))
    draw_topo.text((tx, r_ty), r_text, font=font_region, fill=(200, 220, 255))

draw_topo.rectangle([30, 30, 680, 100], fill=(15, 20, 30), outline=(200, 180, 120), width=3)
draw_topo.text((50, 42), "DIVIDE AND CONQUER v5", font=font_title, fill=(230, 200, 110))
draw_topo.text((50, 78), "Middle-earth Topographic Map - Settlements & Provinces", font=font_legend_sub, fill=(200, 200, 200))

topo_out_path = f"{out_dir}/physical_terrain_map_dac5.png"
final_topo.save(topo_out_path, format="PNG")
print(f"Saved Physical Terrain Map: {topo_out_path}")

# 9. RENDER POLITICAL MAP
print("7. Rendering Political Map with accurate Settlement & Province labels...")
political_arr = np.zeros((h_reg, w_reg, 3), dtype=np.uint8)

for y in range(h_reg):
    for x in range(w_reg):
        rgb = tuple(arr_reg[y, x])
        if rgb in rgb_to_region:
            reg = rgb_to_region[rgb]
            fac = reg["owner"]
            col = faction_palette.get(fac, (175, 175, 175))
            political_arr[y, x] = col
        else: # Sea / Water
            political_arr[y, x] = (22, 45, 85)

pol_img = Image.fromarray(political_arr).resize((out_w, out_h), Image.NEAREST)

# Blend hillshade for depth
shaded_resized = Image.fromarray((shade * 255).astype(np.uint8)).resize((out_w, out_h), Image.BILINEAR)
shaded_arr = np.array(shaded_resized).astype(float) / 255.0
shaded_3d_hires = np.stack([shaded_arr, shaded_arr, shaded_arr], axis=2)

pol_arr_hires = np.array(pol_img).astype(float)
blended_pol = pol_arr_hires * (0.55 + 0.45 * shaded_3d_hires)
blended_pol = np.clip(blended_pol, 0, 255).astype(np.uint8)

# Province Borders
reg_id_map = np.zeros((h_reg, w_reg), dtype=np.int32)
reg_lookup_list = list(regions.values())
for i, reg in enumerate(reg_lookup_list):
    r_mask = (arr_reg[:, :, 0] == reg["rgb"][0]) & (arr_reg[:, :, 1] == reg["rgb"][1]) & (arr_reg[:, :, 2] == reg["rgb"][2])
    reg_id_map[r_mask] = i + 1

grad_y = np.abs(np.diff(reg_id_map, axis=0, append=reg_id_map[-1:, :])) > 0
grad_x = np.abs(np.diff(reg_id_map, axis=1, append=reg_id_map[:, -1:])) > 0
borders_mask = grad_y | grad_x

border_img = Image.fromarray((borders_mask * 255).astype(np.uint8)).resize((out_w, out_h), Image.NEAREST)
border_arr = np.array(border_img) > 100

blended_pol[border_arr] = [20, 20, 20]
blended_pol[river_arr] = [40, 90, 160]
final_pol = Image.fromarray(blended_pol)

draw_pol = ImageDraw.Draw(final_pol)

for px, py in port_locs:
    sx = int((px + 0.5) * scale_x)
    sy = int((py + 0.5) * scale_y)
    draw_pol.ellipse([sx-4, sy-4, sx+4, sy+4], fill=(0, 220, 255), outline=(0, 50, 100), width=1)

for x, y, reg in settlement_locs:
    sx = int((x + 0.5) * scale_x)
    sy = int((y + 0.5) * scale_y)
    draw_pol.ellipse([sx-7, sy-7, sx+7, sy+7], fill=(255, 215, 0), outline=(20, 20, 20), width=2)
    draw_pol.ellipse([sx-3, sy-3, sx+3, sy+3], fill=(200, 30, 30), outline=(20, 20, 20), width=1)
    
    s_name = reg["settlement_display"]
    r_name = reg["region_display"]
    
    tx = sx + 9 if sx < out_w - 200 else sx - len(s_name)*9 - 10
    ty = sy - 10 if sy > 35 else sy + 10
    
    # Settlement Name in bold white
    for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,1), (0,-1), (1,0), (-1,0)]:
        draw_pol.text((tx+ox, ty+oy), s_name, font=font_settlement, fill=(0, 0, 0))
    draw_pol.text((tx, ty), s_name, font=font_settlement, fill=(255, 255, 255))
    
    # Province Name in brackets
    r_text = f"[{r_name}]"
    r_ty = ty + 16
    for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        draw_pol.text((tx+ox, r_ty+oy), r_text, font=font_region, fill=(0, 0, 0))
    draw_pol.text((tx, r_ty), r_text, font=font_region, fill=(230, 230, 180))

draw_pol.rectangle([30, 30, 680, 100], fill=(15, 20, 30), outline=(200, 180, 120), width=3)
draw_pol.text((50, 42), "DIVIDE AND CONQUER v5", font=font_title, fill=(230, 200, 110))
draw_pol.text((50, 78), "Middle-earth Campaign Map - Settlements & Starting Territories", font=font_legend_sub, fill=(200, 200, 200))

# Faction Legend Box
legend_factions = [
    ("sicily", "Kingdom of Gondor"),
    ("denmark", "Principality of Dol Amroth"),
    ("milan", "Kingdom of Rohan"),
    ("normans", "Bree-land & The Shire"),
    ("turks", "Northern Dúnedain"),
    ("scotland", "Kingdom of Dale"),
    ("timurids", "Anduin Vale (Beornings)"),
    ("byzantium", "Vale of Dorwinion"),
    ("moors", "Dwarves of Erebor"),
    ("hungary", "Dwarves of Ered Luin"),
    ("norway", "Dwarves of Khazad-dûm"),
    ("saxons", "High Elves (Lindon/Rivendell)"),
    ("ireland", "Realm of Lothlórien"),
    ("mongols", "Woodland Realm (Thranduil)"),
    ("teutonic_order", "Clans of Enedwaith"),
    ("venice", "Easterlings of Rhûn"),
    ("england", "Mordor"),
    ("poland", "Dol Guldur"),
    ("france", "Dominion of Isengard"),
    ("aztecs", "Dunlendings"),
    ("hre", "Goblins of Moria"),
    ("gundabad", "Orcs of Gundabad"),
    ("portugal", "Remnants of Angmar"),
    ("spain", "Haradrim Tribes"),
    ("khand", "Variags of Khand"),
    ("russia", "Ar-Adûnâim (Horde Start)"),
    ("slave", "Independent Realms")
]

leg_x, leg_y = 30, out_h - 430
draw_pol.rectangle([leg_x, leg_y, leg_x + 520, leg_y + 400], fill=(15, 20, 30), outline=(200, 180, 120), width=2)
draw_pol.text((leg_x + 20, leg_y + 12), "FACTION STARTING TERRITORIES", font=font_legend, fill=(230, 200, 110))

for i, (fac_key, fac_label) in enumerate(legend_factions):
    col = faction_palette.get(fac_key, (175, 175, 175))
    col_idx = i // 14
    row_idx = i % 14
    bx = leg_x + 20 + col_idx * 245
    by = leg_y + 45 + row_idx * 24
    draw_pol.rectangle([bx, by, bx + 16, by + 16], fill=col, outline=(255, 255, 255), width=1)
    draw_pol.text((bx + 24, by), fac_label, font=font_legend_sub, fill=(230, 230, 230))

pol_out_path = f"{out_dir}/political_map_dac5.png"
final_pol.save(pol_out_path, format="PNG")
print(f"Saved Political Map: {pol_out_path}")

# 10. Interactive Web Viewer Data
settlement_data_json = []
for x, y, reg in settlement_locs:
    settlement_data_json.append({
        "name": reg["settlement_display"],
        "region": reg["region_display"],
        "faction": reg["owner_display"],
        "creator": reg["creator"],
        "resources": reg["resources"],
        "x": int((x + 0.5) * scale_x),
        "y": int((y + 0.5) * scale_y)
    })

map_data_obj = {
    "width": out_w,
    "height": out_h,
    "settlements": settlement_data_json
}

with open(f"{out_dir}/map_data.json", "w", encoding="utf-8") as f:
    json.dump(map_data_obj, f, indent=2)

json_str = json.dumps(map_data_obj)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Divide and Conquer v5 - Middle-earth Campaign Map Explorer</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    body, html { margin: 0; padding: 0; height: 100%; width: 100%; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0b0e14; color: #e0e0e0; }
    #map { height: 100%; width: 100%; background: #0b0e14; }
    #sidebar {
      position: absolute; top: 15px; right: 15px; z-index: 1000;
      background: rgba(18, 24, 38, 0.94); border: 1px solid #c8a858;
      border-radius: 8px; padding: 15px; width: 340px; box-shadow: 0 4px 20px rgba(0,0,0,0.6);
      backdrop-filter: blur(4px);
    }
    h2 { margin: 0 0 10px 0; font-size: 17px; color: #e6c86e; text-transform: uppercase; letter-spacing: 1px; }
    .search-box { width: 100%; padding: 8px 12px; box-sizing: border-box; border-radius: 4px; border: 1px solid #444; background: #1b2230; color: #fff; margin-bottom: 10px; font-size: 14px; }
    .search-box:focus { outline: none; border-color: #c8a858; }
    .info-card { background: #131924; border: 1px solid #323d52; border-radius: 6px; padding: 12px; margin-top: 10px; }
    .info-title { font-size: 18px; font-weight: bold; color: #ffd700; margin-bottom: 2px; }
    .info-prov { font-size: 13px; color: #78a6ff; margin-bottom: 8px; }
    .info-row { margin: 5px 0; font-size: 13px; }
    .info-label { color: #8fa0b8; }
    .results-list { max-height: 180px; overflow-y: auto; margin-top: 5px; list-style: none; padding: 0; }
    .results-list li { padding: 6px 8px; border-bottom: 1px solid #222c3d; cursor: pointer; font-size: 13px; }
    .results-list li:hover { background: #26334a; color: #ffd700; }
    .leaflet-container { background: #0b0e14 !important; }
    .leaflet-control-layers { background: rgba(18, 24, 38, 0.94) !important; color: #fff !important; border: 1px solid #c8a858 !important; border-radius: 6px !important; }
  </style>
</head>
<body>
  <div id="map"></div>
  <div id="sidebar">
    <h2>Campaign Map Explorer</h2>
    <input type="text" id="search" class="search-box" placeholder="Search settlement, province, faction..." />
    <ul id="results" class="results-list"></ul>
    <div id="info" class="info-card">
      <div class="info-title">Divide and Conquer v5</div>
      <div class="info-row" style="margin-top:6px; color:#aaa;">Click any settlement marker or search above to view its exact settlement name, province, and starting faction owner.</div>
    </div>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const data = __JSON_DATA__;

    const w = data.width;
    const h = data.height;
    
    const map = L.map('map', {
      crs: L.CRS.Simple,
      minZoom: -2,
      maxZoom: 2,
      zoomSnap: 0.25
    });

    const bounds = [[0, 0], [h, w]];
    
    const politicalLayer = L.imageOverlay('political_map_dac5.png', bounds);
    const physicalLayer = L.imageOverlay('physical_terrain_map_dac5.png', bounds);
    const loreLayer = L.imageOverlay('base_map_FE.jpg', bounds);

    politicalLayer.addTo(map);
    map.fitBounds(bounds);

    const baseMaps = {
      "Political Territories": politicalLayer,
      "Physical / Topography": physicalLayer,
      "Tolkien Parchment Art": loreLayer
    };

    const markersGroup = L.layerGroup().addTo(map);

    data.settlements.forEach(s => {
      const lat = h - s.y;
      const lng = s.x;
      const marker = L.circleMarker([lat, lng], {
        radius: 6,
        fillColor: '#ffd700',
        color: '#111',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.95
      });

      marker.on('click', () => showInfo(s));
      marker.bindTooltip('<b>' + s.name + '</b><br><span style="color:#80b3ff;">[' + s.region + ']</span><br><small style="color:#ffd700;">' + s.faction + '</small>', { direction: 'top' });
      markersGroup.addLayer(marker);
      s._marker = marker;
    });

    L.control.layers(baseMaps, { "Settlement Markers": markersGroup }, { position: 'topleft' }).addTo(map);

    function showInfo(s) {
      document.getElementById('info').innerHTML = 
        '<div class="info-title">' + s.name + '</div>' +
        '<div class="info-prov">Province: <b>' + s.region + '</b></div>' +
        '<div class="info-row"><span class="info-label">Starting Owner:</span> <span style="color:#ffd700; font-weight:bold;">' + s.faction + '</span></div>' +
        '<div class="info-row"><span class="info-label">Culture Creator:</span> ' + s.creator + '</div>' +
        '<div class="info-row" style="margin-top:8px;"><span class="info-label">Resources & Traits:</span><br><small style="color:#bbb;">' + (s.resources || 'None') + '</small></div>';
    }

    const searchInput = document.getElementById('search');
    const resultsList = document.getElementById('results');

    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      resultsList.innerHTML = '';
      if (!query) return;

      const filtered = data.settlements.filter(s => 
        s.name.toLowerCase().includes(query) || 
        s.region.toLowerCase().includes(query) ||
        s.faction.toLowerCase().includes(query)
      ).slice(0, 10);

      filtered.forEach(s => {
        const li = document.createElement('li');
        li.innerHTML = `<b>${s.name}</b> <span style="color:#78a6ff;">[${s.region}]</span> <small style="color:#8fa0b8;">(${s.faction})</small>`;
        li.addEventListener('click', () => {
          map.setView([h - s.y, s.x], 1);
          showInfo(s);
          s._marker.openTooltip();
        });
        resultsList.appendChild(li);
      });
    });
  </script>
</body>
</html>"""

html_final = html_template.replace('__JSON_DATA__', json_str)
with open(f"{out_dir}/index.html", "w", encoding="utf-8") as f:
    f.write(html_final)

print("Generated all files successfully with exact settlement and province names.")
