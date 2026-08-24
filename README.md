# Divide & Conquer v5 - Middle-earth Campaign Map & Interactive Explorer

High-resolution 2D rendered maps and interactive Leaflet map explorer generated directly from the raw game data of **Medieval II: Total War: Divide and Conquer (DaC) v5**.

---

## 🌟 Features

- 🏔️ **Topographic & Physical Terrain Map ($2040 \times 1948$)**:
  - Exact sea/water masking derived from `map_heights.tga` and strict 3-channel `map_ground_types.tga` classification.
  - Northwest solar hillshading algorithm ($315^\circ$ azimuth, $45^\circ$ elevation) with vector surface normals.
  - Lore-accurate Tolkien biomes: Mediterranean Gondor, golden Haradrim sands, volcanic Gorgoroth/Mordor ash, golden Mallorn wood of Lothlórien, and snow-capped peaks.
  - Real river systems, headwater springs, and river crossings extracted from `map_features.tga`.

- 🗺️ **Political & Starting Factions Map ($2040 \times 1948$)**:
  - Full territory breakdown of all **28 campaign factions** parsed strictly from `descr_strat.txt`.
  - Crisp province border lines across all **199 provinces**.
  - Distinct faction banners and color palettes.

- 📍 **Precise Settlement & Port Mapping**:
  - Sub-pixel coordinate mapping from `map_regions.tga` (199 settlements, 80 ports) directly into geographic terrain features (mountain passes, river crossings, valleys).
  - Dual labeling displaying **Exact Settlement Name** (*e.g., Minas Tirith, Barad-dûr, Hornburg, Caras Galadhon*) and **Province / Region Name** (*e.g., Pelennor Fields, Plains of Orodruin, Helm's Deep, Lothlórien*).

- 📜 **Tolkien Vintage Hand-Drawn Parchment Map ($3200 \times 2400$)**:
  - High-resolution original artwork from `map_FE.tga`.
  - Dynamic pin positioning: settlement markers smoothly calculate their locations on the vintage hand-drawn artwork without warping or distorting the original illustration.

- 🌐 **Interactive Web Explorer (`index.html`)**:
  - Multi-layer toggle between Political, Topography, and Vintage Parchment maps.
  - Instant live search by settlement name, province, faction, or cultural origin.
  - Detailed inspector card showing starting faction owner, cultural/architectural heritage, religious demographics, and trade resources.
  - Zero external web server dependencies (native standalone browser compatibility).

---

## 📂 Repository Structure

```
├── rendered_maps/
│   ├── index.html                     # Standalone interactive map viewer
│   ├── political_map_dac5.png         # High-resolution 2040x1948 political territory map
│   ├── physical_terrain_map_dac5.png  # High-resolution 2040x1948 physical terrain map
│   ├── base_map_FE.jpg                # Original 3200x2400 vintage Tolkien parchment art
│   └── map_data.json                  # Settlement metadata & dual-coordinate database
├── index.html                         # Root interactive explorer (GitHub Pages ready)
├── render_maps.py                     # Python rendering engine
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. View the Interactive Map
Simply open `index.html` (or `rendered_maps/index.html`) in any modern web browser.

### 2. Re-generating the Maps
To re-render the high-resolution maps from raw Medieval II mod data:
```bash
pip install numpy pillow scipy opencv-python
python render_maps.py
```

---

## 📜 Credits & Lore Data
- **Mod**: Divide and Conquer (DaC) for Medieval II: Total War (Kingdoms)
- **Universe**: J.R.R. Tolkien's Middle-earth
