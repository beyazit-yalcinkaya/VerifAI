""" Scenario Description
Based on 2019 Carla Challenge Traffic Scenario 03.
Leading vehicle decelerates suddenly due to an obstacle and 
ego-vehicle must react, performing an emergency brake or an avoidance maneuver.
"""
param map = localPath('../../../tests/scenic/Town01.xodr')
param carla_map = 'Town01'

model scenic.simulators.newtonian.driving_model

#CONSTANTS
EGO_SPEED = 7.5
THROTTLE_ACTION = 0.6
BRAKE_ACTION = 1.0
EGO_OFFSET = Range(-20, -15)
EGO_BRAKING_THRESHOLD = 11

behavior FollowTrajectoryBehaviorAvoidCollision(target_speed, trajectory):
    try:
        do FollowTrajectoryBehavior(target_speed=target_speed, trajectory=trajectory)

    interrupt when withinDistanceToAnyObjs(self, EGO_BRAKING_THRESHOLD):
        take SetBrakeAction(BRAKE_ACTION)

scenario SubScenario1(target):
    setup:
        override target with behavior FollowLaneBehavior(EGO_SPEED)

scenario SubScenario2(target, direction):
    setup:
        current_lane = target.lane
        straight_manuevers = filter(lambda i: i.type == direction, current_lane.maneuvers)
        maneuver = None
        if len(straight_manuevers) > 0:
            maneuver = Uniform(*straight_manuevers)
        assert maneuver
        override target with behavior FollowTrajectoryBehaviorAvoidCollision(target_speed=1, trajectory=[target.lane, maneuver.connectingLane, maneuver.endLane])

        points = maneuver.endLane.points
        if len(points) > 0:
            point = points[0]
        obstacle = new Car at point

scenario SubScenario2S(target):
    compose:
        do SubScenario2(target, ManeuverType.STRAIGHT)

scenario SubScenario2L(target):
    compose:
        do SubScenario2(target, ManeuverType.LEFT_TURN)

scenario Main():
    setup:
        ego = new Car following roadDirection from 171.87 @ 2.04 for EGO_OFFSET, with behavior FollowLaneBehavior(0)
    compose:
        do SubScenario1(ego) until (distance to intersection) < 5
        do choose SubScenario2S(ego), SubScenario2L(ego)

