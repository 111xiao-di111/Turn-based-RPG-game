import pygame
import random

# --- Configuration & Setup ---
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel RPG V1.1.8 - The Full Fix")
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
        self.x = pos_x
        self.y = 250
        self.size = 100
        self.cooldown = 0
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
        if p_class == "Warrior": super().__init__("Warrior", 150, 50, 20, 10, BLUE, 150)
        elif p_class == "Assassin": super().__init__("Assassin", 100, 80, 15, 15, GRAY, 150)
        elif p_class == "Mage": super().__init__("Mage", 80, 75, 10, 12, PURPLE, 150)
        self.p_class = p_class
        self.gold = 0
        self.armor_tier = "None"
        self.last_loot = ""

class BattleManager:
    def __init__(self, player, stage_num):
        self.player = player
        self.stage_num = stage_num
        self.player.hp = self.player.max_hp
        self.player.is_alive = True
        self.player.cooldown = 0
        
        hp_list = [100, 250, 500, 1200]
        self.enemy = Entity("BOSS" if stage_num==4 else f"Enemy St.{stage_num}", hp_list[stage_num-1], 20+(stage_num*10), 10+(stage_num*5), 8+stage_num, GREEN, 650)
        
        self.turn = "Player" if self.player.speed >= self.enemy.speed else "Enemy"
        self.log = "Battle Start!"
        self.battle_over = False
        self.vfx_timer = 0
        self.vfx_pos = (0, 0)
        self.turn_wait_timer = 0 

    def trigger_action(self, type="attack"):
        self.vfx_timer = 12
        if self.turn == "Player":
            self.vfx_pos = (self.enemy.x, self.enemy.y + 50)
            if type == "attack":
                dmg = self.enemy.take_damage(self.player.atk)
                self.log = f"Critical! {dmg} DMG"
            else:
                mult = 1.5 if self.player.p_class == "Warrior" else (2.0 if self.player.p_class == "Assassin" else 1.4)
                dmg = self.enemy.take_damage(self.player.atk * mult)
                if self.player.p_class == "Mage": self.enemy.burn_timer = 3
                self.player.cooldown = 3
                self.log = f"SKILL HIT! {int(dmg)} DMG"
        else:
            self.vfx_pos = (self.player.x + 100, self.player.y + 50)
            dmg = self.player.take_damage(self.enemy.atk)
            self.log = f"Enemy strikes for {dmg}!"
        
        self.end_turn()

    def end_turn(self):
        if not self.player.is_alive or not self.enemy.is_alive:
            self.battle_over = True; return
        if self.turn == "Enemy":
            if self.enemy.burn_timer > 0: self.enemy.hp -= 10; self.enemy.burn_timer -= 1
            if self.player.cooldown > 0: self.player.cooldown -= 1
            self.turn = "Player"
        else:
            self.turn = "Enemy"; self.turn_wait_timer = 90

# --- Main Game Loop ---
def main():
    state, selected_class = 0, "Warrior"
    player, battle, shop_items = None, None, []
    running = True

    def get_shop():
        items = []
        rarity_names = ["C", "R", "E", "L", "M", "???"]
        for _ in range(3):
            idx = random.choices(range(6), weights=[50, 25, 15, 7, 2.5, 0.5])[0]
            items.append({'rarity': rarity_names[idx], 'price': round(40 * (2.2 ** idx)), 'stat': 25 + (idx * 35)})
        return items

    def draw_stats(ent, x, y):
        stats = [f"{ent.name}", f"HP:{int(ent.hp)}/{ent.max_hp}", f"ATK:{int(ent.atk)}", f"DEF:{int(ent.defense)}", f"SPD:{int(ent.speed)}"]
        for i, s in enumerate(stats):
            screen.blit(font_small.render(s, True, WHITE if i==0 else GOLD), (x, y + i * 20))

    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if state == 0 and event.key == pygame.K_SPACE: player = Player(selected_class); state = 1
                elif state == 1 and event.key == pygame.K_s: shop_items = get_shop(); state = 3
                elif state == 3 and event.key == pygame.K_ESCAPE: state = 1
                elif state == 2 and battle.turn == "Player" and not battle.battle_over and battle.vfx_timer <= 0:
                    if event.key == pygame.K_q: battle.trigger_action("attack")
                    if event.key == pygame.K_e and player.cooldown <= 0: battle.trigger_action("skill")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == 0:
                    for i, c in enumerate(["Warrior", "Assassin", "Mage"]):
                        if pygame.Rect(WIDTH//2-100, 235+i*50, 200, 40).collidepoint(mouse_pos): selected_class = c
                elif state == 1:
                    for i in range(1, 5):
                        if pygame.Rect(WIDTH//2-100, 150+i*60, 200, 40).collidepoint(mouse_pos):
                            battle = BattleManager(player, i); state = 2
                elif state == 3:
                    for i, item in enumerate(shop_items):
                        if pygame.Rect(100+i*250, 200, 200, 180).collidepoint(mouse_pos):
                            if player.gold >= item['price']:
                                player.gold -= item['price']; player.max_hp += item['stat']
                                player.atk += item['stat']; player.defense += item['stat']
                                player.armor_tier = item['rarity']; shop_items.pop(i); break
                elif state == 2 and battle.battle_over:
                    if battle.player.is_alive:
                        g = random.randint(10, 20) * battle.stage_num
                        player.gold += g; player.last_loot = f"WIN! +{g}G"; state = 1
                    else: state = 0

        if state == 2:
            if battle.turn == "Enemy" and not battle.battle_over and battle.vfx_timer <= 0:
                if battle.turn_wait_timer > 0: battle.turn_wait_timer -= 1
                else: battle.trigger_action()

            # Drawing
            pygame.draw.rect(screen, battle.player.color, (battle.player.x, 250, 100, 100))
            pygame.draw.rect(screen, battle.enemy.color, (battle.enemy.x, 250, 100, 100))
            if battle.vfx_timer > 0:
                pygame.draw.circle(screen, WHITE, battle.vfx_pos, (13 - battle.vfx_timer) * 8, 2)
                battle.vfx_timer -= 1

            # Stats & HP
            draw_stats(battle.player, 20, 250)
            draw_stats(battle.enemy, 770, 250)
            pygame.draw.rect(screen, RED, (150, 230, 100, 8))
            pygame.draw.rect(screen, GREEN, (150, 230, (battle.player.hp/battle.player.max_hp)*100, 8))
            pygame.draw.rect(screen, RED, (650, 230, 100, 8))
            pygame.draw.rect(screen, GREEN, (650, 230, (battle.enemy.hp/battle.enemy.max_hp)*100, 8))
            
            screen.blit(font_med.render(battle.log, True, WHITE), (WIDTH//2-150, 450))
            
            # --- THE TUTORIAL / CONTROLS ---
            if not battle.battle_over and battle.turn == "Player" and battle.vfx_timer <= 0:
                screen.blit(font_small.render("[Q] ATTACK  [E] SKILL", True, GOLD), (WIDTH//2-100, 500))
            elif battle.battle_over:
                screen.blit(font_med.render("CLICK TO CONTINUE", True, GOLD), (WIDTH//2-130, 200))

        elif state == 0:
            screen.blit(font_large.render("PIXEL RPG", True, WHITE), (WIDTH//2-120, 100))
            for i, c in enumerate(["Warrior", "Assassin", "Mage"]):
                color = GOLD if selected_class == c else WHITE
                screen.blit(font_med.render(c, True, color), (WIDTH//2-50, 250+i*50))
            screen.blit(font_small.render("SPACE TO START", True, GREEN), (WIDTH//2-60, 450))

        elif state == 1:
            screen.blit(font_med.render(f"GOLD: {player.gold} | {player.armor_tier} ARMOR", True, GOLD), (20, 20))
            for i in range(1, 5):
                pygame.draw.rect(screen, GRAY, (WIDTH//2-100, 150+i*60, 200, 40))
                screen.blit(font_small.render(f"Stage {i}", True, WHITE), (WIDTH//2-40, 162+i*60))
            screen.blit(font_small.render("[S] SHOP", True, PURPLE), (WIDTH-100, 20))
            if player.last_loot: screen.blit(font_small.render(player.last_loot, True, GOLD), (WIDTH//2-80, 100))

        elif state == 3:
            screen.blit(font_large.render("SHOP", True, GOLD), (WIDTH//2-50, 50))
            for i, item in enumerate(shop_items):
                rect = pygame.Rect(100+i*250, 200, 200, 180); pygame.draw.rect(screen, GRAY, rect)
                screen.blit(font_small.render(f"[{item['rarity']}] Armor", True, WHITE), (rect.x+10, rect.y+20))
                screen.blit(font_small.render(f"+{item['stat']} All", True, GREEN), (rect.x+10, rect.y+60))
                screen.blit(font_small.render(f"{item['price']}G", True, GOLD), (rect.x+10, rect.y+140))
            screen.blit(font_small.render("[ESC] EXIT", True, WHITE), (20, 20))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__": main()
