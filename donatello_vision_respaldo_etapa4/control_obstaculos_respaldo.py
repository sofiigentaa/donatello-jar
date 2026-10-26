import math
import rclpy

from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class ControlObstaculos(Node):
    def __init__(self):
        super().__init__('control_obstaculos')

        self.create_subscription(
            LaserScan,
            '/scan',
            self.procesar_scan,
            qos_profile_sensor_data
        )

        self.get_logger().info('Control de obstaculos iniciado')

    def procesar_scan(self, msg):
        frente = []

        for i, distancia in enumerate(msg.ranges):
            angulo = msg.angle_min + i * msg.angle_increment

            angulo_robot = math.atan2(
                math.sin(angulo + math.pi),
                math.cos(angulo + math.pi)
            )

            if abs(angulo_robot) <= math.radians(15):
                if math.isfinite(distancia):
                    frente.append(distancia)

        if frente:
            minimo = min(frente)

            if minimo < 0.40:
                estado = 'DETENER'
            else:
                estado = 'CAMINO LIBRE'

            self.get_logger().info(
                f'Distancia frontal: {minimo:.2f} m | {estado}',
                throttle_duration_sec=2.0
            )
        else:
            self.get_logger().info(
                'Sin mediciones frontales validas',
                throttle_duration_sec=2.0
            )


def main():
    rclpy.init()
    nodo = ControlObstaculos()

    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
