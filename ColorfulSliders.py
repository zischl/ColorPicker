class ColorfulSliders():
    def compute_h_line(width, length):
        pixels = np.zeros((width, length, 4), dtype=np.uint8)
        for y in range(width):
            for x in range(length):
                if y < width/2 and x in range(0, 16-y): continue
                if y == width/2 and x in range(y): continue
                if y > width/2 and x in range(y): continue
                if y < width/2 and x in range(length-16+y, length): continue
                if y == width/2 and x in range(length-16, length): continue
                if y > width/2 and x in range(length, length-y, -1): continue
                hue = x / length
                r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")
    
    def compute_s_line(self, width, length, hue, s, v):
        s = s if s else (x / (length - 1))
        v = v if v else (y / (length - 1))
        # center = size // 2
        pixels = np.zeros((width, length, 4), dtype=np.uint8)
        hue = hue/360
        for y in range(width):
            for x in range(length):
                r, g, b = colorsys.hsv_to_rgb(hue, s, v)
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")
    
    def compute_v_line(self, width, length, hue):
        # center = size // 2
        pixels = np.zeros((width, length, 4), dtype=np.uint8)
        hue = hue/360
        for y in range(width):
            for x in range(length):
                r, g, b = colorsys.hsv_to_rgb(hue, 1, (x / (length - 1)))
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")
    
    def compute_RGB_line(self, width, length, hue):
        # center = size // 2
        pixels = np.zeros((width, length, 4), dtype=np.uint8)
        hue = hue/360
        for y in range(width):
            for x in range(length):
                r, g, b = colorsys.hsv_to_rgb(hue, 1, (x / (length - 1)))
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")