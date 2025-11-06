#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Odometry
from geometry_msgs.msg import Twist
import numpy as np
from collections import deque
import math

class FloodFillMazeSolver(Node):
    def __init__(self):
        super().__init__('floodfill_maze_solver')
        
        # Subscribers
        self.map_sub = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, 10)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        
        # Publisher
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Parameters
        self.goal_cell = (3,3)  # example goal (y, x)
        self.map_received = False
        self.odom_received = False
        self.timer = self.create_timer(0.2, self.navigate_step)
        
    def map_callback(self, msg):
        self.resolution = msg.info.resolution
        self.origin = msg.info.origin
        width = msg.info.width
        height = msg.info.height
        data = np.array(msg.data).reshape((height, width))
        self.maze = (data == 0).astype(int)  # 1=free, 0=wall
        self.dist_map = self.flood_fill(self.maze, self.goal_cell)
        self.map_received = True

    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        self.odom_received = True

    def world_to_grid(self, x, y):
        gx = int((x - self.origin.position.x) / self.resolution)
        gy = int((y - self.origin.position.y) / self.resolution)
        return gy, gx  # return (row, col)

    def grid_to_world(self, gy, gx):
        x = self.origin.position.x + gx * self.resolution + self.resolution/2
        y = self.origin.position.y + gy * self.resolution + self.resolution/2
        return x, y

    def flood_fill(self, maze, goal):
        rows, cols = maze.shape
        dist = np.full_like(maze, fill_value=9999)
        q = deque()
        gy, gx = goal
        dist[gy][gx] = 0
        q.append((gy, gx))
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        
        while q:
            y, x = q.popleft()
            for dy, dx in directions:
                ny, nx = y+dy, x+dx
                if 0 <= ny < rows and 0 <= nx < cols:
                    if maze[ny][nx] == 1 and dist[ny][nx] > dist[y][x] + 1:
                        dist[ny][nx] = dist[y][x]+1
                        q.append((ny,nx))
        return dist

    def navigate_step(self):
        if not (self.map_received and self.odom_received):
            return
        
        gy, gx = self.world_to_grid(self.robot_x, self.robot_y)
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        min_dist = self.dist_map[gy][gx]
        next_cell = (gy, gx)
        
        # Find neighbor with smallest distance
        for dy, dx in directions:
            ny, nx = gy+dy, gx+dx
            if 0 <= ny < self.dist_map.shape[0] and 0 <= nx < self.dist_map.shape[1]:
                if self.dist_map[ny][nx] < min_dist:
                    min_dist = self.dist_map[ny][nx]
                    next_cell = (ny, nx)
        
        # Compute velocity towards next cell
        wx, wy = self.grid_to_world(next_cell[0], next_cell[1])
        dx = wx - self.robot_x
        dy = wy - self.robot_y
        distance = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        
        cmd = Twist()
        if distance > 0.05:
            cmd.linear.x = 0.1
            cmd.angular.z = 2.0 * (angle - self.get_yaw())
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
        
        self.cmd_pub.publish(cmd)

    def get_yaw(self):
        # Convert quaternion to yaw
        import tf_transformations
        q = [0,0,0,1]
        if hasattr(self, 'robot_q'):
            q = self.robot_q
        else:
            q = [0,0,0,1]
        _, _, yaw = tf_transformations.euler_from_quaternion(q)
        return yaw

def main(args=None):
    rclpy.init(args=args)
    node = FloodFillMazeSolver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

