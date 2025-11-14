async function validarLogin(event) {
  if (event) event.preventDefault();

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  if (!username || !password) {
    showWarning('Por favor, completa todos los campos', 'Campos requeridos');
    return false;
  }

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username,
        password: password
      })
    });

    const data = await response.json();

    if (data.success || data.access_token) {
      // Guardar token y datos del usuario
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('usuario', JSON.stringify(data.user));
      localStorage.setItem('isLoggedIn', 'true');
      // Al iniciar sesión, establecer inicio como sección por defecto
      localStorage.setItem('currentSection', 'inicio');

      showSuccess('Bienvenido ' + data.user.username, 'Acceso concedido');

      // Redirigir al home después de un breve delay
      setTimeout(() => {
        window.location.href = "/home";
      }, 1000);
    } else {
      showError(data.message || 'Usuario o contraseña incorrectos', 'Error de autenticación');
    }
  } catch (error) {
    console.error('Error al iniciar sesión:', error);
    showError('No se pudo conectar con el servidor. Verifica que esté corriendo.', 'Error de conexión');
  }

  return false;
}


// Alternar menú lateral
function toggleMenu() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.overlay');
    sidebar.classList.toggle('active');
    const menuToggle = document.querySelector('.menu-toggle');
    
    // Animar botón hamburguesa
    if (menuToggle) {
        menuToggle.classList.toggle('active');
    }
    overlay.classList.toggle('active');
}

// Mostrar sección específica
function showSection(sectionId) {
    console.log('showSection llamado con:', sectionId);

    // Ocultar todas las secciones
    document.querySelectorAll('.section-content').forEach(section => {
        section.classList.remove('active');
    });

    // Remover clase active de todos los items del menú
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });

    // Mostrar la sección seleccionada
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        console.log('Sección activada:', sectionId);
    } else {
        console.error('Sección no encontrada:', sectionId);
    }

    // Activar el item del menú correspondiente
    // RF-12: Buscar el menu-item que corresponde a esta sección
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        const onclick = item.getAttribute('onclick');
        if (onclick && onclick.includes(`'${sectionId}'`)) {
            item.classList.add('active');
        }
    });

    // Guardar la sección actual en localStorage
    localStorage.setItem('currentSection', sectionId);

    // Cargar datos específicos según la sección
    if (sectionId === 'verventas' && typeof cargarVentasDelDia === 'function') {
        console.log('Llamando a cargarVentasDelDia');
        cargarVentasDelDia();
    }

    // RF-12: Cerrar el menú en móviles después de seleccionar
    if (window.innerWidth <= 768) {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.overlay');
        if (sidebar && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    }
}

// Función de logout
function logout() {
    localStorage.removeItem('usuario');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('token');
    localStorage.removeItem('currentSection');
    window.location.href = '/login';
}

// Cargar información del usuario al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si está en la página home
    if (window.location.pathname.includes('home')) {
        const usuario = JSON.parse(localStorage.getItem('usuario'));

        if (!usuario) {
            // Si no hay sesión, redirigir al login
            window.location.href = '/login';
        } else {
            // Mostrar nombre del usuario en el header
            const headerUsername = document.getElementById('headerUsername');
            if (headerUsername) {
                headerUsername.textContent = usuario.username || usuario.username;
            }

            // Mostrar info en sidebar
            const userNameElement = document.querySelector('.user-name');
            const userEmailElement = document.querySelector('.user-email');
            if (userNameElement) userNameElement.textContent = usuario.username || usuario.username;
            if (userEmailElement) userEmailElement.textContent = usuario.email;

            // Restaurar la sección activa desde localStorage SIN animación
            const savedSection = localStorage.getItem('currentSection');
            if (savedSection) {
                // Aplicar directamente sin setTimeout para evitar el "amague"
                showSection(savedSection);
            } else {
                // Si no hay sección guardada, mostrar inicio por defecto
                showSection('inicio');
            }
        }
    }
});
