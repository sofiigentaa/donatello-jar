# Donatello — Proyecto de práctica para Challenge JAR

Proyecto de robot autónomo con **ROS 2 Humble**, **Gazebo Fortress** y el robot simulado Yahboom ROSMASTER.

## Estado actual

- **Etapa 4 completada:** navegación autónoma por pasillo en L, giro a la derecha y parada por posición; respaldo en `donatello_vision/seguir_pasillo_etapa4_completa.py`.
- **Etapa 5 en preparación:** laberinto de práctica `laberinto_simple_victimas.world`, con bloques rojos y azules. Se verificaron `/scan`, `/odom`, `/ground_truth/odom` y `/cmd_vel`.
- **Pendiente:** navegación de un laberinto desconocido, detección visual de víctimas, localización en `map`, reportes en `/victimas` e integración con la interfaz oficial.

**Advertencia:** `donatello_vision/seguir_pasillo.py` fue creado para el pasillo en L; contiene una meta fija `y <= -2.30` y giros a la derecha. **No ejecutarlo sin adaptación en el laberinto nuevo.** El mundo de práctica no está confirmado como mapa oficial.

**Contrato de competencia:** la entrega JAR 2026 se realiza como un fork del
[template oficial](https://github.com/AIRclub-UdeSA/jar_challenge), no desde este
repositorio de simulación. El equipo debe arrancar con
`equipo_jar.competencia.launch.py`, recibir `victimas:=N` y esperar `/map`
antes de mover o reportar. `/victimas` usa `geometry_msgs/msg/PointStamped`
con `frame_id: map`; `/done` usa `std_msgs/msg/Empty`. No se permite usar
`/ground_truth/odom` como localización de competencia. Este repositorio conserva
mundos, mapas y herramientas de simulación para desarrollo; no copiarlo entero
al fork de entrega. Verificar siempre el
[reglamento vigente](https://airclub-udesa.github.io/jar_site/reglamento/).

## Archivos

- `src/yahboom_rosmaster/`: paquetes ROS, modelos, mundos y lanzadores de simulación.
- `donatello_vision/`: controladores Python desarrollados.
- `donatello_vision_respaldo_etapa4/`: respaldos.
- `Dockerfile` y `compose.yaml`: entorno Docker raíz para el workspace, con las
  dependencias ROS resueltas desde los manifiestos de los paquetes.

## Para un compañero con Windows 11

### Requisitos

1. Windows 11 actualizado y virtualización habilitada.
2. WSL 2 con **Ubuntu 22.04** (en PowerShell como administrador: `wsl --install -d Ubuntu-22.04`; reiniciar si se solicita).
3. Docker Desktop, con **Use WSL 2 based engine** y la integración con Ubuntu habilitada en Settings > Resources > WSL Integration.
4. Git en Ubuntu: `sudo apt update && sudo apt install -y git`.
5. Espacio suficiente en disco y memoria para compilar ROS 2 y ejecutar Gazebo.

### Descargar y compilar

Ejecutar **en la terminal Ubuntu de WSL**, no en PowerShell:

```bash
cd ~
git clone URL_DEL_REPOSITORIO donatello-jar
cd ~/donatello-jar
docker compose build
docker compose run --rm donatello
```

Reemplazar `URL_DEL_REPOSITORIO` por la URL real del repositorio una vez publicado. **El Dockerfile y Compose todavía no están validados en Windows.**

El Dockerfile raíz instala las dependencias declaradas por los paquetes ROS al
construir la imagen. Ya **dentro del contenedor**:

```bash
source /opt/ros/humble/setup.bash
cd /root/donatello_ws
colcon build --symlink-install
source install/setup.bash
```

### Iniciar el laberinto de práctica

Dentro del contenedor, con ROS y el workspace cargados:

```bash
ros2 launch yahboom_rosmaster_gazebo rosmaster_gazebo_fortress.launch.py world:=/root/donatello_ws/src/yahboom_rosmaster/yahboom_rosmaster_gazebo/worlds/laberinto_simple_victimas.world spawn_x:=0.0 spawn_y:=0.0 spawn_yaw:=0.0 motion_profile:=ideal motion_bias:=false
```

En otra terminal conectada al mismo contenedor y con ROS cargado, comprobar:

```bash
ros2 topic list
```

Se esperan, entre otros, `/scan`, `/cmd_vel` y `/odom`.

### Advertencia de interfaz gráfica

La configuración `compose.yaml` actual **no incluye los montajes gráficos específicos de WSLg**. Por tanto, la ventana de Gazebo puede no abrirse todavía en Windows 11. Hay que validar o adaptar la integración gráfica antes de considerar completa la instalación. En Linux Mint el contenedor original usa X11 y `/dev/dri`.

## Colaboración con GitHub

Antes de trabajar, actualizar con `git pull`. Trabajar preferentemente en una rama propia, revisar con `git status`, confirmar con `git add` y `git commit`, y subir con `git push`. Abrir pull requests para integrar cambios. No subir contraseñas, tokens ni datos privados.

## Próximas tareas

1. Validar construcción de Docker y Gazebo en Windows 11.
2. Adaptar la navegación para explorar sin coordenadas de meta prefijadas ni depender de `/ground_truth/odom`.
3. Detectar víctimas con cámara y estimar coordenadas en el marco `map`.
4. Publicar reportes conforme al reglamento en `/victimas`.
5. Integrar y probar el formato de lanzamiento oficial de la competencia.

Reglamento: https://airclub-udesa.github.io/jar_site/reglamento/

Proyecto oficial de referencia: https://github.com/AIRclub-UdeSA/jar_challenge
