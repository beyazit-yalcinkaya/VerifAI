""" Scenario Description
Based on 2019 Carla Challenge Traffic Scenario 03.
Leading vehicle decelerates suddenly due to an obstacle and 
ego-vehicle must react, performing an emergency brake or an avoidance maneuver.
"""
# param map = localPath('../../../tests/scenic/Town01.xodr')
param map = localPath('../../tests/scenic/Town01.xodr')
param carla_map = 'Town01'

model scenic.simulators.newtonian.driving_model

#CONSTANTS
# EGO_SPEED = 10
EGO_SPEED = 1
THROTTLE_ACTION = 0.6
BRAKE_ACTION = 1.0
EGO_TO_OBSTACLE = Range(-20, -15)
EGO_BRAKING_THRESHOLD = 11

#EGO BEHAVIOR: Follow lane and brake when reaches threshold distance to obstacle
behavior EgoBehavior(speed=10):    
    try:
        do FollowLaneBehavior(speed)

    interrupt when withinDistanceToAnyObjs(self, EGO_BRAKING_THRESHOLD):
        take SetBrakeAction(BRAKE_ACTION)

scenario PlaceCar(position, speed):
    precondition: True and True
    invariant: True and True
    setup:
        obstacle = new Car following roadDirection from position for -EGO_TO_OBSTACLE, with behavior FollowLaneBehavior(speed)

scenario Main():
    precondition: True and True
    invariant: True and True
    setup:
        ego = new Car following roadDirection from 171.87 @ 2.04 for EGO_TO_OBSTACLE, with behavior EgoBehavior(EGO_SPEED)
    compose:
        # do choose Temp(ego.position, 1), Temp(ego.position, 2)
        do Temp(ego.position, 0) for 1 seconds
        do Temp(ego.position, EGO_SPEED) for 10 seconds

scenario Temp(position, speed):
    precondition: True and True
    invariant: True and True
    # setup:
        # print(f"\n{EGO_TO_OBSTACLE}")
    compose:
        do PlaceCar(position, speed)
