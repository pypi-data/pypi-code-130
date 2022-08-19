#!usr/bin/env python3

import gym
from gym import error, spaces, utils
from gym.utils import seeding
import os
import pybullet as pb
import pybullet_data
import math
import numpy as np
import random
import sys

ROBOT_PATH = '/home/saun/ReinforcementLearning_Robot/src/differential_robot/urdf/diff_robot.urdf'
ENV_PATH = '/home/saun/ReinforcementLearning_Robot/src/turtlebot3_simulations/turtlebot3_gazebo/models/training_maze/env.urdf'
sys.path.insert(0,ROBOT_PATH)

class DB_Env(gym.Env):
    metadata = {"render.modes":["robot"]}
    def __init__(self):
        pb.connect(pb.GUI)
        pb.resetDebugVisualizerCamera(cameraDistance=1.5, cameraYaw=0, cameraPitch=-40, cameraTargetPosition=[0.55,-0.35,0.2])
        self.action_space = spaces.Box(np.array([-1]*4), np.array([1]*4))
        self.observation_space = spaces.Box(np.array([-1]*5), np.array([1]*5))
        
    def reset(self):
        pb.resetSimulation()
        pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING,0) # we will enable rendering after we loaded everything
        pb.setGravity(0,0,-10)
        urdfRootPath=pybullet_data.getDataPath()

        self.planeUid = pb.loadURDF(os.path.join(urdfRootPath,"plane.urdf"), basePosition=[0,0,-0.08])

        rest_poses = [0,-0.215,0,-2.57,0,2.356,2.356,0.08,0.08]
        self.robotID = pb.loadURDF(ROBOT_PATH,useFixedBase=True)
        for i in range(7):
            pb.resetJointState(self.robotID,i, rest_poses[i])

        self.envID = pb.loadURDF(ENV_PATH,basePosition=[0.0,0.0,0.0])

        # state_object= [random.uniform(0.5,0.8),random.uniform(-0.2,0.2),0.05]
        # self.objectUid = pb.loadURDF(os.path.join(urdfRootPath, "random_urdfs/000/000.urdf"), basePosition=state_object)
        state_robot = pb.getLinkState(self.robotID, 8)[0]
        # state_fingers = (pb.getJointState(self.robotID,9)[0], pb.getJointState(self.robotID, 10)[0])
        observation = state_robot
        pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING,1) # rendering's back on again
        return observation

    def step(self, action):
        pb.configureDebugVisualizer(pb.COV_ENABLE_SINGLE_STEP_RENDERING)
        orientation = pb.getQuaternionFromEuler([0.,-math.pi,math.pi/2.])
        dv = 0.005
        dx = action[0] * dv
        dy = action[1] * dv
        dz = action[2] * dv
        fingers = action[3]

        currentPose = pb.getLinkState(self.robotID, 11)
        currentPosition = currentPose[0]
        newPosition = [currentPosition[0] + dx,
                       currentPosition[1] + dy,
                       currentPosition[2] + dz]
        jointPoses = pb.calculateInverseKinematics(self.robotID,11,newPosition, orientation)

        pb.setJointMotorControlArray(self.robotID, list(range(7))+[9,10], pb.POSITION_CONTROL, list(jointPoses)+2*[fingers])

        pb.stepSimulation()

        # state_object, _ = pb.getBasePositionAndOrientation(self.objectUid)
        state_robot = pb.getLinkState(self.robotID, 11)[0]
        # state_fingers = (pb.getJointState(self.robotID,9)[0], pb.getJointState(self.robotID, 10)[0])
        if state_robot[2]>0.45:
            reward = 1
            done = True
        else:
            reward = 0
            done = False
        info = state_robot
        observation = state_robot
        return observation, reward, done, info

    def render(self, mode='robot'):
        view_matrix = pb.computeViewMatrixFromYawPitchRoll(cameraTargetPosition=[1.0,0.05,0.35],
                                                            distance=.7,
                                                            yaw=-90,
                                                            pitch=0,
                                                            roll=0,
                                                            upAxisIndex=2)
        proj_matrix = pb.computeProjectionMatrixFOV(fov=60,
                                                     aspect=float(960) /720,
                                                     nearVal=0.1,
                                                     farVal=100.0)
        (_, _, px, _, _) = pb.getCameraImage(width=960,
                                              height=720,
                                              viewMatrix=view_matrix,
                                              projectionMatrix=proj_matrix,
                                              renderer=pb.ER_BULLET_HARDWARE_OPENGL)

        rgb_array = np.array(px, dtype=np.uint8)
        rgb_array = np.reshape(rgb_array, (720,960, 4))

        rgb_array = rgb_array[:, :, :3]
        return rgb_array

    def Control(self, V_right, V_left):
        pb.setJointMotorControlArray(bodyUniqueId=self.robotID, jointIndices=[7,8],
                                    controlMode=pb.VELOCITY_CONTROL, targetVelocities=[V_right, V_left], forces=[1.0,1.0])


    def close(self):
        pb.disconnect()
