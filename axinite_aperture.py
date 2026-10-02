"""Axinite Aperture — neon iris arcade for ElbowOS. Python 3 + pygame.

Open the iris to swallow apricot motes. Snap it shut to shatter crimson shards.
Arrows / A D change aperture. Space snaps shut. R restarts.
"""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get(
    "ELBOWOS_MP4", "/workspace/artifacts/AXINITE_APERTURE_ElbowOS.mp4"
)
CX, CY = W // 2, 980
INK = (18, 8, 14)
APRICOT = (255, 168, 72)
CREAM = (255, 236, 206)
CRIMSON = (255, 64, 92)
VIOLET = (168, 92, 186)
LENS = (120, 230, 255)
BLADE = (92, 42, 58)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY and not RECORD else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption("Axinite Aperture")
        self.font = pygame.font.SysFont("dejavusans", 64, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 36, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.combo = 0
        self.ap = 150.0
        self.target = 150.0
        self.motes = []
        self.sparks = []
        self.dust = [
            [random.randrange(W), random.randrange(H), random.uniform(0.4, 1.6)]
            for _ in range(70)
        ]
        self.banner = ""
        self.banner_t = 0
        self.spawn = 0

    def spawn_mote(self):
        ang = random.random() * math.tau
        dist = random.uniform(620, 780)
        kind = "shard" if random.random() < 0.38 else "gold"
        speed = random.uniform(3.4, 5.6) + self.t * 0.004
        self.motes.append(
            {
                "x": CX + math.cos(ang) * dist,
                "y": CY + math.sin(ang) * dist * 0.92,
                "vx": -math.cos(ang) * speed,
                "vy": -math.sin(ang) * speed * 0.92,
                "kind": kind,
                "r": 18 if kind == "gold" else 16,
            }
        )

    def burst(self, x, y, col, n=12):
        for _ in range(n):
            a = random.random() * math.tau
            s = random.uniform(1.5, 7)
            self.sparks.append(
                [x, y, math.cos(a) * s, math.sin(a) * s, col, random.randint(10, 22)]
            )

    def step(self, opening):
        self.t += 1
        self.target = max(70, min(290, self.target + opening))
        self.ap += (self.target - self.ap) * 0.22
        self.spawn -= 1
        if self.spawn <= 0:
            self.spawn_mote()
            self.spawn = max(8, 22 - self.t // 40)
        keep = []
        for m in self.motes:
            m["x"] += m["vx"]
            m["y"] += m["vy"]
            dx, dy = m["x"] - CX, m["y"] - CY
            d = math.hypot(dx, dy) + 0.01
            if d < self.ap - 6:
                if m["kind"] == "gold":
                    self.score += 100 + self.combo * 15
                    self.combo += 1
                    self.banner, self.banner_t = "SWALLOW", 18
                    self.burst(m["x"], m["y"], APRICOT, 16)
                else:
                    self.score = max(0, self.score - 80)
                    self.combo = 0
                    self.banner, self.banner_t = "SCORCH", 18
                    self.burst(m["x"], m["y"], CRIMSON, 18)
                continue
            if d < 310 and self.ap < d - 8 and m["kind"] == "shard":
                self.score += 40
                self.banner, self.banner_t = "SHATTER", 14
                self.burst(m["x"], m["y"], VIOLET, 14)
                continue
            if d < 40:
                self.combo = 0
                continue
            keep.append(m)
        self.motes = keep
        nxt = []
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[5] -= 1
            if s[5] > 0:
                nxt.append(s)
        self.sparks = nxt
        if self.banner_t:
            self.banner_t -= 1
        for d in self.dust:
            d[1] -= d[2]
            if d[1] < 0:
                d[1] = H
                d[0] = random.randrange(W)

    def auto(self):
        threat = None
        prize = None
        for m in self.motes:
            d = math.hypot(m["x"] - CX, m["y"] - CY)
            if m["kind"] == "shard" and d < 460 and (threat is None or d < threat):
                threat = d
            if m["kind"] == "gold" and d < 520 and (prize is None or d < prize):
                prize = d
        if threat is not None and threat < 360:
            return -28
        if prize is not None:
            return 18
        return -6

    def draw(self, surf):
        surf.fill(INK)
        for i, col in enumerate(((42, 16, 28), (28, 10, 22), (16, 6, 14))):
            pygame.draw.circle(surf, col, (CX, CY), 640 - i * 140)
        for d in self.dust:
            pygame.draw.circle(surf, (90, 50, 60), (int(d[0]), int(d[1])), 2)
        pygame.draw.circle(surf, (8, 18, 28), (CX, CY), int(self.ap - 4))
        pygame.draw.circle(surf, LENS, (CX, CY), max(8, int(self.ap * 0.45)), 3)
        blades = 12
        for i in range(blades):
            a0 = self.t * 0.01 + i * math.tau / blades
            a1 = a0 + math.tau / blades * 0.86
            outer = 340
            inner = self.ap
            pts = [
                (CX + math.cos(a0) * inner, CY + math.sin(a0) * inner),
                (CX + math.cos(a0 + 0.08) * outer, CY + math.sin(a0 + 0.08) * outer),
                (CX + math.cos(a1) * outer, CY + math.sin(a1) * outer),
                (CX + math.cos(a1 - 0.04) * inner, CY + math.sin(a1 - 0.04) * inner),
            ]
            shade = (110 + (i % 3) * 18, 48 + (i % 2) * 20, 62)
            pygame.draw.polygon(surf, shade, pts)
            pygame.draw.polygon(surf, APRICOT, pts, 2)
        pygame.draw.circle(surf, CREAM, (CX, CY), 338, 3)
        for m in self.motes:
            col = APRICOT if m["kind"] == "gold" else CRIMSON
            pygame.draw.circle(surf, col, (int(m["x"]), int(m["y"])), m["r"] + 6)
            pygame.draw.circle(surf, CREAM, (int(m["x"]), int(m["y"])), m["r"])
        for s in self.sparks:
            pygame.draw.circle(surf, s[4], (int(s[0]), int(s[1])), max(1, s[5] // 5))
        title = self.font.render("AXINITE APERTURE", True, APRICOT)
        surf.blit(title, title.get_rect(center=(CX, 120)))
        sub = self.small.render("open for gold  ·  shut on shards", True, CREAM)
        surf.blit(sub, sub.get_rect(center=(CX, 180)))
        score = self.mid.render(f"SCORE  {self.score}", True, LENS)
        surf.blit(score, score.get_rect(center=(CX, 250)))
        combo = self.small.render(f"COMBO  x{self.combo}", True, VIOLET)
        surf.blit(combo, combo.get_rect(center=(CX, 300)))
        if self.banner_t:
            b = self.font.render(self.banner, True, CREAM)
            surf.blit(b, b.get_rect(center=(CX, CY - 420)))
        tag = self.mid.render("x.com/ElbowOS", True, APRICOT)
        surf.blit(tag, tag.get_rect(center=(CX, H - 90)))

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-preset", "veryfast", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for i in range(frames):
                self.step(self.auto())
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)

    def play(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            opening = 0
            keys = pygame.key.get_pressed()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_UP]:
                opening = 10
            if keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_DOWN]:
                opening = -10
            if keys[pygame.K_SPACE]:
                opening = -22
            self.step(opening)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play()
    else:
        g.record()
        pygame.quit()


if __name__ == "__main__":
    main()
