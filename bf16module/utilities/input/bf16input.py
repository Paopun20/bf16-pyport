import pygame

class BF16input:
    """
    Reads key state and maps it to an 8-bit input value.
    Returns:
        int: Bitflag representation of key states.
    """
    @staticmethod
    def get_key_state():
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        key = 0
        if keys[pygame.K_z]: key |= 0x80
        if keys[pygame.K_x]: key |= 0x40
        if keys[pygame.K_RETURN]: key |= 0x20
        if keys[pygame.K_SPACE]: key |= 0x10
        if keys[pygame.K_UP]: key |= 0x08
        if keys[pygame.K_DOWN]: key |= 0x04
        if keys[pygame.K_LEFT]: key |= 0x02
        if keys[pygame.K_RIGHT]: key |= 0x01
        return key