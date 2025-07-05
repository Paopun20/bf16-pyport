class BF16color:
    @staticmethod
    def rgb332(val):
        r = ((val >> 5) & 0x07) * 255 // 7
        g = ((val >> 2) & 0x07) * 255 // 7
        b = (val & 0x03) * 255 // 3
        color = (r, g, b)
        return color
    
    @staticmethod
    def grayscale(val):
        color = (val, val, val)
        return color

    @staticmethod
    def binary_bw(val):
        # Black if <127.5, White if ≥128
        return (0, 0, 0) if val < 127.5 else (255, 255, 255)

    @staticmethod
    def redscale(val):
        val &= 0xFF
        return (val, 0, 0)

    @staticmethod
    def greenscale(val):
        val &= 0xFF
        return (0, val, 0)

    @staticmethod
    def bluescale(val):
        val &= 0xFF
        return (0, 0, val)

    @staticmethod
    def rainbow(val):
        """Maps value to a visible color in a rainbow spectrum using HSV."""
        import colorsys
        h = (val % 256) / 256.0
        r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def cmyk(val):
        """Maps value to CMYK-like colors."""
        c = ((val >> 6) & 0x03) * 255 // 3  # Cyan
        m = ((val >> 4) & 0x03) * 255 // 3  # Magenta
        y = ((val >> 2) & 0x03) * 255 // 3  # Yellow
        k = (val & 0x03) * 255 // 3         # Black (inverted for display)

        # Convert CMYK to RGB for display
        r = 255 - min(255, c + k)
        g = 255 - min(255, m + k)
        b = 255 - min(255, y + k)
        return (r, g, b)

    @staticmethod
    def fire(val):
        """Maps value to fire-like colors (red, orange, yellow)."""
        r = min(255, val * 2)
        g = min(255, (val - 64) * 2) if val > 64 else 0
        b = min(255, (val - 128) * 2) if val > 128 else 0
        return (r, g, b)

    @staticmethod
    def ice(val):
        """Maps value to ice-like colors (blue, cyan, white)."""
        r = min(255, (val - 128) * 2) if val > 128 else 0
        g = min(255, (val - 64) * 2) if val > 64 else 0
        b = min(255, val * 2)
        return (r, g, b)

    @staticmethod
    def forest(val):
        """Maps value to forest-like colors (greens, browns)."""
        r = min(255, val // 2 + 50)
        g = min(255, val * 2)
        b = min(255, val // 4)
        return (r, g, b)

    @staticmethod
    def purple(val):
        """Maps value to purple-like colors."""
        r = min(255, val * 1)
        g = 0
        b = min(255, val * 1.5)
        return (r, g, b)
    
    @staticmethod
    def pastel(val):
        """Maps value to pastel colors."""
        r = 128 + (val // 2)
        g = 128 + (val // 3)
        b = 128 + (val // 4)
        return (min(255, r), min(255, g), min(255, b))
    
    @staticmethod
    def neon(val):
        """Maps value to neon colors."""
        r = 0
        g = 0
        b = 0
        if val < 85: # Neon Green
            r = int(val * 3)
            g = 255
        elif val < 170: # Neon Blue
            g = 255 - int((val - 85) * 3)
            b = 255
        else: # Neon Pink
            r = 255
            b = 255 - int((val - 170) * 3)
        return (r, g, b)
    
    @staticmethod
    def thermal(val):
        """Maps value to thermal-like colors (blue to red)."""
        # Blue at low values, transitioning to red at high values
        r = min(255, val * 2)
        g = min(255, val * 2) if val < 128 else max(0, 255 - (val - 128) * 2)
        b = max(0, 255 - val * 2)
        return (r, g, b)
    
    @staticmethod
    def circuit(val):
        """ TBS (the broken script) Circuit LOL """
        val = 255 if val > 0 else 0
        return (val, val, val)