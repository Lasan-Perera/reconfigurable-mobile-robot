# Reconfigurable Mobile Robot (ROS 2 + ros2_control)

A simulated mobile robot that **physically reconfigures its own morphology at runtime**,
switching between a 4-wheel deployed stance and a compact 2-wheel differential-drive
stance by folding a pair of wheels — with the ROS 2 control stack switching to match,
coordinated by a dedicated reconfiguration sequencing node.

This project is a control-reconfiguration case study, not a multi-module
self-reconfiguration system: the mechanism, kinematics, and controller-switching
architecture are the focus, built from scratch in ROS 2 Humble.

## Why this project exists

Reconfigurable robotics is usually framed around multi-module systems that physically
dock and rearrange (e.g. M-TRAN, PolyBot, SMORES). This project explores a narrower,
practically achievable slice of that idea on a single robot: **can one robot change its
own footprint, and can its software correctly recognize and adapt to that change** —
without inter-module docking or a combinatorial reconfiguration-planning algorithm.

## What it does

- **4-wheel deployed mode** — all four wheels touch the ground, driven together as a
  wide, stable differential-drive base. Suited to open or rough terrain.
- **2-wheel folded mode** — a rear wheel pair folds up and out of contact via an
  actuated hinge joint; the robot drives on the front two wheels only, balanced by a
  passive caster. Suited to squeezing through narrow gaps.
- **Reconfiguration** is a coordinated, safety-ordered sequence — deactivate the active
  drive controller, command the fold joints to their new target, wait for the fold to
  physically complete, then activate the matching drive controller — driven by a
  standalone ROS 2 node calling `ros2_control`'s `switch_controller` service.

## Mechanism design

Each folding wheel is a two-joint kinematic chain, not a single joint:

```
chassis → [fold joint, revolute, 0–90°, axis Y] → fold_arm
                                                      │
                                    [spin joint, continuous, axis Z]
                                                      │
                                                    wheel
```

The fold joint and the drive joint are genuinely different degrees of freedom — folding
needs hard limits and happens rarely; driving needs to spin freely and happens
continuously. A single joint can't do both, so the fold_arm exists purely to let each
joint do its own job independently.

## Repo structure

This repo holds two ROS 2 packages, meant to be built together in one workspace:

```
reconfigurable_robot/
├── reconfig_robot_description/   # robot geometry + ros2_control interfaces
│   ├── urdf/                     # Xacro: modular wheel/chassis macros, fold mechanism
│   ├── config/                   # controller definitions (controllers.yaml)
│   ├── launch/                   # view_robot.launch.py (RViz), control.launch.py (full stack)
│   └── rviz/                     # saved RViz config
└── reconfig_robot_control/       # reconfiguration behavior
    └── reconfig_robot_control/
        └── reconfig_node.py      # the sequencing node (fold + controller switching)
```

### `reconfig_robot_description`

- **`urdf/wheel.xacro`** — modular Xacro macros: `fixed_wheel` (front pair),
  `folding_wheel` (rear pair, parametrized for left/right mirroring via
  `fold_axis_sign`), plus the chassis and caster.
- **`urdf/reconfig_robot.ros2_control.xacro`** — hardware interface declarations
  (velocity command/state for drive joints, position command/state for fold joints).
- **`config/controllers.yaml`** — controller definitions:
  - `front_diff_drive_controller` — 2-wheel mode
  - `four_wheel_diff_drive_controller` — 4-wheel mode (mutually exclusive with the
    above; `ros2_control` enforces this since both claim the front wheels' command
    interface)
  - `fold_position_controller` — commands the fold joints
  - `joint_state_broadcaster` — publishes joint states and TF

### `reconfig_robot_control`

- **`reconfig_node.py`** — a standalone node that performs one full reconfiguration
  sequence: deactivate the current drive controller → command the fold joints →
  poll `/joint_states` until the fold reaches its target (within tolerance) →
  activate the new drive controller. Uses a `switch_controller` service client, a
  `/fold_position_controller/commands` publisher, and a `/joint_states` subscriber.

## Status

- [x] Modular URDF library with a working fold mechanism (verified in RViz: both
      end-states stable, TF tree correct)
- [x] `ros2_control` hardware interfaces and controllers (verified with mock hardware:
      front drive controller responds correctly to `cmd_vel`, fold controller responds
      correctly to position commands)
- [x] Reconfiguration sequencing node — 4-wheel → 2-wheel direction implemented and
      verified end-to-end (controller deactivation, fold motion, controller
      activation all confirmed via `ros2 control list_controllers` and `/joint_states`)
- [x] Reverse sequence (2-wheel → 4-wheel) — full bidirectional auto-detecting reconfiguration node
- [ ] Gazebo simulation (physics, real odometry)
- [ ] Terrain-driven autonomous reconfiguration demo (Nav2 integration)

## Running it

```bash
# Visualize the robot and manually pose it
ros2 launch reconfig_robot_description view_robot.launch.py

# Bring up the full control stack (mock hardware)
ros2 launch reconfig_robot_description control.launch.py

# Drive in 2-wheel mode
ros2 topic pub /front_diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped \
  "{header: {frame_id: 'base_link'}, twist: {linear: {x: 0.2}, angular: {z: 0.0}}}"

# Command the fold joints directly (0 = deployed, 1.5708 = folded)
ros2 topic pub /fold_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [1.5708, 1.5708]}"

# Run the full reconfiguration sequence (assumes 4-wheel mode is currently active)
ros2 run reconfig_robot_control reconfig_node
```

## Requirements

- ROS 2 Humble
- `ros2_control`, `ros2_controllers`, `diff_drive_controller`,
  `joint_state_broadcaster`, `xacro`
- `rclpy`, `controller_manager_msgs`, `sensor_msgs`, `std_msgs` (for the control node)

## Scope and limitations

This is a single-robot, software-triggered reconfiguration project. It deliberately
does **not** implement inter-module docking, autonomous module rearrangement, or a
reconfiguration-planning algorithm — those belong to full self-reconfigurable modular
robotics. The mock hardware interface used for controller development also means
odometry and fold-motion timing are not physically meaningful until the Gazebo
integration is complete.

## Background reading

This project's design was informed by:
- Chennareddy, Agrawal & Karuppiah, *"Modular Self-Reconfigurable Robotic Systems: A
  Survey on Hardware Architectures,"* Journal of Robotics, 2017.
- Wei, Liu, Dong, Zhu & Zhao, *"A Graph-Based Hybrid Reconfiguration Deformation
  Planning for Modular Robots,"* Sensors, 2023.

## License

MIT — see [LICENSE](LICENSE).
