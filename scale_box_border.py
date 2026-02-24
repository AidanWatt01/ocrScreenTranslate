import os
import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

input_dir = "assets/tooltip"
output_dir = "assets/tooltip_small"
os.makedirs(output_dir, exist_ok=True)

scale_factor = 0.4

for filename in os.listdir(input_dir):
    if filename.endswith(".png"):
        path_in = os.path.join(input_dir, filename)
        path_out = os.path.join(output_dir, filename)

        try:
            img = pygame.image.load(path_in).convert_alpha()
            w, h = img.get_size()

            if w == 0 or h == 0:
                print(f"⚠️ Skipping {filename} — invalid size {w}x{h}")
                continue

            img_scaled = pygame.transform.scale(img, (int(w * scale_factor), int(h * scale_factor)))
            pygame.image.save(img_scaled, path_out)
            print(f"✅ Scaled {filename} to {img_scaled.get_size()}")

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")

print("🎉 Done scaling all border slices.")
