import grpc
import soldier_pb2
import soldier_pb2_grpc
import random
import time
from concurrent import futures
from colorama import Fore, Style
from logging import *

_SERVER_PORT = 50051
missile_radius = 3
_INITIAL_BATTLE_DURATION = 0

class SoldierService(soldier_pb2_grpc.SoldierServiceServicer):
    def __init__(self):
        self.soldiers = []
        self.missiles = []
        self.missile_id_counter = 0
        self.commander_id = None
        self.field_size = None
        self.most_recent_missile = None
        self.battle_duration = _INITIAL_BATTLE_DURATION
        self.curr = 0
        self.commDead = False
        self.initial_soldier_count = 0
        self.prev_comm = 0
        self.new_comm = 0
        self.impacted_coordinates = []
        self.field = []
        self.T = None
        self.t = None
        basicConfig(filename='server.log', level= INFO, filemode='w')

    def InitializeSoldiers(self, request, context):
        self.field_size = request.field_size
        self.T = request.battle_duration
        self.t = request.missile_interval
        self.initial_soldier_count = request.num_soldiers

        self.field = [['-' for _ in range(self.field_size)] for _ in range(self.field_size)]

        for soldier_id in range(request.num_soldiers):
            x = random.randint(0, self.field_size - 1)
            y = random.randint(0, self.field_size - 1)
            
            while self.field[x][y] != '-':
                x = random.randint(0, self.field_size - 1)
                y = random.randint(0, self.field_size - 1)

            speed = random.randint(0, 4)
            is_commander = soldier_id == request.commander_id
            self.soldiers.append(soldier_pb2.Soldier(id=soldier_id, x=x, y=y, speed=speed, is_commander=is_commander, alive=True))
            if is_commander:
                self.field[x][y] = f'C{soldier_id}'
            else:
                self.field[x][y] = f'S{soldier_id}'

            if is_commander:
                self.commander_id = soldier_id
        self.print_battlefield_status(self.battle_duration, self.prev_comm, self.new_comm, self.most_recent_missile, None, None)
        
        return soldier_pb2.SoldierList(soldiers=self.soldiers)


    def IssueCommand(self, request, context):
        result = "Command received: " + request.command
        return soldier_pb2.CommandResponse(result=result)

    # def LaunchMissile(self, request, context):
    #     if self.battle_duration >= self.T:
    #         return soldier_pb2.CommandResponse(result="Battle duration exceeded. No more missiles can be launched.")
        
    #     missile = soldier_pb2.Missile(
    #         id=self.missile_id_counter,
    #         target_x=request.target_x,
    #         target_y=request.target_y,
    #         category=request.category,
    #     )
    #     self.missiles.append(missile)
    #     self.most_recent_missile = missile
    #     self.missile_id_counter += 1

    #     affected_soldiers = []
    #     is_commander_affected = False

    #     for soldier in self.soldiers:
    #         if soldier.alive and abs(soldier.x - missile.target_x) <= missile_radius and \
    #            abs(soldier.y - missile.target_y) <= missile_radius:
    #             affected_soldiers.append(soldier.id)
    #             if soldier.is_commander:
    #                 is_commander_affected = True

    #     for soldier_id in affected_soldiers:
    #         yield soldier_pb2.MissileStrike(
    #             missile_id=missile.id,
    #             affected_soldier_id=soldier_id,
    #             is_commander_affected=is_commander_affected,
    #         )

    #     self.battle_duration += self.t
    #     time.sleep(self.t)
        
    #     self.print_battlefield_status()
        
    #     for soldier in self.soldiers:
    #         if soldier.id in affected_soldiers:
    #             soldier.alive = False
    #     self.soldiers = [soldier for soldier in self.soldiers if soldier.alive]

    # ...
    def LaunchMissile(self, request, context):
        self.commDead = False
        if self.battle_duration >= self.T:
            self.print_battlefield_status(self.battle_duration, None, None)
            exit()
            
       
        missile = soldier_pb2.Missile(
            id=self.missile_id_counter,
            target_x=request.target_x,
            target_y=request.target_y,
            category=request.category,
        )
        #print("1")
        self.missiles.append(missile)
        self.most_recent_missile = missile
        self.missile_id_counter += 1

        #print("2")
        missile_impacted_coordinates = []
        # for x in range(max(0, missile.target_x - missile_radius-1), 
        #             min(self.field_size, missile.target_x + missile_radius)):
        #     for y in range(max(0, missile.target_y - missile_radius-1), 
        #                 min(self.field_size, missile.target_y + missile_radius)):
        #         if (x, y) not in missile_impacted_coordinates:
        #             missile_impacted_coordinates.append((x, y))
        missile_radius = random.randint(1, 4)
        for x in range(missile.target_x - missile_radius + 1, missile.target_x + missile_radius):
            for y in range(missile.target_y - missile_radius + 1, missile.target_y + missile_radius):
                if (x, y) not in missile_impacted_coordinates:
                    missile_impacted_coordinates.append((x, y))


        #print("3")
        self.soldiers = [soldier for soldier in self.soldiers if soldier.alive]
        affected_soldiers = []
        is_commander_affected = False
        for soldier in self.soldiers:
            if soldier.alive and (soldier.x, soldier.y) in missile_impacted_coordinates:
                soldier.alive = False
                affected_soldiers.append(soldier)
                if soldier.is_commander:
                    self.prev_comm = soldier.id
                    is_commander_affected = True
        self.battle_duration += self.t
        self.curr = self.curr + self.t
        print() 
        print("\nBattlefield status:")
        info("\nBattlefield status:")
        print(f"Battle Duration: {self.battle_duration} seconds")
        info(f"Battle Duration: {self.battle_duration} seconds")
        #print("4")
        for soldier in affected_soldiers:
            new_x, new_y = self.calculate_new_position_based_on_speed(soldier, missile_impacted_coordinates)
            #print("5")
            if new_x is not None and new_y is not None:
                self.field[soldier.x][soldier.y] = '-'
                soldier.x, soldier.y = new_x, new_y
                self.field[soldier.x][soldier.y] = f'S{soldier.id}'
                soldier.alive = True
                print()
                print(''.join(Fore.GREEN + 'Soldier ID : {} SAFE. Moved out of red zone to ({}, {})'.format(soldier.id, new_x, new_y )), end="")
                print(Style.RESET_ALL, end="")
                print()
                info('Soldier ID : {} SAFE. Moved out of red zone to ({}, {})'.format(soldier.id, new_x, new_y ))
            else:
                #self.field[soldier.x][soldier.y] = '-'
                soldier.alive = False
                print()
                print(''.join(Fore.RED + 'Soldier ID : {} DEAD'.format(soldier.id)), end="")
                print(Style.RESET_ALL, end="")
                print()
                info('Soldier ID : {} DEAD'.format(soldier.id))

        #print("out")
        # for soldier in affected_soldiers:
        #     self.field[soldier.x][soldier.y] = '-'

        #self.soldiers = [soldier for soldier in self.soldiers if soldier.alive]
        self.commander_id = self.select_new_commander(affected_soldiers)
        self.new_comm = self.commander_id
        for soldier in self.soldiers:
            if not soldier.is_commander:
                self.field[soldier.x][soldier.y] = f'S{soldier.id}'
            else:
                self.field[soldier.x][soldier.y] = f'C{soldier.id}'

        #self.soldiers = [soldier for soldier in self.soldiers if soldier.alive]
        # self.battle_duration += self.t
        # self.curr = self.curr + self.t
        #time.sleep(self.t // 2)
        if self.battle_duration % self.t == 0:
            self.print_battlefield_status(self.curr, self.prev_comm, self.new_comm,self.most_recent_missile, missile_impacted_coordinates, missile_radius)


    def select_new_commander(self, affected_soldiers):
        if self.commander_id is None or self.commander_id not in [soldier.id for soldier in self.soldiers]:
            while True:
                new_commander = random.choice(self.soldiers)
                if new_commander not in affected_soldiers:
                    new_commander.is_commander = True
                    self.commander_id = new_commander.id
                    x, y = new_commander.x, new_commander.y
                    self.field[x][y] = f'C{new_commander.id}'
                    break 
            self.commDead = True
        return self.commander_id
    

    def calculate_new_position_based_on_speed(self, soldier, missile_impacted_coordinates):
        missile_time_to_strike = self.t / 2

        max_distance = min(soldier.speed, int(missile_time_to_strike))

        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):
                new_x, new_y = soldier.x + dx, soldier.y + dy

                if (
                    0 <= new_x < self.field_size
                    and 0 <= new_y < self.field_size
                    and self.field[new_x][new_y] == '-'
                ):
                    if (new_x, new_y) not in missile_impacted_coordinates:
                        return new_x, new_y
                    else:
                        soldier.alive = False
                        self.field[soldier.x][soldier.y] = '-'
                        return None, None

        return None, None


    def print_battlefield_status(self, battle_duration, prev_comm, new_comm, missile=None, missile_impacted_coordinates=None, missile_radius=None):
        
        print("Number of Soldiers Alive:", sum([1 for soldier in self.soldiers if soldier.alive]))
        info("Number of Soldiers Alive:", sum([1 for soldier in self.soldiers if soldier.alive]))

        # for row in self.field:
        #     print(" ".join(row))
        #     #print '{:4}'.format(val),
        print()
        # print('\n'.join([''.join(['{:8}'.format(item) for item in row]) for row in self.field]))

        # for row in self.field:
        #     for val in row:
        #         print(''.join(Fore.GREEN + '{:8}'.format(val)), end="")
        #     print(Style.RESET_ALL)
        #     print()


        if missile_impacted_coordinates is not None:
            for x in range(self.field_size):
                for y in range(self.field_size):
                    if (x, y) in missile_impacted_coordinates:
                        if self.field[x][y] == '-':
                            print(''.join(Fore.RED + '{:8}'.format('|')), end="")
                            print(Style.RESET_ALL, end="")
                        else:
                            print(''.join(Fore.RED + '{:8}'.format(self.field[x][y])), end="")
                            print(Style.RESET_ALL, end="")
                    # if self[x][y] == '-':
                    #     print(''.join(Fore.YELLOW + '{:8}'.format(self.field[x][y])), end="")
                    #     print(Style.RESET_ALL, end="")
                    elif self.field[x][y] != '-':
                        print(''.join(Fore.GREEN + '{:8}'.format(self.field[x][y])), end="")
                        print(Style.RESET_ALL, end="")
                    else:
                        print(''.join(Fore.YELLOW + '{:8}'.format(self.field[x][y])), end="")
                        print(Style.RESET_ALL, end="")
                print()
                print()
        else:
            for row in self.field:
                for val in row:
                    print(''.join(Fore.GREEN + '{:8}'.format(val)), end="")
                print(Style.RESET_ALL)
                print()

        if missile:
            print("Most Recently Launched Missile:")
            print(f"Missile ID: {missile.id}, Target X: {missile.target_x}, Target Y: {missile.target_y}, Radius: {missile_radius}")
            info(f"Missile ID: {missile.id}, Target X: {missile.target_x}, Target Y: {missile.target_y}, Radius: {missile_radius}")

        if self.commDead:
            print(f"Commander Dead: {prev_comm}")
            print(f"New Commander Elected : {new_comm}")
            info(f"New Commander Elected : {new_comm}")


        print("\nUpdated Coordinates of Soldiers:")
        info("\nUpdated Coordinates of Soldiers:")
        for soldier in self.soldiers:
            if soldier.alive:
                print(f"ID: {soldier.id}, X: {soldier.x}, Y: {soldier.y}, Speed: {soldier.speed}, Commander: {soldier.is_commander}, Alive: {soldier.alive}")
                info(f"ID: {soldier.id}, X: {soldier.x}, Y: {soldier.y}, Speed: {soldier.speed}, Commander: {soldier.is_commander}, Alive: {soldier.alive}")
            else:
                self.field[soldier.x][soldier.y] = '-'
        
        

    def CheckBattleResult(self, request, context):
        soldiers_alive_at_T = sum(1 for soldier in self.soldiers if soldier.alive)
        
        is_battle_won = soldiers_alive_at_T > (self.initial_soldier_count // 2)

        return soldier_pb2.BattleResult(is_battle_won=is_battle_won)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    soldier_pb2_grpc.add_SoldierServiceServicer_to_server(SoldierService(), server)
    server.add_insecure_port('[::]:' + str(_SERVER_PORT))
    server.start()
    print("Server started on port " + str(_SERVER_PORT))
    info("Server started on port " + str(_SERVER_PORT))

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()


