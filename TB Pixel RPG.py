import pygame
import random
import math

# --- Configuration & Setup ---
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Turn Based RPG - Healed & Looted")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("monospace", 15)
font_med = pygame.font.SysFont("monospace", 25)
font_large = pygame.font.SysFont("monospace", 50)

# Colors
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (50, 50, 50)
RED, GREEN, BLUE = (200, 0, 0), (0, 200, 0), (0, 0, 200)
GOLD, PURPLE = (218, 165, 32), (150, 0, 255)


# --- Classes ---

class Entity:
    def __init__(self, name, hp, atk, def_stat, spd, color):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = def_stat
        self.speed = spd
        self.base_speed = spd
        self.color = color
        self.cooldown = 0
        self.speed_debuff_timer = 0
        self.burn_timer = 0
        self.is_alive = True

    def take_damage(self, dmg):
        actual_dmg = max(5, int(dmg - (self.defense * 0.15)))
        self.hp -= actual_dmg
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return actual_dmg


class Player(Entity):
    def __init__(self, p_class):
        if p_class == "Warrior":
            super().__init__("Warrior", 150, 50, 20, 10, BLUE)
            self.skill_name = "Stomp"
        elif p_class == "Assassin":
            super().__init__("Assassin", 100, 80, 15, 15, GRAY)
            self.skill_name = "Flash Step"
        elif p_class == "Mage":
            super().__init__("Mage", 80, 75, 10, 12, PURPLE)
            self.skill_name = "Fireball"
        self.p_class = p_class
        self.last_loot = ""


class BattleManager:
    def __init__(self, player, stage_num):
        self.player = player
        # --- THE FIX: FULL HEAL ---
        self.player.hp = self.player.max_hp
        self.player.is_alive = True
        self.player.cooldown = 0
        self.player.speed = self.player.base_speed

        hp_list = [100, 200, 300, 1000]
        enemy_hp = hp_list[stage_num - 1]
        enemy_name = "BOSS" if stage_num == 4 else f"Enemy St.{stage_num}"
        self.enemy = Entity(enemy_name, enemy_hp, 20 + (stage_num * 8), 10 + stage_num, 8 + stage_num, GREEN)

        self.turn = "Player" if self.player.speed >= self.enemy.speed else "Enemy"
        self.log = f"Battle Start! Full Heal Applied."
        self.battle_over = False

    def player_attack(self):
        dmg = self.enemy.take_damage(self.player.atk)
        self.log = f"You hit for {dmg}!"
        self.end_turn()

    def player_skill(self):
        if self.player.cooldown > 0:
            self.log = f"Skill on CD: {self.player.cooldown}"
            return
        if self.player.p_class == "Warrior":
            dmg = self.enemy.take_damage(self.player.atk * 1.2)
        elif self.player.p_class == "Assassin":
            dmg = self.enemy.take_damage(self.player.atk * 1.5)
            self.player.speed *= 0.7
            self.player.speed_debuff_timer = 2
        elif self.player.p_class == "Mage":
            dmg = self.enemy.take_damage(self.player.atk * 1.3)
            self.enemy.burn_timer = 3
        self.player.cooldown = 3
        self.log = f"Skill Used! {int(dmg)} DMG!"
        self.end_turn()

    def enemy_turn(self):
        if not self.enemy.is_alive: return
        dmg = self.player.take_damage(self.enemy.atk)
        self.log = f"Enemy deals {dmg} damage!"
        self.end_turn()

    def end_turn(self):
        if self.turn == "Enemy":
            if self.enemy.burn_timer > 0:
                self.enemy.hp -= (self.enemy.max_hp * 0.01)
                self.enemy.burn_timer -= 1
            if self.player.cooldown > 0: self.player.cooldown -= 1
            if self.player.speed_debuff_timer > 0:
                self.player.speed_debuff_timer -= 1
                if self.player.speed_debuff_timer == 0: self.player.speed = self.player.base_speed
            self.turn = "Player"
        else:
            self.turn = "Enemy"

    def roll_loot(self):
        if random.random() < 0.20:
            rarities = ["Common", "Rare", "Epic", "Legendary", "Mythical", "Secret"]
            weights = [50, 25, 15, 7, 2.5, 0.5]  # Expert tip: weighted luck!
            rarity = random.choices(rarities, weights=weights)[0]
            item_type = random.choice(["Artifact", "Armor"])
            self.player.last_loot = f"NEW: {rarity} {item_type}!"
        else:
            self.player.last_loot = "No drops this time."


# --- Main Game Loop ---
def main():
    state = 0  # MENU
    selected_class = "Warrior"
    player, battle = None, None
    running = True

    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == 0 and event.key == pygame.K_SPACE:
                    player = Player(selected_class)
                    state = 1  # STAGE SELECT
                elif state == 2 and battle.turn == "Player" and not battle.battle_over:
                    if event.key == pygame.K_q: battle.player_attack()
                    if event.key == pygame.K_e: battle.player_skill()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == 0:
                    for i, c in enumerate(["Warrior", "Assassin", "Mage"]):
                        if pygame.Rect(WIDTH // 2 - 100, 235 + i * 50, 200, 40).collidepoint(mouse_pos):
                            selected_class = c
                elif state == 1:
                    for i in range(1, 5):
                        if pygame.Rect(WIDTH // 2 - 100, 150 + i * 60, 200, 40).collidepoint(mouse_pos):
                            battle = BattleManager(player, i)
                            state = 2  # BATTLE
                elif state == 2 and battle.battle_over:
                    if battle.player.is_alive:
                        battle.roll_loot()
                        state = 1
                    else:
                        state = 0

        # --- Draw Logic ---
        if state == 0:
            screen.blit(font_large.render("PIXEL RPG", True, WHITE), (WIDTH // 2 - 130, 100))
            for i, c in enumerate(["Warrior", "Assassin", "Mage"]):
                color = GOLD if selected_class == c else WHITE
                txt = font_med.render(c, True, color)
                screen.blit(txt, txt.get_rect(center=(WIDTH // 2, 250 + i * 50)))
            screen.blit(font_small.render("SPACE TO START", True, GREEN), (WIDTH // 2 - 60, 450))

        elif state == 1:
            screen.blit(font_med.render(f"{player.p_class} - SELECT STAGE", True, WHITE), (WIDTH // 2 - 150, 50))
            if player.last_loot:
                screen.blit(font_small.render(player.last_loot, True, GOLD), (WIDTH // 2 - 100, 100))
            for i in range(1, 5):
                name = f"Stage {i}" if i < 4 else "BOSS"
                btn = pygame.Rect(WIDTH // 2 - 100, 150 + i * 60, 200, 40)
                pygame.draw.rect(screen, GRAY, btn)
                screen.blit(font_small.render(name, True, WHITE), (btn.x + 60, btn.y + 12))

        elif state == 2:
            pygame.draw.rect(screen, battle.player.color, (150, 250, 100, 100))
            pygame.draw.rect(screen, battle.enemy.color, (650, 250, 100, 100))

            # Bars
            pygame.draw.rect(screen, RED, (150, 230, 100, 10))
            pygame.draw.rect(screen, GREEN, (150, 230, (battle.player.hp / battle.player.max_hp) * 100, 10))
            pygame.draw.rect(screen, RED, (650, 230, 100, 10))
            pygame.draw.rect(screen, GREEN, (650, 230, (battle.enemy.hp / battle.enemy.max_hp) * 100, 10))

            def draw_stats(ent, x, y):
                lines = [f"{ent.name}", f"HP:{int(ent.hp)}", f"ATK:{ent.atk}", f"DEF:{ent.defense}",
                         f"SPD:{int(ent.speed)}"]
                for i, l in enumerate(lines):
                    screen.blit(font_small.render(l, True, WHITE), (x, y + i * 20))

            draw_stats(battle.player, 20, 250)
            draw_stats(battle.enemy, 770, 250)
            screen.blit(font_med.render(battle.log, True, WHITE), (WIDTH // 2 - 150, 450))

            if not battle.battle_over:
                if battle.turn == "Player":
                    screen.blit(font_small.render("[Q] ATTACK  [E] SKILL", True, GOLD), (WIDTH // 2 - 100, 500))
                else:
                    pygame.display.flip()
                    pygame.time.delay(800)
                    battle.enemy_turn()
                if not battle.player.is_alive or not battle.enemy.is_alive:
                    battle.battle_over = True
            else:
                msg = "VICTORY! CLICK." if battle.player.is_alive else "DEFEAT. CLICK."
                screen.blit(font_med.render(msg, True, GOLD), (WIDTH // 2 - 120, 200))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()