import pygame as pg
import sys, time
from brd import Bird
import emoji
from pipe import Pipe
pg.init()

class Game:
    def __init__(self):
        # setting up the display config
        self.width = 600
        self.height = 768
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width, self.height))
        self.clock = pg.time.Clock()
        self.move_speed = 150 
        self.start_monitoring = False
        self.score = 0
        self.font = pg.font.Font("assets/font.ttf", 24)
        self.score_text = self.font.render("score: 0 ", True, (0, 0, 0))
        self.score_text_rect = self.score_text.get_rect(center=(100, 30))
        self.bird = Bird(self.scale_factor)

        # High Score setup
        self.high_score = self.load_high_score()

        # adding sound
        self.is_enter_pressed = False
        self.flap_sound = pg.mixer.Sound("assets/sfx/flap.wav")
        self.score_sound = pg.mixer.Sound("assets/sfx/score.wav")
        self.collision_sound = pg.mixer.Sound("assets/sfx/dead.wav")
        self.pipes = []
        self.pipe_generate_counter = 71

        self.setupBgAndGround()

        self.gameloop()

    def gameloop(self):
       last_time = time.time()
       while True:
            # calculating delta time
            new_time = time.time()
            dt = new_time - last_time
            last_time = new_time
            for event in pg.event.get():
               if event.type == pg.QUIT:
                   pg.quit()
                   sys.exit()
               if event.type == pg.KEYDOWN:
                   if event.key == pg.K_RETURN:
                        self.is_enter_pressed = True
                        self.bird.update_on = True
                   if event.key == pg.K_SPACE and self.is_enter_pressed:
                        self.bird.flap(dt)
                        self.flap_sound.play()  # sound for bird

            if self.is_game_over():
                self.game_over_screen()

            self.updateEverything(dt)
            self.checkCollisions()
            self.checkScore()
            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)


    def is_game_over(self):
        # checck for the game condition
        return self.bird.rect.bottom > 568 or \
                (len(self.pipes) > 0 and (self.bird.rect.colliderect(self.pipes[0].rect_down) or
                                          self.bird.rect.colliderect(self.pipes[0].rect_up)))
    
    def game_over_screen(self):
        # displaying the game over msg and restart option
        game_over_text = self.font.render("GAME OVER",True,(255,0,0))
        restart_text = self.font.render("PRESS ENTER TO RESTART", True, (139,0,139))

        sad_emoji_img = pg.image.load("assets/confused.png").convert_alpha()
        sad_emoji_img = pg.transform.scale(sad_emoji_img, (50, 50))  # scale to fit your needs

        

        # position the text
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        sad_emoji_rect = sad_emoji_img.get_rect(center=(self.width // 2, self.height // 2))  # place it near game over text


        self.win.fill((255,255,255))
        self.win.blit(game_over_text, game_over_rect)
        self.win.blit(restart_text, restart_rect)
        self.win.blit(sad_emoji_img, sad_emoji_rect)

        pg.display.update()


        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key ==pg.K_RETURN: #  restart the game
                        self.reset_game()
                        return
                    elif event.key == pg.K_ESCAPE: # to quit the game
                        sys.exit()

    def reset_game(self):
        # reset the game
        self.score = 0
        self.score_text = self.font.render(f"score: {self.score}", True, (0,0,0))
        self.bird = Bird(self.scale_factor)
        self.pipes.clear()
        self.start_monitoring = False
        self.is_enter_pressed = False
        self.pipe_generate_counter = 71
        self.setupBgAndGround()  # reset the bg and ground positions



            # updating score

    def checkScore(self):
       if len(self.pipes) > 0:
           if (self.bird.rect.left > self.pipes[0].rect_down.left and
               self.bird.rect.right < self.pipes[0].rect_down.right and not self.start_monitoring):
               self.start_monitoring = True
           if self.bird.rect.left > self.pipes[0].rect_down.right and self.start_monitoring:
               self.start_monitoring = False
               self.score +=1
               self.score_sound.play()  # sound for score
               self.score_text = self.font.render(f"score: {self.score}", True, (0, 0, 0))

                # Check if the new score is higher than the high score
           if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def checkCollisions(self):
       if len(self.pipes):
           if self.bird.rect.bottom > 568:
               self.bird.update_on = False
               self.is_enter_pressed = False
               self.collision_sound.play()  # sound for pipe collision
           if (self.bird.rect.colliderect(self.pipes[0].rect_down) or
          self.bird.rect.colliderect(self.pipes[0].rect_up)):
               self.is_enter_pressed = False
               self.collision_sound.play()  # sound for ground collision

    def updateEverything(self, dt):
       if self.is_enter_pressed:
            # moving ground
            self.ground1_rect.x -= (self.move_speed * dt)
            self.ground2_rect.x -= (self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

            # generating the pipes
            if self.pipe_generate_counter > 70:
                self.pipes.append(Pipe(self.scale_factor, self.move_speed))
                self.pipe_generate_counter = 0

            self.pipe_generate_counter += 1

            # moving the pipes
            for pipe in self.pipes:
               pipe.update(dt)

            if len(self.pipes) != 0:
                if self.pipes[0].rect_up.right < 0:
                    self.pipes.pop(0)

            # moving the bird
       self.bird.update(dt)

    def drawEverything(self):
       self.win.blit(self.bg_img, (0, -300))
       for pipe in self.pipes:
            pipe.drawPipe(self.win)

       self.win.blit(self.ground1_img, self.ground1_rect)
       self.win.blit(self.ground2_img, self.ground2_rect)
       self.win.blit(self.bird.image, self.bird.rect)
       self.win.blit(self.score_text, self.score_text_rect)

        # Display high score
       high_score_text = self.font.render(f"HiGH SCORE: {self.high_score}", True, (220,20,60))
       high_score_text_rect = high_score_text.get_rect(center=(self.width - 150, 30))
       self.win.blit(high_score_text, high_score_text_rect)

    def setupBgAndGround(self):
        # loading the img for ground and background
        self.bg_img = pg.transform.scale_by(pg.image.load("assets/bg.png").convert(), self.scale_factor)
        self.ground1_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)
        self.ground2_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)

        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = 568
        self.ground2_rect.y = 568

    # High score handling
    def load_high_score(self):
       try:
           with open("high_score.txt", "r") as file:
               return int(file.read())
       except FileNotFoundError:
          return 0  # Default high score if the file doesn't exist

    def save_high_score(self):
       with open("high_score.txt", "w") as file:
          file.write(str(self.high_score))


# Run the game
Game = Game()