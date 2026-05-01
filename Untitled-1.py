
# !/usr/bin/env python3
from pyniryo import *
import time

# Connect to robot
robot = NiryoRobot("10.10.10.10")
sensor_pin_id    = PinID.DI5

workspace_name = "Wokspace_test"
observation_pose = PoseObject(0.1618,0.1716,0.266,1.942,1.1478,-2.5301)

place_pose_RED   = PoseObject(-0.0055,-0.2395,0.1119,-2.057,1.2714,1.4726)
place_pose_BLUE  = PoseObject(-0.1463,0.2562,0.0795,-2,1.3067,-1.0353)
place_pose_GREEN = PoseObject(-0.1817,-0.241,0.1044,-1.8443,1.3884,1.1396)
pick_pose = PoseObject(0.1911,0.1405,0.0545,2.6135,1.521,-2.8091)

robot.clear_collision_detected()
robot.calibrate_auto()
robot.update_tool()

conveyor_id = robot.set_conveyor()
catch_count = 0

# Move to the viewing position once at the start
robot.move(observation_pose)

robot.led_ring_rainbow_cycle()


max_catch_count = 3
height_offset   = - 0.5  # tweak this if gripper is too high/low at pick

while catch_count < max_catch_count:

    # 1. Run conveyor until sensor triggers

    robot.run_conveyor(conveyor_id, speed=50, direction=ConveyorDirection.FORWARD)
    while robot.digital_read(sensor_pin_id) == PinState.HIGH:
        robot.wait(0.1)
    robot.stop_conveyor(conveyor_id)
 

    # 2. Move to observation pose
    robot.move(observation_pose)

    # 3. get_target_pose_from_cam — camera detects object and returns a PoseObject
    #    you can then modify it before picking (add z offset, clamp values, etc.)
    try:
        obj_found, obj_pose, shape, color = robot.get_target_pose_from_cam(
            workspace_name,
            height_offset=height_offset,
            shape=ObjectShape.ANY,
            color=ObjectColor.ANY)
       
        print(color)
        print(shape)
 
    except TypeError:
        continue

    if not obj_found:
        continue
    # 4. Optional: override or clamp the z if camera pose is unreliable
    # obj_pose = obj_pose.copy_with_offsets(z_offset=0.005)

    # 5. Manually execute the pick using the camera-derived pose


    robot.pick(pick_pose)


    # 6. Route by color
    if color == ObjectColor.RED:
        target_pose = place_pose_RED
                 
    elif color == ObjectColor.BLUE:
        target_pose = place_pose_BLUE

    else:
        target_pose = place_pose_GREEN

    robot.place(target_pose)

    catch_count += 1

robot.stop_conveyor(conveyor_id)
