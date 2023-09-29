# import grpc
# import soldier_pb2
# import soldier_pb2_grpc
# import random
# import time

# _SERVER_ADDRESS = 'localhost:50051'

# class SoldierClient:
#     def __init__(self):
#         self.stub = None
#         self.current_time = 0  # Initialize current time to 0

#     def connect_to_server(self):
#         channel = grpc.insecure_channel(_SERVER_ADDRESS)
#         self.stub = soldier_pb2_grpc.SoldierServiceStub(channel)

#     def initialize_soldiers(self, num_soldiers, field_size, commander_id, battle_duration, missile_interval):
#         response = self.stub.InitializeSoldiers(
#             soldier_pb2.SoldierListRequest(
#                 num_soldiers=num_soldiers,
#                 field_size=field_size,
#                 commander_id=commander_id,
#                 battle_duration=battle_duration,
#                 missile_interval=missile_interval,
#             )
#         )
#         self.initial_soldiers = response.soldiers

#     def issue_command(self, command):
#         response = self.stub.IssueCommand(soldier_pb2.CommandRequest(command=command))
#         return response.result

#     def launch_missile(self, target_x, target_y, category):
#         response = self.stub.LaunchMissile(
#             soldier_pb2.LaunchMissileRequest(
#                 target_x=target_x,
#                 target_y=target_y,
#                 category=category,
#             )
#         )
#         return response.result

#     def notify_threat(self, is_commander_dead, dead_soldier_ids):
#         response = self.stub.NotifyThreat(
#             soldier_pb2.ThreatNotification(
#                 is_commander_dead=is_commander_dead,
#                 dead_soldier_ids=dead_soldier_ids,
#             )
#         )
#         return response.result

#     def move_soldier(self, soldier_id, new_x, new_y):
#         response = self.stub.UpdateSoldierPosition(
#             soldier_pb2.UpdateSoldierPositionRequest(
#                 soldier_id=soldier_id,
#                 new_x=new_x,
#                 new_y=new_y,
#             )
#         )
#         return response.result

#     def check_battle_result(self, num_soldiers):
#         response = self.stub.CheckBattleResult(soldier_pb2.CheckBattleResultRequest(num_soldiers=num_soldiers))
#         return response.is_battle_won

#     def run_simulation(self, num_soldiers, field_size, commander_id, battle_duration, missile_interval):
#         self.connect_to_server()

#         self.initialize_soldiers(num_soldiers, field_size, commander_id, battle_duration, missile_interval)
#         print("Soldiers initialized:")
#         for soldier in self.initial_soldiers:
#             print(f"ID: {soldier.id}, X: {soldier.x}, Y: {soldier.y}, Speed: {soldier.speed}, Commander: {soldier.is_commander}")

#         while self.current_time <= battle_duration:
#             # Continue launching missiles periodically
#             target_x = random.randint(0, field_size)  # Change this as needed
#             target_y = random.randint(0, field_size)  # Change this as needed
#             category = random.choice(["Category1", "Category2", "Category3", "Category4"])
#             response = self.launch_missile(target_x, target_y, category)
#             print("Missile launched!")

#             # Sleep for 'missile_interval' seconds before launching the next missile
#             time.sleep(missile_interval)

#             # Update the current time
#             self.current_time += missile_interval

#         print("Battle result:", "won" if self.check_battle_result(num_soldiers) else "lost")

# def run():
#     client = SoldierClient()
#     client.run_simulation(num_soldiers=8, field_size=10, commander_id=0, battle_duration=60, missile_interval=10)

# if __name__ == '__main__':
#     run()

import grpc
import soldier_pb2
import soldier_pb2_grpc
import random
import time
from logging import *

_SERVER_ADDRESS = 'localhost:50051'

class SoldierClient:
    def __init__(self):
        self.stub = None
        self.client_id = None
        self.soldiers = {}
        self.is_commander = False
        self.current_time = 0
        basicConfig(filename='client.log', level= INFO, filemode='w')

    def connect_to_server(self):
        channel = grpc.insecure_channel(_SERVER_ADDRESS)
        self.stub = soldier_pb2_grpc.SoldierServiceStub(channel)

    def initialize_soldiers(self, num_soldiers, field_size, battle_duration, missile_interval):
        response = self.stub.InitializeSoldiers(
            soldier_pb2.SoldierListRequest(
                num_soldiers=num_soldiers,
                field_size=field_size,
                battle_duration=battle_duration,
                missile_interval=missile_interval,
            )
        )

        self.client_id = random.randint(0, num_soldiers - 1)
        commander_id = self.client_id

        for soldier in response.soldiers:
            x, y, speed, alive = soldier.x, soldier.y, soldier.speed, soldier.alive
            is_commander = (soldier.id == commander_id)
            self.soldiers[soldier.id] = {'x': x, 'y': y, 'speed': speed, 'alive': alive, 'commander': is_commander}

        self.is_commander = True if self.client_id == commander_id else False

    def issue_command(self, command):
        response = self.stub.IssueCommand(soldier_pb2.CommandRequest(command=command))
        return response.result

    def launch_missile(self, target_x, target_y, category):
        if not self.is_commander:
            return "Only the commander can launch missiles."

        response = self.stub.LaunchMissile(
            soldier_pb2.LaunchMissileRequest(
                target_x=target_x,
                target_y=target_y,
                category=category,
            )
        )
        return response.result

    def notify_threat(self, is_commander_dead, dead_soldier_ids):
        response = self.stub.NotifyThreat(
            soldier_pb2.ThreatNotification(
                is_commander_dead=is_commander_dead,
                dead_soldier_ids=dead_soldier_ids,
            )
        )
        return response.result


    def check_battle_result(self):
        response = self.stub.CheckBattleResult(soldier_pb2.CheckBattleResultRequest())
        return response.is_battle_won

    def run_simulation(self, num_soldiers, field_size, battle_duration, missile_interval):
        self.connect_to_server()

        self.initialize_soldiers(num_soldiers, field_size, battle_duration, missile_interval)
        print("Soldiers initialized:")
        info("Soldiers initialized:")
        for soldier_id, data in self.soldiers.items():
            print(f"ID: {soldier_id}, X: {data['x']}, Y: {data['y']}, Speed: {data['speed']}, Commander: {data['commander']}")
            info(f"ID: {soldier_id}, X: {data['x']}, Y: {data['y']}, Speed: {data['speed']}, Commander: {data['commander']}")

        while self.current_time <= battle_duration:
            time.sleep(missile_interval)

            self.current_time += missile_interval
            if self.is_commander:
                target_x = random.randint(0, field_size-1)
                target_y = random.randint(0, field_size-1)
                category = random.choice(["Category1", "Category2", "Category3", "Category4"])
                response = self.launch_missile(target_x, target_y, category)
                print("Missile launched!")
                info("Missile launched!")

       
        if self.check_battle_result:
            print("BATTLE WON.")
            info("BATTLE WON.")
        else:
            print("BATTLE LOST.")
            info("BATTLE LOST.")

def run():
    client = SoldierClient()

    flag1 = True
    flag2 = True
    while flag1:
        num_soldiers = int(input('Enter number of soldiers : '))
        field_size = int(input('Enter size of the field : '))
        if num_soldiers > field_size*field_size:
            print('Number of soldiers more than available blocks. Please re-enter.')
            warning('Number of soldiers more than available blocks. Please re-enter.')
            continue
        else:
            flag1 = False
        
        while flag2:
            battle_duration = int(input('Enter duration of battle T : '))
            missile_interval = int(input('Enter missile interval t : '))
            if missile_interval > battle_duration:
                print('Missile Launch interval cannot be greater than duration of battle. Please re-enter.')
                warning('Missile Launch interval cannot be greater than duration of battle. Please re-enter.')
                continue
            else:
                flag2 = False
        client.run_simulation(num_soldiers, field_size, battle_duration, missile_interval)

if __name__ == '__main__':
    run()

