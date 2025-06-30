class bf16color:
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