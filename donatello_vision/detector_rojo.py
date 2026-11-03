import cv2
import numpy as np
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data


class DetectorRojo(Node):
    def __init__(self):
        super().__init__('detector_rojo')

        self.create_subscription(
            Image,
            '/cam_1/color/image_raw',
            self.procesar_imagen,
            qos_profile_sensor_data
        )

        self.get_logger().info('Detector rojo iniciado')

    def procesar_imagen(self, msg):
        self.get_logger().info(
            f'Imagen recibida: {msg.width}x{msg.height}',
            once=True
        )
        imagen = np.frombuffer(msg.data, dtype=np.uint8)
        imagen = imagen.reshape((msg.height, msg.width, 3))

        # La c�mara publica im�genes RGB.
        hsv = cv2.cvtColor(imagen, cv2.COLOR_RGB2HSV)

        # El rojo ocupa dos extremos del rango HSV.
        mascara1 = cv2.inRange(
            hsv, np.array([0, 100, 100]), np.array([10, 255, 255])
        )
        mascara2 = cv2.inRange(
            hsv, np.array([170, 100, 100]), np.array([179, 255, 255])
        )

        mascara = mascara1 | mascara2

        # TODO JAR: validar el color frente a distractores y confirmar detecciones en varios frames.

        contornos, _ = cv2.findContours(
            mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if contornos:
            area = max(cv2.contourArea(c) for c in contornos)

            if area > 500:
                # TODO JAR: estimar el centro en el piso con RGB-D y TF; publicar PointStamped en /victimas.
                self.get_logger().info(
                    f'Posible objeto rojo detectado. �rea: {area:.0f} p�xeles'
                )


def main():
    rclpy.init()
    nodo = DetectorRojo()

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
