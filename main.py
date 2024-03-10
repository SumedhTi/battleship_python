import pygame
import time
import os
import asyncio
import socket

pygame.font.init()
WIDTH, HEIGHT = 1400, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BATTLESHIP")

#LOADING IMAGES
BG = pygame.transform.scale(pygame.image.load("assets\sea.jpeg"), (WIDTH, HEIGHT))

main_font = pygame.font.SysFont("comicsans", 60)
button_font = pygame.font.SysFont("comicsans", 30)
status = "PLAY AS"
I_AM = ""
soc = socket.socket()
soc.settimeout(10)
host = "localhost"
port = 8000
connection = None
receved = ''
msg_send = ''


class Grid():
    def __init__(self,ystart,yend,xstart,xend):
        self.array = []
        self.count = 0
        self.hit = 0
        self.list = []
        block_size = 60
        for y in range(ystart,yend):
            for x in range(xstart,xend):
                rect = pygame.Rect(x*(block_size+5), y*(block_size+5), block_size, block_size)
                pygame.draw.rect(WIN, (0,0,100), rect, 2)
                self.array.append([rect,(0,0,100),2,False])
    
    def draw(self):
        for i in self.array:
            pygame.draw.rect(WIN, i[1], i[0], i[2])
    
    def attck(self,pos):
        global status
        global msg_send
        if status != "Your Turn":
            return
        i=0
        for c in self.array:
            if c[0].collidepoint(pos):
                c[1] = (100,0,0)
                c[2] = 0
                break
            i+=1
        print(i)
        if i != 64:
            num_to_word = ["A","B","C",'D','E','F','G','H']
            status = f"Attaking {num_to_word[(i)//8]}{i%8}"
            self.attck_pos = i
            msg_send = str(i)
    
    def embed(self,Ships):
        global status
        arr = []
        for i in self.array:
            arr.append(i[0])
        for ship in Ships: 
            self.list.append(ship.collidelistall(arr))
        
        for i in self.list:
            for j in i:
                self.array[j][1] = (64,64,64)
                self.array[j][2] = 0
                self.array[j][3] = True
                self.count += 1
        
        if I_AM == "SERVER":
            status = "Your Turn"
        else:
            status = "Enemy Turn"
        

    def reply(self):
        global receved
        global msg_send
        global status
        self.array[int(receved)][1] = (255,0,0)
        self.hit += 1
        if self.check_win():
            msg_send = "lost"
            status = "Lost"
        else:
            if self.array[int(receved)][3]:
                msg_send = "True"
            else:
                msg_send = "False"
        receved = ''

            
    def check_hit(self):
        global status
        global receved
        global msg_send
        if receved == b'True':
            status = "HIT"
            self.array[self.attck_pos][1] = (0,255,0)
        else:
            status = "MISS"
        receved = ''
        msg_send = 'your turn'
    
    def check_win(self):
        if self.hit == self.count:
            return True
        else:
            return False


#INITIALS        
FPS = 60
start = False
initial = True
clock = pygame.time.Clock()
own_grid = Grid(2,10,2,10)
ene_grid = Grid(2,10,12,20)
ship_click = None
#SHIPS
destroyer = pygame.Rect(20,100,45,100)
cruiser = pygame.Rect(20,230,45,160)
submarine = pygame.Rect(20,410,45,160)
carrier = pygame.Rect(80,100,45,300)
battleship = pygame.Rect(80,410,45,220)

Ships = [destroyer,cruiser,submarine,carrier,battleship]
conf = pygame.Rect((WIDTH/2)+50,HEIGHT/2, 250, 50)
ser = pygame.Rect(200,(HEIGHT/2)-50,300,50)
cli = pygame.Rect(200,(HEIGHT/2)+50,300,50)
colour1 = (0,0,0)
colour2 = (0,0,0)

def redraw_window():
    WIN.blit(BG, (0,0))
    label = main_font.render(status, 1, (255,255,255))
    WIN.blit(label, (100,10))
    if initial or connection == None:
        pygame.draw.rect(WIN, colour1, ser)
        button_label = button_font.render("SERVER", 1, (255,255,255))
        WIN.blit(button_label, (200,(HEIGHT/2)-50))

        pygame.draw.rect(WIN, colour2, cli)
        button_label = button_font.render("CLIENT", 1, (255,255,255))
        WIN.blit(button_label, (200,(HEIGHT/2)+50))
        if initial == False and connection == None:
            if I_AM == "CLIENT":
                label = button_font.render("Pls Enter host IP address in console", 1, (255,255,255))
                WIN.blit(label, (WIDTH/2,(HEIGHT/2)))
                pygame.display.update()
                global host
                host = input("ENTER IP OF HOST : ")
            else:
                label = button_font.render("Wating for player 2", 1, (255,255,255))
                WIN.blit(label, (WIDTH/2,(HEIGHT/2)))
            
        pygame.display.update()
        return
    

    own_grid.draw()  

    
    if start != True:
        pygame.draw.rect(WIN, (0,0,0), conf)
        button_label = button_font.render("CONFIRM", 1, (255,255,255))
        WIN.blit(button_label, ((WIDTH/2)+100,(HEIGHT/2)))
        for ship in Ships:
            pygame.draw.rect(WIN,(255,0,0),ship)
    else:        
        ene_grid.draw()  

    pygame.display.update()

async def main1():
    global status
    global ship_click
    global start
    global initial
    global colour1
    global colour2
    global receved
    global I_AM
    run = True

    while run:
        clock.tick(FPS)
        redraw_window()

        if start == True:                   
            if receved != '':
                if receved.isdigit():
                    own_grid.reply()
                else:
                    if receved == b"your turn":
                        status = "Your Turn"
                        receved = ''
                    elif receved == b"lost":
                        status = "WIN"
                        receved = ''
                        ene_grid.array[ene_grid.attck_pos][1] = (0,255,0)
                    else:
                        ene_grid.check_hit()
            
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    for num, ship in enumerate(Ships):
                        if ship.collidepoint(event.pos):
                            ship_click = num
                else:
                    pos = pygame.mouse.get_pos()
                    ene_grid.attck(pos)
                    if conf.collidepoint(pos):
                        start = True
                        own_grid.embed(Ships)
                    if ser.collidepoint(pos):
                        initial = False
                        I_AM = "SERVER"
                        status = "Setup"
                        colour1 = (0,255,0)
                        soc.bind((host, port))        
                        soc.listen(5) 
                    if cli.collidepoint(pos):
                        initial = False
                        I_AM = "CLIENT"
                        status = "Setup"
                        colour2 = (0,255,0)


            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                ship_click = None

            if event.type == pygame.MOUSEMOTION and ship_click != None:
                Ships[ship_click].move_ip(event.rel)
            
            if event.type == pygame.KEYDOWN and event.unicode == "r" and ship_click != None:
                temp = Ships.pop(ship_click)
                temp = pygame.Rect(temp[0],temp[1],temp[3],temp[2])
                Ships.insert(ship_click, temp)


            if event.type == pygame.QUIT:
                run = False
                quit()
        
        await asyncio.sleep(0.001)
            




async def start_server():
    global receved
    global msg_send
    global start
    while True:
        if I_AM == "":
            print("wating")
            await asyncio.sleep(1)
        
        elif I_AM == "SERVER": 
            global connection
            print('Server started!')
            print('Waiting for clients...')
            addr = None
            while addr == None:
                try:
                    connection, addr = soc.accept()     
                    print('Got connection from', addr)
                    connection.settimeout(1)
                except TimeoutError:
                    await asyncio.sleep(2)

            while start == False:
                await asyncio.sleep(5)

            while True:
                if msg_send != '':
                    connection.send(msg_send.encode()) 
                    msg_send = ''
                try:
                    receved = connection.recv(1024)
                except TimeoutError:
                    await asyncio.sleep(2)
                await asyncio.sleep(2)
        
        elif I_AM == "CLIENT":
            while connection == None:
                try:
                    soc.connect((host, port))
                    connection = True
                    print("connected")
                    soc.settimeout(1)
                except (TimeoutError, ConnectionRefusedError):
                    await asyncio.sleep(2)
            
            while start == False:
                await asyncio.sleep(5)
            
            while True:
                if msg_send != '':
                    soc.send(msg_send.encode())
                    msg_send = ''
                try:
                    receved = soc.recv(1024)
                except TimeoutError:
                    await asyncio.sleep(2)
                await asyncio.sleep(2)


async def main():
#         tasks = []
#         tasks.append(asyncio.create_task(main1()))
#         tasks.append(asyncio.create_task(start_server()))
    await asyncio.gather(start_server(),main1())


asyncio.run(main())