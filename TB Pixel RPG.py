import pygame
import random
import math

# --- Configuration & Setup ---
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel RPG V1.1 by xiao")
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
    def __init__(self, name, hp, atk, def_stat, spd, color, pos_x):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = def_stat
        self.speed = spd
        self.base_speed = spd
        self.color = color
        # Animation positioning
        self.base_x = pos_x
        self.render_x = pos_x
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
            super().__init__("Warrior", 150, 50, 20, 10, BLUE, 150)
            self.skill_name = "Stomp"
        elif p_class == "Assassin":
            super().__init__("Assassin", 100, 80, 15, 15, GRAY, 150)
            self.skill_name = "Flash Step"
        elif p_class == "Mage":
            super().__init__("Mage", 80, 75, 10, 12, PURPLE, 150)
            self.skill_name = "Fireball"
        self.p_class = p_class
        self.last_loot = ""
        self.gold = 0
        self.armor_tier = "None"


class BattleManager:
    def __init__(self, player, stage_num):
        self.player = player
        self.stage_num = stage_num
        self.player.hp = self.player.max_hp
        self.player.is_alive = True
        self.player.cooldown = 0
        self.player.speed = self.player.base_speed

        # Reset positions for new battle
        self.player.base_x = 150
        self.player.render_x = 150

        hp_list = [100, 200, 300, 1000]
        enemy_hp = hp_list[stage_num - 1]
        enemy_name = "BOSS" if stage_num == 4 else f"Enemy St.{stage_num}"
        self.enemy = Entity(enemy_name, enemy_hp, 20 + (stage_num * 8), 10 + stage_num, 8 + stage_num, GREEN, 650)

        self.turn = "Player" if self.player.speed >= self.enemy.speed else "Enemy"
        self.log = f"Battle Start! Heal Applied."
        self.battle_over = False

        # Animation State
        self.animating = False
        self.anim_timer = 0
        self.vfx_timer = 0
        self.vfx_pos = (0, 0)
        self.move_type = ""

    def player_attack(self):
        dmg = self.enemy.take_damage(self.player.atk)
        self.log = f"You hit for {dmg}!"
        self.end_turn()

    def player_skill(self):
        if self.player.cooldown > 0:
            self.log = f"Skill on CD: {self.player.cooldown}"
            return

        if random.random() < 0.30:
            self.log = "SKILL FAILED!"
        else:
            if self.player.p_class == "Warrior":
                dmg = self.enemy.take_damage(self.player.atk * 1.2)
            elif self.player.p_class == "Assassin":
                dmg = self.enemy.take_damage(self.player.atk * 1.5)
                self.player.speed *= 0.7
                self.player.speed_debuff_timer = 2
            elif self.player.p_class == "Mage":
                dmg = self.enemy.take_damage(self.player.atk * 1.3)
                self.enemy.burn_timer = 3
            self.log = f"Skill Success! {int(dmg)} DMG!"

        self.player.cooldown = 3
        self.end_turn()

    def enemy_turn(self):
        if not self.enemy.is_alive: return
        dmg = self.player.take_damage(self.enemy.atk)
        self.log = f"Enemy deals {dmg} damage!"
        self.end_turn()

    def end_turn(self):
        # Only switch turns if everyone is still alive
        if not self.player.is_alive or not self.enemy.is_alive:
            self.battle_over = True
            return

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
        r = random.random()
        g = 0
        if self.stage_num == 1:
            g = 3 if r < 0.7 else (4 if r < 0.9 else 5)
        elif self.stage_num == 2:
            if r < 0.6:
                g = 6
            elif r < 0.9:
                g = 7
            elif r < 0.95:
                g = 8
            elif r < 0.99:
                g = 9
            else:
                g = 10
        elif self.stage_num == 3:
            if r < 0.8:
                g = random.randint(20, 30)
            elif r < 0.95:
                g = random.randint(31, 40)
            elif r < 0.999:
                g = random.randint(40, 45)
            else:
                g = random.randint(45, 50)
        elif self.stage_num == 4:
            if r < 0.9:
                g = random.randint(100, 200)
            elif r < 0.98:
                g = random.randint(200, 300)
            elif r < 0.99:
                g = random.randint(300, 400)
            elif r < 0.9999:
                g = random.randint(400, 499)
            else:
                g = 500

        self.player.gold += g
        if random.random() < 0.20:
            rarities = ["C", "R", "E", "L", "M", "???"]
            weights = [50, 25, 15, 7, 2.5, 0.5]
            rarity = random.choices(rarities, weights=weights)[0]
            item_type = random.choice(["Artifact", "Armor"])
            self.player.last_loot = f"NEW: {rarity} {item_type} + {g}G!"
        else:
            self.player.last_loot = f"Gained {g} Gold."


# --- Main Game Loop ---
def main():
    state = 0  # 0:Menu, 1:Stages, 2:Battle, 3:Shop
    selected_class = "Warrior"
    player, battle = None, None
    shop_items = []
    running = True

    def get_shop():
        items = []
        rarity_names = ["C", "R", "E", "L", "M", "???"]
        for _ in range(3):
            idx = random.choices(range(6), weights=[50, 25, 15, 7, 2.5, 0.5])[0]
            price = round(50 * (2.5 ** idx))
            stat = 30 + (idx * 40)
            items.append({'rarity': rarity_names[idx], 'price': price, 'stat': stat})
        return items

    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT: running = False

            if event.type == pygame.KEYDOWN:
                if state == 0 and event.key == pygame.K_SPACE:
                    player = Player(selected_class);
                    state = 1
                elif state == 1 and event.key == pygame.K_s:
                    shop_items = get_shop();
                    state = 3
                elif state == 3:
                    if event.key == pygame.K_ESCAPE: state = 1
                    if event.key == pygame.K_r and player.gold >= 20:
                        player.gold -= 20;
                        shop_items = get_shop()
                elif state == 2 and battle.turn == "Player" and not battle.battle_over and not battle.animating:
                    if event.key == pygame.K_q:
                        battle.animating = True;
                        battle.anim_timer = 0;
                        battle.move_type = "attack"
                    if event.key == pygame.K_e:
                        battle.animating = True;
                        battle.anim_timer = 0;
                        battle.move_type = "skill"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == 0:
                    for i, c in enumerate(["Warrior", "Assassin", "Mage"]):
                        if pygame.Rect(WIDTH // 2 - 100, 235 + i * 50, 200, 40).collidepoint(mouse_pos):
                            selected_class = c
                elif state == 1:
                    for i in range(1, 5):
                        if pygame.Rect(WIDTH // 2 - 100, 150 + i * 60, 200, 40).collidepoint(mouse_pos):
                            battle = BattleManager(player, i);
                            state = 2
                elif state == 3:
                    for i, item in enumerate(shop_items):
                        if pygame.Rect(100 + i * 250, 200, 200, 180).collidepoint(mouse_pos):
                            if player.gold >= item['price']:
                                player.gold -= item['price'];
                                b = item['stat']
                                player.max_hp += b;
                                player.atk += b;
                                player.defense += b
                                player.armor_tier = item['rarity'];
                                shop_items.pop(i);
                                break
                elif state == 2 and battle.battle_over:
                    if battle.player.is_alive:
                        battle.roll_loot(); state = 1
                    else:
                        state = 0

        # --- Draw Logic ---
        if state == 0:
            screen.blit(font_large.render("PIXEL RPG V1.1", True, WHITE), (WIDTH // 2 - 180, 100))
            for i, c in enumerate(["Warrior", "Assassin", "Mage"]):
                color = GOLD if selected_class == c else WHITE
                txt = font_med.render(c, True, color)
                screen.blit(txt, txt.get_rect(center=(WIDTH // 2, 250 + i * 50)))
            screen.blit(font_small.render("SPACE TO START", True, GREEN), (WIDTH // 2 - 60, 450))

        elif state == 1:
            screen.blit(font_med.render(f"GOLD: {player.gold} | ARMOR: {player.armor_tier}", True, GOLD), (20, 20))
            screen.blit(font_small.render("[S] SHOP", True, PURPLE), (WIDTH - 100, 20))
            if player.last_loot: screen.blit(font_small.render(player.last_loot, True, GOLD), (WIDTH // 2 - 120, 100))
            for i in range(1, 5):
                name = f"Stage {i}" if i < 4 else "BOSS"
                btn = pygame.Rect(WIDTH // 2 - 100, 150 + i * 60, 200, 40)
                pygame.draw.rect(screen, GRAY, btn)
                screen.blit(font_small.render(name, True, WHITE), (btn.x + 60, btn.y + 12))

        elif state == 3:
            screen.blit(font_large.render("SHOP", True, GOLD), (WIDTH // 2 - 50, 50))
            screen.blit(font_small.render(f"GOLD: {player.gold} | [R] REFRESH (20G) | [ESC] EXIT", True, WHITE),
                        (220, 120))
            for i, item in enumerate(shop_items):
                rect = pygame.Rect(100 + i * 250, 200, 200, 180);
                pygame.draw.rect(screen, GRAY, rect)
                screen.blit(font_med.render(f"[{item['rarity']}] Armor", True, WHITE), (rect.x + 10, rect.y + 20))
                screen.blit(font_small.render(f"+{item['stat']} All Stats", True, GREEN), (rect.x + 10, rect.y + 60))
                screen.blit(font_med.render(f"{item['price']}G", True, GOLD), (rect.x + 10, rect.y + 140))

        elif state == 2:
            # Animation Engine Fixes
            if battle.animating:
                battle.anim_timer += 0.05
                attacker = battle.player if battle.turn == "Player" else battle.enemy
                target = battle.enemy if battle.turn == "Player" else battle.player

                # COLLISION OFFSET: Stop slightly before the center of the other square
                collision_target_x = target.base_x - 80 if battle.turn == "Player" else target.base_x + 80

                if battle.anim_timer <= 0.5:  # Forward
                    attacker.render_x = attacker.base_x + (collision_target_x - attacker.base_x) * (
                                battle.anim_timer * 2)
                elif battle.anim_timer <= 1.0:  # Back
                    if battle.vfx_timer == 0:
                        # VFX POSITION FIX: Centered on the point of collision
                        battle.vfx_pos = (
                            collision_target_x + 50 if battle.turn == "Player" else collision_target_x + 50, 300)
                        if battle.turn == "Player":
                            if battle.move_type == "attack":
                                battle.player_attack()
                            else:
                                battle.player_skill()
                        else:
                            battle.enemy_turn()
                        battle.vfx_timer = 12
                    attacker.render_x = collision_target_x + (attacker.base_x - collision_target_x) * (
                                (battle.anim_timer - 0.5) * 2)
                else:  # Reset
                    battle.animating = False
                    attacker.render_x = attacker.base_x  # SNAP BACK TO ORIGINAL POSITION

            if not battle.animating and battle.turn == "Enemy" and not battle.battle_over:
                pygame.time.delay(500)
                if battle.enemy.is_alive:  # DEAD LOOP FIX
                    battle.animating = True;
                    battle.anim_timer = 0;
                    battle.move_type = "attack"

            # Draw squares at render_x
            pygame.draw.rect(screen, battle.player.color, (battle.player.render_x, 250, 100, 100))
            pygame.draw.rect(screen, battle.enemy.color, (battle.enemy.render_x, 250, 100, 100))

            if battle.vfx_timer > 0:  # VFX at collision point
                pygame.draw.circle(screen, WHITE, battle.vfx_pos, (13 - battle.vfx_timer) * 8, 2)
                battle.vfx_timer -= 1

            pygame.draw.rect(screen, RED, (150, 230, 100, 10))
            pygame.draw.rect(screen, GREEN, (150, 230, (battle.player.hp / battle.player.max_hp) * 100, 10))
            pygame.draw.rect(screen, RED, (650, 230, 100, 10))
            pygame.draw.rect(screen, GREEN, (650, 230, (battle.enemy.hp / battle.enemy.max_hp) * 100, 10))

            def draw_stats(ent, x, y):
                lines = [f"{ent.name}", f"HP:{int(ent.hp)}", f"ATK:{ent.atk}", f"DEF:{ent.defense}",
                         f"SPD:{int(ent.speed)}"]
                for i, l in enumerate(lines): screen.blit(font_small.render(l, True, WHITE), (x, y + i * 20))

            draw_stats(battle.player, 20, 250);
            draw_stats(battle.enemy, 770, 250)
            screen.blit(font_med.render(battle.log, True, WHITE), (WIDTH // 2 - 150, 450))
            if not battle.battle_over:
                if battle.turn == "Player" and not battle.animating:
                    screen.blit(font_small.render("[Q] ATTACK  [E] SKILL", True, GOLD), (WIDTH // 2 - 100, 500))
            else:
                msg = "VICTORY! CLICK." if battle.player.is_alive else "DEFEAT. CLICK."
                screen.blit(font_med.render(msg, True, GOLD), (WIDTH // 2 - 120, 200))

        pygame.display.flip();
        clock.tick(60)


if __name__ == "__main__":
    main()
