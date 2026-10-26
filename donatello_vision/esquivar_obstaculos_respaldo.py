import math
import rclpy

from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class ControlObstaculos(Node):
    def __init__(self):
        super().__init__('control_obstaculos')
        self.publicador = self.create_publisher(Twist, '/cmd_vel', 10)
        self.velocidad_avance = 0.08
        self.velocidad_giro = 0.30
        self.estado_movimiento = "AVANZAR"
        self.distancia_seguridad = 0.40
        self.distancia_liberacion = 0.60
        self.obstaculo_detectado = False
        self.ultimo_scan = None
        self.create_timer(0.1, self.verificar_lidar)

        self.create_subscription(
            LaserScan,
            '/scan',
            self.procesar_scan,
            qos_profile_sensor_data
        )

        self.get_logger().info('Control de obstaculos iniciado')

    def verificar_lidar(self):
        orden = Twist()

        if self.ultimo_scan is None:
            self.publicador.publish(orden)
            return

        tiempo = (self.get_clock().now() - self.ultimo_scan).nanoseconds / 1e9

        if tiempo > 1.0:
            self.obstaculo_detectado = True
            self.publicador.publish(orden)
            self.get_logger().warn(
                'LiDAR sin datos: DETENER',
                throttle_duration_sec=2.0
            )

    def procesar_scan(self, msg):
        self.ultimo_scan = self.get_clock().now()
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

            orden = Twist()

            if minimo < self.distancia_seguridad:
                self.estado_movimiento = "GIRAR"
                self.obstaculo_detectado = True

            if self.estado_movimiento == "GIRAR" and minimo > self.distancia_liberacion:
                self.estado_movimiento = "AVANZAR"
                self.obstaculo_detectado = False
            if self.obstaculo_detectado:
                estado = 'DETENER'
                orden.linear.x = 0.0
                orden.angular.z = self.velocidad_giro
            else:
                estado = 'CAMINO LIBRE'
                orden.linear.x = self.velocidad_avance

            self.publicador.publish(orden)

            self.get_logger().info(
                f'Distancia frontal: {minimo:.2f} m | {estado}',
                throttle_duration_sec=2.0
            )
        else:
            self.obstaculo_detectado = True
            self.publicador.publish(Twist())
            self.get_logger().warn(
                'Sin mediciones frontales validas: DETENER',
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
        if rclpy.ok():
            nodo.publicador.publish(Twist())
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
