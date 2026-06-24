import { useRef, useEffect } from 'react'

export default function ThreeDBackground() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let scene: any
    let camera: any
    let renderer: any
    let animationId: number
    let shapes: any[] = []

    const init = async () => {
      const THREE = await import('three')

      scene = new THREE.Scene()

      camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
      camera.position.z = 5

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
      renderer.setSize(window.innerWidth, window.innerHeight)
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

      if (containerRef.current) {
        containerRef.current.appendChild(renderer.domElement)
      }

      // Lights
      const ambientLight = new THREE.AmbientLight(0x6366f1, 0.4)
      scene.add(ambientLight)
      const directionalLight = new THREE.DirectionalLight(0x6366f1, 0.6)
      directionalLight.position.set(1, 1, 1)
      scene.add(directionalLight)
      const pointLight = new THREE.PointLight(0x8b5cf6, 0.3)
      pointLight.position.set(-2, 1, 2)
      scene.add(pointLight)

      // Geometry configs
      const geoConfigs = [
        { type: 'TorusGeometry', args: [0.6, 0.2, 16, 32] },
        { type: 'OctahedronGeometry', args: [0.5] },
        { type: 'IcosahedronGeometry', args: [0.5] },
        { type: 'TorusKnotGeometry', args: [0.5, 0.15, 64, 8] },
      ]

      const colors = [0x6366f1, 0x8b5cf6, 0xa78bfa, 0x7c3aed, 0x818cf8]
      const positions = [
        { x: -1.8, y: 0.5, z: -1 },
        { x: 1.6, y: -0.8, z: -0.5 },
        { x: 0, y: 1.5, z: -1.5 },
        { x: -1.2, y: -1.2, z: -1 },
        { x: 1.5, y: 1.0, z: -1.2 },
      ]
      const rotations = [
        { x: 0.3, y: 0.5, z: 0.1 },
        { x: 0.1, y: 0.8, z: 0.3 },
        { x: 0.5, y: 0.2, z: 0.7 },
        { x: 0.8, y: 0.3, z: 0.2 },
        { x: 0.2, y: 0.6, z: 0.4 },
      ]
      const speeds = [
        { x: 0.003, y: 0.005 },
        { x: 0.004, y: 0.003 },
        { x: 0.005, y: 0.002 },
        { x: 0.002, y: 0.006 },
        { x: 0.004, y: 0.004 },
      ]

      for (let i = 0; i < 5; i++) {
        const cfg = geoConfigs[i % geoConfigs.length]
        let geometry

        switch (cfg.type) {
          case 'TorusGeometry':
            geometry = new THREE.TorusGeometry(cfg.args[0], cfg.args[1], cfg.args[2], cfg.args[3])
            break
          case 'OctahedronGeometry':
            geometry = new THREE.OctahedronGeometry(cfg.args[0])
            break
          case 'IcosahedronGeometry':
            geometry = new THREE.IcosahedronGeometry(cfg.args[0])
            break
          case 'TorusKnotGeometry':
            geometry = new THREE.TorusKnotGeometry(cfg.args[0], cfg.args[1], cfg.args[2], cfg.args[3])
            break
        }

        const material = new THREE.MeshPhongMaterial({
          color: colors[i % colors.length],
          transparent: true,
          opacity: 0.25,
          shininess: 30,
        })

        const mesh = new THREE.Mesh(geometry, material)
        mesh.position.set(positions[i].x, positions[i].y, positions[i].z)
        mesh.rotation.set(rotations[i].x, rotations[i].y, rotations[i].z)
        mesh.userData = { speed: speeds[i] }
        scene.add(mesh)
        shapes.push(mesh)

        // Wireframe overlay
        const wireMat = new THREE.MeshBasicMaterial({
          color: colors[i % colors.length],
          wireframe: true,
          transparent: true,
          opacity: 0.08,
        })
        const wireframe = new THREE.Mesh(geometry.clone(), wireMat)
        wireframe.position.copy(mesh.position)
        wireframe.rotation.copy(mesh.rotation)
        scene.add(wireframe)
        shapes.push(wireframe)
      }

      const animate = () => {
        animationId = requestAnimationFrame(animate)
        shapes.forEach((mesh: any) => {
          if (mesh.userData?.speed) {
            mesh.rotation.x += mesh.userData.speed.x
            mesh.rotation.y += mesh.userData.speed.y
          } else {
            mesh.rotation.x += 0.002
            mesh.rotation.y += 0.003
          }
        })
        renderer.render(scene, camera)
      }

      animate()
    }

    init()

    const handleResize = () => {
      if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight
        camera.updateProjectionMatrix()
        renderer.setSize(window.innerWidth, window.innerHeight)
      }
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      cancelAnimationFrame(animationId)
      if (renderer) {
        renderer.dispose()
        if (containerRef.current && containerRef.current.contains(renderer.domElement)) {
          containerRef.current.removeChild(renderer.domElement)
        }
      }
      shapes = []
    }
  }, [])

  return (
    <div
      ref={containerRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
        opacity: 0.7,
      }}
    />
  )
}
