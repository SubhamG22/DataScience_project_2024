function runAnimations() {
    // Initialize animations here if needed
}

// Initialize animations
runAnimations();

document.addEventListener("DOMContentLoaded", function () {
    // Handle Learn More button click
    const learnMoreButtons = document.querySelectorAll(".learn-more-btn");
    learnMoreButtons.forEach(button => {
        button.addEventListener("click", function () {
            alert("Learn more about our services!"); // Replace this with actual functionality
        });
    });

    // Handle Scan Plant button click
    const scanButton = document.getElementById("scan-button");
    if (scanButton) {
        scanButton.addEventListener("click", function () {
            document.getElementById("plant-health-check-results").innerText = "Scanning feature is coming soon!";
        });
    }

    // Handle nutrient recommendations
    const nutrientRecommendations = document.getElementById("nutrient-recommendations");
    if (nutrientRecommendations) {
        nutrientRecommendations.innerText = "Nutrient recommendations will be updated based on your input.";
    }

    // Three.js and GSAP setup
    const canvas = document.querySelector('canvas.webgl');
    const loadingBarElement = document.querySelector('.loading-bar');
    const bodyElement = document.querySelector('body');
    
    if (!canvas || !loadingBarElement || !bodyElement) {
        console.error('Required elements are missing.');
        return;
    }

    const loadingManager = new THREE.LoadingManager(
        () => {
            window.setTimeout(() => {
                if (overlayMaterial) {
                    gsap.to(overlayMaterial.uniforms.uAlpha, {
                        duration: 3,
                        value: 0,
                        delay: 1
                    });
                }
                loadingBarElement.classList.add('ended');
                bodyElement.classList.add('loaded');
                loadingBarElement.style.transform = '';
            }, 500);
        },
        (itemUrl, itemsLoaded, itemsTotal) => {
            console.log(itemUrl, itemsLoaded, itemsTotal);
            const progressRatio = itemsLoaded / itemsTotal;
            loadingBarElement.style.transform = 'scaleX(${progressRatio})';
        }
    );
    
    const gltfLoader = new THREE.GLTFLoader(loadingManager);
    const textureLoader = new THREE.TextureLoader();
    const alphaShadow = textureLoader.load('');

    const scene = new THREE.Scene();

    const overlayGeometry = new THREE.PlaneGeometry(2, 2, 1, 1);
    const overlayMaterial = new THREE.ShaderMaterial({
        vertexShader: `
            void main() {
                gl_Position = vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float uAlpha;
            void main() {
                gl_FragColor = vec4(0.0, 0.0, 0.0, uAlpha);
            }
        `,
        uniforms: {
            uAlpha: { value: 1.0 }
        },
        transparent: true
    });
    const overlay = new THREE.Mesh(overlayGeometry, overlayMaterial);
    scene.add(overlay);

    let butterfly = null;
    let mixer = null;


    gltfLoader.load('./static/assets/butterfly/scene.gltf',
        (gltf) => {
            butterfly = gltf.scene;
            mixer = new THREE.AnimationMixer(butterfly);

            // Add animations from the GLTF file
            gltf.animations.forEach((clip) => {
                mixer.clipAction(clip).play();
            });

            const radius = 1.5;
            butterfly.position.x = 1.5;
            butterfly.rotation.x = Math.PI * 0.2;
            butterfly.rotation.z = Math.PI * 0.15;
            butterfly.scale.set(radius, radius, radius);

            scene.add(butterfly);
        },
        (progress) => {
            console.log(progress);
        },
        (error) => {
            console.error(error);
        }
    );

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(1, 2, 0);
    scene.add(directionalLight);

    const sizes = {
        width: window.innerWidth,
        height: window.innerHeight
    };

    let scrollY = window.scrollY;
    let currentSection = 0;

    const transformButterfly = [
        { rotationZ: 0.45, positionX: 1.5 },
        { rotationZ: -0.45, positionX: -1.5 },
        { rotationZ: 0.45, positionX: 1.5},
        { rotationZ: -0.45, positionX: -1.5 },
        { rotationZ: 0.45, positionX: 1.5},
        { rotationZ: -0.45, positionX: -1.5 },
        { rotationZ: 0.0314, positionX: 0 },
    ];

    window.addEventListener('scroll', () => {
        scrollY = window.scrollY;
        const newSection = Math.round(scrollY / sizes.height);

        if (newSection != currentSection) {
            currentSection = newSection;

            if (butterfly) {
                gsap.to(butterfly.rotation, {
                    duration: 1.5,
                    ease: 'power2.inOut',
                    z: transformButterfly[currentSection].rotationZ
                });
                gsap.to(butterfly.position, {
                    duration: 1.5,
                    ease: 'power2.inOut',
                    x: transformButterfly[currentSection].positionX
                });
            }
        }
    });

    const camera = new THREE.PerspectiveCamera(35, sizes.width / sizes.height, 0.1, 1000);
    camera.position.z = 5;
    scene.add(camera);

    const renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        alpha: true
    });
    renderer.shadowMap.enabled = false;
    renderer.setSize(sizes.width, sizes.height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const clock = new THREE.Clock();
    let lastElapsedTime = 0;

    const tick = () => {
        const elapsedTime = clock.getElapsedTime();
        const deltaTime = elapsedTime - lastElapsedTime;
        lastElapsedTime = elapsedTime;

        if (mixer) {
            mixer.update(deltaTime);
        }

        renderer.render(scene, camera);

        window.requestAnimationFrame(tick);
    };

    tick();

    window.onbeforeunload = function () {
        window.scrollTo(0, 0);
    };
});

// Add class 'loaded' to body once content is fully loaded
window.addEventListener("load", function () {
    document.body.classList.add("loaded");
});