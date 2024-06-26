import numpy as np
from PIL import Image, ImageTk
import random
import tkinter as tk

# Konfigurasi ukuran peta dan sel
map_width, map_height = 150, 150 
cell_size = 32  # Ukuran setiap sel dalam piksel

# Menginisialisasi peta
city_map = np.zeros((map_height * cell_size, map_width * cell_size, 3), dtype=np.uint8) #menyimpan Array matriks 3D gambar peta
occupied_map = np.zeros((map_height, map_width), dtype=bool)  # array 2D yang digunakan menyimpan status sel ditempati 

# Warna jalan dan garis
road_color = [128, 128, 128]  # Warna jalan
line_color = [255, 255, 255]  # Warna garis putus-putus di tengah jalan
main_road_flag = np.zeros((map_height, map_width), dtype=bool)  # Menandai jalan utama

# Fungsi untuk menggambar garis putus-putus di tengah jalan utama
def draw_center_line(image, start, end):# menggambar jalan putus-putus
    if start[0] == end[0]:  # jalan vertikal
        for y in range(start[1], end[1] + 1):
            if y % 2 == 0:
                image[y * cell_size:(y + 1) * cell_size, start[0] * cell_size + cell_size // 2 - 1:start[0] * cell_size + cell_size // 2 + 1] = line_color
    else:  # Jalan horizontal
        for x in range(start[0], end[0] + 1):
            if x % 2 == 0:
                image[start[1] * cell_size + cell_size // 2 - 1:start[1] * cell_size + cell_size // 2 + 1, x * cell_size:(x + 1) * cell_size] = line_color

# Fungsi untuk menggambar jalan
def draw_road(image, start, end, is_main_road=False): #fungsi gambar jalan
    if start[0] == end[0]:  # Jalan vertikal
        for y in range(start[1], end[1] + 1):
            if 0 <= y < map_height and 0 <= start[0] < map_width:
                image[y * cell_size:(y + 1) * cell_size, start[0] * cell_size:(start[0] + 1) * cell_size] = road_color
                occupied_map[y, start[0]] = True
                if is_main_road:
                    main_road_flag[y, start[0]] = True
        if is_main_road:
            draw_center_line(image, start, end)
    else:  # Jalan horizontal
        for x in range(start[0], end[0] + 1):
            if 0 <= start[1] < map_height and 0 <= x < map_width:
                image[start[1] * cell_size:(start[1] + 1) * cell_size, x * cell_size:(x + 1) * cell_size] = road_color
                occupied_map[start[1], x] = True 
                if is_main_road:
                    main_road_flag[start[1], x] = True
        if is_main_road:
            draw_center_line(image, start, end)

# Fungsi untuk menggambar jalan di sekitar bangunan tanpa menghubungkannya ke jalan utama
def ensure_road_around_building(top_left, size):
    for dy in range(-1, size[1] + 1):
        for dx in range(-1, size[0] + 1):
            if (dx == -1 or dx == size[0]) or (dy == -1 or dy == size[1]):
                x, y = top_left[0] + dx, top_left[1] + dy
                if 0 <= x < map_width and 0 <= y < map_height and not occupied_map[y, x]:
                    draw_road(city_map, (x, y), (x, y))

# Fungsi untuk menempatkan bangunan di sisi jalan utama
def place_building_on_side_of_main_road(image_path, size, max_attempts=1000):
    main_road_coords = np.argwhere(main_road_flag)#koordinat jalan utama
    if len(main_road_coords) == 0:
        return False

    for attempt in range(max_attempts):
        y, x = random.choice(main_road_coords)
        # Pilih arah acak untuk menempatkan bangunan di sisi jalan utama
        direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])  # Kanan, Kiri, Bawah, Atas
        dx, dy = direction
        top_left = (x + dx, y + dy)

        # Koordinat sudut kanan bawah bangunan
        bottom_right = (top_left[0] + size[0], top_left[1] + size[1])

        if 0 <= top_left[0] < map_width and 0 <= top_left[1] < map_height and bottom_right[0] <= map_width and bottom_right[1] <= map_height:
            if not occupied_map[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]].any():
                try:
                    building = Image.open(image_path).convert('RGB')
                    building = building.resize((size[0] * cell_size, size[1] * cell_size), Image.LANCZOS)
                    y_start = top_left[1] * cell_size
                    y_end = y_start + size[1] * cell_size
                    x_start = top_left[0] * cell_size
                    x_end = x_start + size[0] * cell_size
                    city_map[y_start:y_end, x_start:x_end] = np.array(building)
                    occupied_map[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = True
                    ensure_road_around_building(top_left, size)
                    return True
                except FileNotFoundError:
                    print(f"File not found: {image_path}")
                    return False
    return False


# Fungsi untuk menempatkan objek secara acak di sel yang kosong
def place_object_randomly(image_path, size, count):
    for _ in range(count):
        placed = False
        while not placed:
            x, y = random.randint(0, map_width - size[0]), random.randint(0, map_height - size[1])
            if not occupied_map[y:y + size[1], x:x + size[0]].any():
                try:
                    obj_image = Image.open(image_path).convert('RGB')
                    obj_image = obj_image.resize((size[0] * cell_size, size[1] * cell_size), Image.LANCZOS)
                    y_start = y * cell_size
                    y_end = y_start + size[1] * cell_size
                    x_start = x * cell_size
                    x_end = x_start + size[0] * cell_size
                    city_map[y_start:y_end, x_start:x_end] = np.array(obj_image)
                    occupied_map[y:y + size[1], x:x + size[0]] = True
                    placed = True
                except FileNotFoundError:
                    print(f"File not found: {image_path}")
                    return

# Fungsi untuk membagi peta menggunakan partitioning space binary
def binary_space_partition(x, y, width, height, min_size, roads):
    if width < min_size * 2 and height < min_size * 2:
        return

    horizontal_split = random.choice([True, False])
    if width < min_size * 2:
        horizontal_split = True
    if height < min_size * 2:
        horizontal_split = False

    if horizontal_split:
        split = random.randint(min_size, height - min_size)
        roads.append(((x, y + split), (x + width - 1, y + split)))
        draw_road(city_map, (x, y + split), (x + width - 1, y + split), is_main_road=True)
        binary_space_partition(x, y, width, split, min_size, roads)
        binary_space_partition(x, y + split + 1, width, height - split - 1, min_size, roads)
    else:
        split = random.randint(min_size, width - min_size)
        roads.append(((x + split, y), (x + split, y + height - 1)))
        draw_road(city_map, (x + split, y), (x + split, y + height - 1), is_main_road=True)
        binary_space_partition(x, y, split, height, min_size, roads)
        binary_space_partition(x + split + 1, y, width - split - 1, height, min_size, roads)

    for road in roads:
        draw_road(city_map, road[0], road[1], is_main_road=True)


# Fungsi untuk memperluas jalan buntu ke tepi kanvas atau jalan lain
def extend_road_to_edge_or_road():
    for y in range(map_height):
        for x in range(map_width):
            if occupied_map[y, x]:
                if x == 0 or not occupied_map[y, x - 1]:
                    extend_road(city_map, (x, y), (-1, 0))  # Kiri
                if x == map_width - 1 or not occupied_map[y, x + 1]:
                    extend_road(city_map, (x, y), (1, 0))  # Kanan
                if y == 0 or not occupied_map[y - 1, x]:
                    extend_road(city_map, (x, y), (0, -1))  # Atas
                if y == map_height - 1 or not occupied_map[y + 1, x]:
                    extend_road(city_map, (x, y), (0, 1))  # Bawah

# Fungsi untuk memperluas jalan dari posisi yang ditentukan
def extend_road(image, start, direction):
    x, y = start
    dx, dy = direction
    while 0 <= x < map_width and 0 <= y < map_height and not occupied_map[y, x]:
        image[y * cell_size:(y + 1) * cell_size, x * cell_size:(x + 1) * cell_size] = road_color
        draw_center_line(image, (x, y), (x + dx, y + dy))
        occupied_map[y, x] = True
        x += dx
        y += dy

# Fungsi untuk desain ulang kota
def redesign_city():
    global city_map, occupied_map, main_road_flag
    city_map.fill(0)  # Membersihkan peta
    occupied_map.fill(False)  # Membersihkan status peta
    main_road_flag.fill(False)  # Membersihkan tanda jalan utama

    grass_color = [224, 236, 139]  # Warna hijau untuk area kosong

    roads = []
    # Buat jalan dengan algoritma BSP
    binary_space_partition(0, 0, map_width, map_height, 20, roads)

    # Perluas jalan buntu ke tepi kanvas atau jalan lain
    extend_road_to_edge_or_road()

    # Tempatkan bangunan di sisi jalan utama
    for _ in range(4): place_building_on_side_of_main_road("asset/Big Building.png", (10, 5))
    for _ in range(8): place_building_on_side_of_main_road("asset/Medium Building.png", (5, 3))
    for _ in range(12): place_building_on_side_of_main_road("asset/Small Building.png", (2, 2))
    for _ in range(15): place_building_on_side_of_main_road("asset/House.png", (1, 2))

    # Tempatkan objek secara acak
    place_object_randomly("asset/batu.png", (1, 1), 200)
    place_object_randomly("asset/kolam.png", (10, 10), 5)
    place_object_randomly("asset/pohon.png", (2, 2), 200)

    # Warna hijau untuk area kosong
    for y in range(map_height):
        for x in range(map_width):
            if not occupied_map[y, x]:
                city_map[y * cell_size:(y + 1) * cell_size, x * cell_size:(x + 1) * cell_size] = grass_color

# Fungsi untuk memperbarui tampilan peta
def update_map():
    redesign_city()
    final_map = Image.fromarray(city_map)
    zoom_level = 2
    final_map_resized = final_map.resize((map_width * cell_size // zoom_level, map_height * cell_size // zoom_level), Image.LANCZOS)  # Zoom 1:4
    img_tk = ImageTk.PhotoImage(final_map_resized)

    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.image = img_tk  # Simpan referensi gambar untuk mencegah garbage collection
    canvas.config(scrollregion=canvas.bbox(tk.ALL))  # Set scrollregion after image is created

# GUI setup
root = tk.Tk()
root.title("IKN Design City")

# Frame utama untuk canvas dan scrollbars
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Frame untuk tombol dan scrollbar horizontal
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

# Setup canvas untuk menampilkan gambar
canvas = tk.Canvas(frame, width=800, height=600)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbars
hbar = tk.Scrollbar(bottom_frame, orient=tk.HORIZONTAL, command=canvas.xview)
hbar.pack(side=tk.BOTTOM, fill=tk.X)
vbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
vbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

# Button to redesign map
button = tk.Button(bottom_frame, text="Redesign Map", command=update_map)
button.pack(side=tk.TOP)

# Menampilkan peta awal
update_map()

root.mainloop()