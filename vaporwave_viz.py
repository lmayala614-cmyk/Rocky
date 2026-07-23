import math
import random
import colorsys

def init_vaporwave(sw, sh):
    return {
        "time": 0,
        "beat": 0.0,
        "sub_beat": 0.0,
        "grid_offset": 0.0,
        "hue_shift": 0.0,
        "sun_rays": [random.uniform(0, math.pi * 2) for _ in range(12)],
    }

def draw_vaporwave(scene, screen, pygame, sw, sh, is_playing,
                   bass_level=0.0, mid_level=0.0, treble_level=0.0):
    s = scene
    s["time"] += 1

    if bass_level > 0.01 or mid_level > 0.01:
        s["beat"] = min(1.0, bass_level * 2.0)
        s["sub_beat"] = min(1.0, mid_level * 1.5)
    else:
        breathe = (math.sin(s["time"] * 0.018) + 1) / 2
        breathe2 = (math.sin(s["time"] * 0.031 + 1.0) + 1) / 2
        if is_playing:
            s["beat"] = breathe * 0.35
            s["sub_beat"] = breathe2 * 0.25
        else:
            s["beat"] = max(0.0, s["beat"] - 0.01)
            s["sub_beat"] = max(0.0, s["sub_beat"] - 0.01)

    beat = s["beat"]
    sub = s["sub_beat"]
    t = s["time"]

    speed = 1.5 + beat * 4.0 if is_playing else 0.3
    s["grid_offset"] = (s["grid_offset"] + speed) % 100
    s["hue_shift"] = (s["hue_shift"] + 0.3 + beat * 2) % 360

    def hsv(h, sat, v, a=255):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, sat, v)
        return (int(r*255), int(g*255), int(b*255), a)

    # Background — deep purple to black
    screen.fill((8, 0, 18))

    cx = sw // 2
    horizon = int(sh * 0.52)

    # Sky gradient — layers of color
    sky_colors = [
        (20, 0, 40),
        (40, 0, 60),
        (60, 10, 80),
        (80, 20, 60),
        (100, 30, 40),
    ]
    band_h = horizon // len(sky_colors)
    for i, col in enumerate(sky_colors):
        r = min(255, col[0] + int(beat * 40))
        g = min(255, col[1] + int(beat * 20))
        b = min(255, col[2] + int(beat * 30))
        pygame.draw.rect(screen, (r, g, b),
                        (0, i * band_h, sw, band_h + 1))

    # Sun — large circle with rings
    sun_y = int(horizon * 0.6)
    sun_r = int(60 + beat * 20)
    sun_col = hsv(s["hue_shift"], 0.6, 1.0)

    # Sun rings
    for i in range(8):
        ring_r = sun_r + i * 12 + int(beat * 5)
        alpha = max(0, int(180 - i * 22))
        ring_surf = pygame.Surface((ring_r*2, ring_r*2), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf,
                          (*sun_col[:3], alpha),
                          (ring_r, ring_r), ring_r, 2)
        screen.blit(ring_surf, (cx - ring_r, sun_y - ring_r))

    # Sun body — horizontal scan lines (vaporwave style)
    for y in range(sun_y - sun_r, sun_y + sun_r):
        dx = math.sqrt(max(0, sun_r**2 - (y - sun_y)**2))
        if dx < 1:
            continue
        # Alternate solid and gap lines
        line_idx = (y - (sun_y - sun_r))
        if line_idx % 8 < 5 or y < sun_y:
            hue = (s["hue_shift"] + (y - sun_y) * 0.5) % 360
            col = hsv(hue, 0.7, 1.0)
            pygame.draw.line(screen, col,
                           (int(cx - dx), y), (int(cx + dx), y))

    # Reflection on ground
    refl_surf = pygame.Surface((sw, sh - horizon), pygame.SRCALPHA)
    for i in range(6):
        refl_y = i * 20
        refl_alpha = max(0, int(60 - i * 10))
        refl_w = int(30 + beat * 10) - i * 4
        if refl_w > 0:
            pygame.draw.line(refl_surf,
                           (*sun_col[:3], refl_alpha),
                           (cx - refl_w, refl_y),
                           (cx + refl_w, refl_y), 2)
    screen.blit(refl_surf, (0, horizon))

    # Grid floor
    grid_surf = pygame.Surface((sw, sh - horizon), pygame.SRCALPHA)
    grid_hue = (s["hue_shift"] + 180) % 360
    grid_col = hsv(grid_hue, 0.9, 0.9)
    grid_col2 = hsv((grid_hue + 40) % 360, 0.8, 0.7)

    vp_y = 0  # vanishing point relative to grid surface
    vp_x = sw // 2

    # Horizontal lines with wave distortion
    num_h_lines = 16
    for i in range(num_h_lines):
        progress = (i / num_h_lines +
                   s["grid_offset"] / 100) % 1.0
        base_y = int((sh - horizon) * (progress ** 1.5))
        if base_y < 1:
            continue
        perspective = progress
        line_alpha = int(40 + perspective * 180)
        line_alpha = min(255, line_alpha + int(beat * 60))
        thickness = max(1, int(perspective * 2))

        # Draw wave — sample points across width
        points = []
        num_pts = 40
        for p in range(num_pts + 1):
            px = int(sw * p / num_pts)
            wave_amp = (8 + beat * 12) * perspective
            wave = math.sin(px * 0.02 + s["time"] * 0.05 + i * 0.5) * wave_amp
            py = base_y + int(wave)
            py = max(0, min(sh - horizon - 1, py))
            points.append((px, py))

        if len(points) > 1:
            pygame.draw.lines(grid_surf,
                            (*grid_col[:3], line_alpha),
                            False, points, thickness)

    # Vertical lines
    num_v_lines = 14
    for i in range(num_v_lines + 1):
        t_val = i / num_v_lines
        # Lines converge at vanishing point
        x_bottom = int(sw * t_val)
        x_mid = int(vp_x + (x_bottom - vp_x) * 0.1)

        dist_from_center = abs(t_val - 0.5)
        line_alpha = int(80 + (1 - dist_from_center * 2) * 140)
        line_alpha = min(255, line_alpha + int(beat * 40))

        pygame.draw.line(grid_surf, (*grid_col2[:3], line_alpha),
                        (x_mid, vp_y),
                        (x_bottom, sh - horizon), 1)

    screen.blit(grid_surf, (0, horizon))

    # Horizon line glow
    glow_h = max(2, int(3 + beat * 6))
    glow_col = hsv(s["hue_shift"] + 20, 1.0, 1.0)
    pygame.draw.rect(screen, glow_col[:3],
                    (0, horizon - glow_h//2, sw, glow_h))

    # Scanlines overlay — subtle CRT effect
    scan_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
    for y in range(0, sh, 4):
        pygame.draw.line(scan_surf, (0, 0, 0, 30), (0, y), (sw, y))
    screen.blit(scan_surf, (0, 0))

    # Beat flash on bass hit
    if beat > 0.7:
        flash = pygame.Surface((sw, sh), pygame.SRCALPHA)
        flash_col = hsv(s["hue_shift"], 0.5, 1.0)
        flash.fill((*flash_col[:3], int((beat - 0.7) * 60)))
        screen.blit(flash, (0, 0))

    return scene