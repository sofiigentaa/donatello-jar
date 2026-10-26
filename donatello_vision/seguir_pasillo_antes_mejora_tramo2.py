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
        self.direccion_giro = 1.0
        self.estado_movimiento = "AVANZAR"
        self.distancia_seguridad = 0.85
        self.distancia_liberacion = 1.00
        self.distancia_izquierda = 0.0
        self.distancia_derecha = 0.0
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
            self.estado_movimiento = "SIN_LIDAR"
            self.obstaculo_detectado = True
            self.publicador.publish(orden)
            self.get_logger().warn(
                'LiDAR sin datos: DETENER',
                throttle_duration_sec=2.0
            )

    def procesar_scan(self, msg):
        self.ultimo_scan = self.get_clock().now()
        if self.estado_movimiento == "SIN_LIDAR":
            self.publicador.publish(Twist())
            return
        frente = []
        izquierda = []
        derecha = []

        for i, distancia in enumerate(msg.ranges):
            angulo = msg.angle_min + i * msg.angle_increment

            angulo_robot = math.atan2(
                math.sin(angulo + math.pi),
                math.cos(angulo + math.pi)
            )

            if abs(angulo_robot) <= math.radians(15):
                if not math.isnan(distancia):
                    frente.append(distancia)

            if math.radians(80) <= angulo_robot <= math.radians(90):
                if not math.isnan(distancia):
                    izquierda.append(distancia)

            if math.radians(-90) <= angulo_robot <= math.radians(-80):
                if not math.isnan(distancia):
                    derecha.append(distancia)

        self.distancia_izquierda = min(izquierda) if izquierda else 0.0
        self.distancia_derecha = min(derecha) if derecha else 0.0

        if frente:
            minimo = min(frente)

            orden = Twist()

            if minimo < self.distancia_seguridad:
                if self.estado_movimiento != "GIRAR":
                    self.direccion_giro = -1.0  # Giro a la derecha para el pasillo en L
                self.estado_movimiento = "GIRAR"
                self.obstaculo_detectado = True

            if self.estado_movimiento == "GIRAR" and minimo > self.distancia_liberacion:
                self.estado_movimiento = "AVANZAR"
                self.obstaculo_detectado = False
            if self.obstaculo_detectado:
                estado = 'GIRAR'
                lado = 'IZQUIERDA' if self.direccion_giro > 0 else 'DERECHA'
                self.get_logger().info(f'Girando hacia: {lado}', throttle_duration_sec=2.0)
                orden.linear.x = 0.0
                orden.angular.z = self.velocidad_giro * self.direccion_giro
            else:
                estado = 'CAMINO LIBRE'
                orden.linear.x = self.velocidad_avance

                # Corregir suavemente la direccion dentro del pasillo.
                izquierda = self.distancia_izquierda
                derecha = self.distancia_derecha

                if (math.isfinite(izquierda) and math.isfinite(derecha)
                        and izquierda > 0.20 and derecha > 0.20
                        and izquierda < 1.20 and derecha < 1.20):
                    error = izquierda - derecha
                    orden.angular.z = max(-0.10, min(0.10, 0.25 * error))

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
