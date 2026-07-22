import math
import random

def make_star(screen_w, screen_h):
    angle = random.uniform(0, 2 * math.pi)
    dist = (random.random() ** 0.6) * min(screen_w, screen_h) * 0.55
    return {
        "base_x": screen_w/2 + math.cos(angle) * dist,
        "base_y": screen_h/2 + math.sin(angle) * dist,
        "x": 0, "y": 0,
        "size": 0.4 + (random.random() ** 2) * 2.5,
        "base_alpha": 0.15 + random.random() * 0.75,
        "twinkle": random.uniform(0, math.pi * 2),
        "twinkle_speed": 0.015 + random.random() * 0.03,
        "dance_angle": random.uniform(0, math.pi * 2),
        "dance_speed": 0.008 + random.random() * 0.015,
        "dance_radius": 1 + random.random() * 4,
        "hue_offset": (random.random() - 0.5) * 80,
        "pulse_strength": 0.3 + random.random() * 0.7,
    }


def make_nebula(screen_w, screen_h, index):
    return {
        "x": random.random() * screen_w,
        "y": random.random() * screen_h,
        "r": 80 + random.random() * 160,
        "base_alpha": 0.04 + random.random() * 0.06,
        "vx": (random.random() - 0.5) * 0.12,
        "vy": (random.random() - 0.5) * 0.08,
        "hue_offset": index * 30,
    }


def make_shooter(screen_w, hue_base):
    angle = math.pi * 0.1 + random.random() * math.pi * 0.3
    return {
        "x": random.random() * screen_w * 0.5,
        "y": random.random() * 100,
        "angle": angle,
        "speed": 5 + random.random() * 5,
        "length": 80 + random.random() * 100,
        "alpha": 0.9,
        "hue": (hue_base + (random.random() - 0.5) * 60) % 360,
    }


def init_scene(screen_w, screen_h):
    return {
        "stars": [make_star(screen_w, screen_h) for _ in range(600)],
        "nebulas": [make_nebula(screen_w, screen_h, i) for i in range(12)],
        "shooters": [],
        "shooter_timer": 150,
        "tau_timer": 400,
        "tau_size": 0,
        "tau_active": False,
        "time": 0,
        "hue_base": 240.0,
        "beat": 0.0,
        "sub_beat": 0.0,
        "beat_timer": 0,
        "sub_timer": 0,
    }


def update_and_draw(scene, screen, pygame, sw, sh, is_playing, dt,
                    bass_level=0.0, mid_level=0.0, treble_level=0.0):
    s = scene
    s["time"] += 1
    s["beat_timer"] += 1
    s["sub_timer"] += 1
    s["shooter_timer"] -= 1

    BEAT = 52
    SUB = 26

    if bass_level > 0.01 or mid_level > 0.01:
        # Real audio — use it directly
        s["beat"] = min(1.0, bass_level * 2.0)
        s["sub_beat"] = min(1.0, mid_level * 1.5)
    else:
        # No audio data — organic breathing movement, no looping pulse
        breathe = (math.sin(s["time"] * 0.02) + 1) / 2      # slow 0-1
        breathe2 = (math.sin(s["time"] * 0.037 + 1.2) + 1) / 2
        if is_playing:
            s["beat"] = breathe * 0.4
            s["sub_beat"] = breathe2 * 0.3
        else:
            s["beat"] = max(0.0, s["beat"] - 0.01)
            s["sub_beat"] = max(0.0, s["sub_beat"] - 0.01)

    beat = s["beat"]
    sub = s["sub_beat"]

    s["beat"] = max(0.0, s["beat"] - 0.018)
    s["sub_beat"] = max(0.0, s["sub_beat"] - 0.03)
    s["hue_base"] = 220 + math.sin(s["time"] * 0.003) * 40

    beat = s["beat"]
    sub = s["sub_beat"]
    hue_base = s["hue_base"]
    t = s["time"]

    if s["shooter_timer"] <= 0:
        s["shooter_timer"] = 200 + int(random.random() * 200)
        s["shooters"].append(make_shooter(sw, hue_base))

    s["tau_timer"] -= 1
    if s["tau_timer"] <= 0 and not s["tau_active"]:
        s["tau_active"] = True
        s["tau_size"] = 0
        s["tau_timer"] = 900

    # Background
    screen.fill((0, 0, 10))

    def hsv_to_rgb(h, s_val, v):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h/360, s_val, v)
        return (int(r*255), int(g*255), int(b*255))

    # Nebulas
    for n in s["nebulas"]:
        n["x"] += n["vx"]
        n["y"] += n["vy"]
        if n["x"] < -n["r"]: n["x"] = sw + n["r"]
        if n["x"] > sw + n["r"]: n["x"] = -n["r"]
        if n["y"] < -n["r"]: n["y"] = sh + n["r"]
        if n["y"] > sh + n["r"]: n["y"] = -n["r"]

        pulse = 1 + beat * 0.6 + sub * 0.3
        hue = (hue_base + n["hue_offset"] + t * 0.04) % 360
        alpha = int(n["base_alpha"] * pulse * 255)
        r_size = int(n["r"] * pulse)

        surf = pygame.Surface((r_size * 2, r_size * 2), pygame.SRCALPHA)
        col = hsv_to_rgb(hue, 0.85, 0.6)
        for layer in range(4):
            layer_r = int(r_size * (1 - layer * 0.2))
            layer_a = max(0, alpha - layer * 15)
            pygame.draw.circle(surf, (*col, layer_a),
                             (r_size, r_size), layer_r)
        screen.blit(surf, (int(n["x"]) - r_size, int(n["y"]) - r_size))

    # Stars
    for star in s["stars"]:
        star["twinkle"] += star["twinkle_speed"]
        star["dance_angle"] += star["dance_speed"]

        dance_amp = star["dance_radius"] * (1 + beat * star["pulse_strength"] * 4 + sub * 2)
        star["x"] = star["base_x"] + math.cos(star["dance_angle"]) * dance_amp
        star["y"] = star["base_y"] + math.sin(star["dance_angle"] * 0.7) * dance_amp * 0.6

        twinkle_mod = 0.6 + 0.4 * math.sin(star["twinkle"])
        beat_mod = 1 + beat * star["pulse_strength"] * 1.5 + sub * 0.8
        alpha = min(1.0, star["base_alpha"] * twinkle_mod * beat_mod)
        size = star["size"] * (1 + beat * star["pulse_strength"] * 2)

        hue = (hue_base + star["hue_offset"] + t * 0.02) % 360
        sat = min(1.0, 0.5 + beat * 0.4)
        col = hsv_to_rgb(hue, sat, 0.9)

        sx = int(star["x"])
        sy = int(star["y"])

        if size > 1.5:
            glow_r = int(size * 3)
            if glow_r > 0:
                glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*col, int(alpha * 80)),
                                 (glow_r, glow_r), glow_r)
                screen.blit(glow, (sx - glow_r, sy - glow_r))

        if size >= 1:
            star_surf = pygame.Surface((int(size)*2+2, int(size)*2+2), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, (*col, int(alpha * 255)),
                             (int(size)+1, int(size)+1), max(1, int(size)))
            screen.blit(star_surf, (sx - int(size) - 1, sy - int(size) - 1))
        else:
            if 0 <= sx < sw and 0 <= sy < sh:
                screen.set_at((sx, sy), (*col, int(alpha * 255)))

    # Beat ring from center
    if beat > 0.5:
        ring_r = int((1 - beat) * 250)
        ring_alpha = int((beat - 0.5) * 80)
        col = hsv_to_rgb(hue_base, 0.8, 0.9)
        ring_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        if ring_r > 10:
            pygame.draw.circle(ring_surf, (*col, ring_alpha),
                             (sw//2, sh//2), ring_r, 3)
        screen.blit(ring_surf, (0, 0))

    # Tau Ceti
    if s["tau_active"]:
        s["tau_size"] += 0.25
        cx, cy = int(sw * 0.72), int(sh * 0.28)
        for i in range(5, -1, -1):
            gr = int(s["tau_size"] * (1 + i * 0.6))
            if gr < 1:
                continue
            glow = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
            a = max(0, int((0.12 - i*0.018) * 255))
            pygame.draw.circle(glow, (255, 220, 100, a), (gr, gr), gr)
            screen.blit(glow, (cx - gr, cy - gr))
        core = min(int(s["tau_size"] * 0.15), 6)
        if core >= 1:
            pygame.draw.circle(screen, (255, 248, 200), (cx, cy), core)
        if s["tau_size"] > 100:
            s["tau_active"] = False
            s["tau_size"] = 0

    # Shooting stars
    new_shooters = []
    for sh_star in s["shooters"]:
        sh_star["x"] += math.cos(sh_star["angle"]) * sh_star["speed"]
        sh_star["y"] += math.sin(sh_star["angle"]) * sh_star["speed"]
        sh_star["alpha"] -= 0.008
        if sh_star["alpha"] <= 0 or sh_star["x"] > sw + 50 or sh_star["y"] > sh + 50:
            continue
        tx = int(sh_star["x"] - math.cos(sh_star["angle"]) * sh_star["length"])
        ty = int(sh_star["y"] - math.sin(sh_star["angle"]) * sh_star["length"])
        col = hsv_to_rgb(sh_star["hue"], 0.5, 0.95)
        pygame.draw.line(screen, (*col, int(sh_star["alpha"] * 200)),
                        (tx, ty), (int(sh_star["x"]), int(sh_star["y"])), 1)
        new_shooters.append(sh_star)
    s["shooters"] = new_shooters

    # Song info bottom left
    return scene