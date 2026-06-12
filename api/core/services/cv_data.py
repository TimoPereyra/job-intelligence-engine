"""
cv_data.py
Perfil base de Timoteo Pereyra.
La IA adapta este perfil a cada vacante sin inventar nada nuevo.
"""

PROFILE = {
    "name": "Timoteo Pereyra",
    "headline": "Desarrollador Full Stack · PHP · Laravel · JavaScript · Python · React",
    "email": "timopereyra@gmail.com",
    "phone": "(+54) 2345 425347",
    "location": "Capital Federal, Buenos Aires",
    "linkedin": "linkedin.com/in/timoteo-pereyra",

    "summary": (
        "Desarrollador Full Stack con más de 3 años de experiencia en el diseño, desarrollo "
        "y optimización de aplicaciones web orientadas a gestión empresarial, salud digital "
        "y automatización de procesos. Sólido dominio en entornos backend con PHP (Laravel, CodeIgniter) "
        "y Python, combinados con arquitecturas modernas en frontend utilizando JavaScript y React. "
        "Capacidad demostrada para liderar migraciones de sistemas legacy, diseñar bases de datos eficientes "
        "y entregar soluciones autónomas end-to-end con fuerte criterio arquitectónico."
    ),

    "experience": [
        {
            "title": "Analista Desarrollador",
            "company": "Uakika",
            "period": "11/2023 – 03/2025",
            "bullets": [
                "Desarrollé y mantuve dos sistemas web en producción en paralelo: uno en Laravel + HTML/CSS y otro en CodeIgniter + jQuery, atendiendo requerimientos simultáneos de distintas áreas del negocio.",
                "Diseñé, desarrollé e integré un sitio web corporativo utilizando WordPress, adaptando plantillas y optimizando la navegación para mejorar la presencia digital de la marca.",
                "Implementé nuevas funcionalidades end-to-end en los sistemas de la empresa, desde el relevamiento inicial de requerimientos con stakeholders hasta el despliegue exitoso en producción.",
                "Optimicé consultas SQL críticas en bases de datos relacionales, reduciendo de forma medible los tiempos de respuesta en pantallas corporativas de alta carga.",
                "Colaboré activamente en la planificación técnica de sprints mediante metodologías ágiles y en la documentación técnica de decisiones de arquitectura."
            ]
        },
        {
            "title": "Analista Desarrollador",
            "company": "Health Management Solutions",
            "period": "04/2023 – 11/2023",
            "bullets": [
                "Desarrollé y mantuve aplicaciones web complejas para la gestión de salud utilizando Oracle APEX, modernizando interfaces clínicas y optimizando flujos de trabajo médicos.",
                "Programé lógica backend avanzada en bases de datos mediante PL/SQL, diseñando procedimientos almacenados complejos, funciones y triggers para la manipulación e integridad de datos críticos.",
                "Creé plugins personalizados dentro del ecosistema de Oracle APEX y diseñé vistas estructuradas con reportes dinámicos interactivos para la toma de decisiones del personal de salud.",
                "Integré servicios externos y Web Services para la sincronización de datos e interoperabilidad entre múltiples sistemas hospitalarios.",
                "Resolví incidencias técnicas de nivel crítico en entornos de producción, garantizando la continuidad del servicio mediante diagnósticos precisos."
            ]
        },
        {
            "title": "Soporte Técnico",
            "company": "Centro Universitario Chivilcoy",
            "period": "03/2023 – 11/2023",
            "bullets": [
                "Brindé asistencia técnica a usuarios finales, diagnosticando y resolviendo eficientemente problemas de hardware, configuración de redes y software de sistemas."
            ]
        }
    ],

    "projects": [
        {
            "title": "Desarrollo de Soluciones y Automatizaciones Web (Independiente / Actualidad)",
            "period": "04/2025 – Presente",
            "bullets": [
                "Diseño y construcción de aplicaciones web interactivas y modulares utilizando React para la creación de interfaces de usuario eficientes y dinámicas.",
                "Desarrollo de scripts de automatización, procesamiento de datos y arquitecturas backend utilizando Python, optimizando flujos de trabajo e integración de componentes.",
                "Exploración e implementación práctica de componentes independientes aplicando principios de Clean Code y arquitecturas limpias basadas en componentes."
            ]
        },
        {
            "title": "Desarrollo Web – Proyecto de Tesina",
            "company": "Centro Universitario Chivilcoy",
            "period": "06/2022 – 11/2022",
            "bullets": [
                "Diseñé e implementé de forma integral (frontend y backend) un sistema web de pedidos multi-categoría con gestión dinámica de servicios para la institución.",
                "Stack utilizado: PHP, JavaScript, HTML, CSS, MySQL."
            ]
        }
    ],

    "education": [
        {
            "degree": "Tecnicatura Universitaria en Programación",
            "institution": "Universidad Tecnológica Nacional (UTN) - Regional San Nicolás",
            "year": "03/2021 – 11/2022"
        }
    ],

    "skills": {
        "backend":    ["PHP", "Laravel", "CodeIgniter", "Python", "Node.js", "PL/SQL", "C", "C++"],
        "frontend":   ["JavaScript", "React", "jQuery", "HTML5", "CSS3", "Bootstrap", "WordPress"],
        "databases":  ["MySQL", "SQL", "Oracle APEX", "MongoDB"],
        "tools":      ["Git", "Linux", "REST APIs", "Postman"],
        "languages":  ["Español (Nativo)", "Inglés B1 — lectura técnica fluida, documentación y escritura"]
    }
}