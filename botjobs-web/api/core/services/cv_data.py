"""
cv_data.py
Perfil base de Timoteo Pereyra.
La IA adapta este perfil a cada vacante sin inventar nada nuevo.
"""

PROFILE = {
    "name": "Timoteo Pereyra",
    "headline": "Desarrollador Full Stack · PHP · Laravel · JavaScript",
    "email": "timopereyra@gmail.com",
    "phone": "(+54) 2345 425347",
    "location": "Capital Federal, Buenos Aires",
    "linkedin": "linkedin.com/in/timoteo-pereyra",

    "summary": (
        "Desarrollador Full Stack con 3+ años de experiencia en el diseño y desarrollo "
        "de aplicaciones web orientadas a gestión empresarial y salud. Especializado en "
        "PHP, Laravel, CodeIgniter y JavaScript, con capacidad para trabajar de forma "
        "autónoma en múltiples sistemas simultáneos. Busco un rol de Desarrollador Full Stack "
        "o Backend donde pueda aplicar mis habilidades en arquitectura de software y buenas "
        "prácticas de desarrollo."
    ),

    "experience": [
        {
            "title": "Analista Desarrollador",
            "company": "Uakika",
            "period": "11/2023 – 03/2025",
            "bullets": [
                "Desarrollé y mantuve dos sistemas web en producción en paralelo: uno en Laravel + HTML/CSS y otro en CodeIgniter + jQuery, atendiendo requerimientos simultáneos de distintas áreas del negocio.",
                "Implementé nuevas funcionalidades end-to-end en ambos sistemas, desde el relevamiento de requerimientos hasta el despliegue en producción.",
                "Optimicé consultas SQL críticas mejorando el tiempo de respuesta de pantallas de alta carga.",
                "Colaboré en la planificación técnica de sprints y en la documentación de decisiones de arquitectura.",
            ]
        },
        {
            "title": "Analista Desarrollador",
            "company": "Health Management Solutions",
            "period": "04/2023 – 11/2023",
            "bullets": [
                "Desarrollé y mantuve aplicaciones web para gestión de salud, integrando módulos de seguimiento y reportes.",
                "Resolví incidencias técnicas en producción con seguimiento hasta su cierre.",
                "Integré servicios externos para sincronización de datos entre sistemas de salud.",
            ]
        },
        {
            "title": "Soporte Técnico",
            "company": "Centro Universitario Chivilcoy",
            "period": "03/2023 – 11/2023",
            "bullets": [
                "Brindé asistencia técnica a usuarios, diagnosticando y resolviendo problemas de hardware y software.",
            ]
        },
        {
            "title": "Desarrollador – Proyecto de Tesina",
            "company": "Centro Universitario Chivilcoy",
            "period": "06/2022 – 11/2022",
            "bullets": [
                "Diseñé e implementé de forma integral (frontend y backend) un sistema web de pedidos multi-categoría con gestión dinámica de servicios.",
                "Stack utilizado: PHP, JavaScript, HTML, CSS, MySQL.",
            ]
        },
    ],

    "education": [
        {
            "degree": "Tecnicatura Universitaria en Programación",
            "institution": "UTN Regional San Nicolás",
            "year": "03/2021 – 11/2022",
        }
    ],

    "skills": {
        "backend":    ["PHP", "Laravel", "CodeIgniter", "Node.js", "Python", "C", "C++"],
        "frontend":   ["JavaScript", "jQuery", "HTML", "CSS", "Bootstrap"],
        "databases":  ["SQL", "PL-SQL", "Oracle Apex", "MongoDB"],
        "tools":      ["Git", "Linux", "REST APIs"],
        "languages":  ["Español (Nativo)", "Inglés B1 — lectura técnica fluida"],
    }
}
