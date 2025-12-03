# Motor de recomendaciones Duolingo (Neo4j)

Este proyecto implementa un **subsistema de recomendaciones** inspirado en Duolingo, usando:

- **FastAPI** como API REST.
- **Neo4j** como base de datos de grafos.
- Integraciones simuladas con:
  - subsistema de lecciones (BD relacional),
  - subsistema de perfiles de usuario (Mongo),
  - y un posible servicio de similitud vectorial (diseñado como extensión futura).

El objetivo es **recibir eventos de uso**, mantener un **grafo de usuarios, lecciones, skills y preferencias**, y exponer un endpoint para obtener **recomendaciones de lecciones/ejercicios**.

---

## Requisitos

- Python 3.10+  
- Neo4j (Desktop o Server) instalado y accesible
- `pip` y entornos virtuales (`venv`) disponibles

---

## Instalación y configuración

### 1. Clonar el proyecto

```bash
git clone <URL_DEL_REPO>
cd bdnr_recommendation_engine
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # en macOS / Linux
# .venv\Scripts\activate   # en Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo .env en la raíz del proyecto con algo similar a:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tu_password
NEO4J_DATABASE=neo4j
INITIALIZE_GRAPH_ON_STARTUP=true
```

Asegurate de que la configuración coincide con tu instancia de Neo4j (host, puerto, usuario, base).

### 5. Inicializar y levantar la API

El archivo run.py arranca la aplicación (FastAPI + Uvicorn):
```bash
python run.py
```

Por defecto la API quedará disponible en: http://localhost:8000

## Endpoints principales

### Health check

Verificar que la API está levantada:

```
curl http://localhost:8000/health
```

Respuesta esperada:

```
{"status": "ok"}
```

### Pruebas rápidas
#### 1. Sincronizar contenido (lecciones, skills, etiquetas, ejercicios)

Este endpoint simula el subsistema de lecciones cargando el catálogo en el grafo.

```
curl -X POST "http://localhost:8000/admin/content-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "lessons": [
      {
        "lesson_id": "L160",
        "lesson_name": "Historias en pasado simple",
        "skills": ["past_simple", "pronouns"],
        "tags": ["stories", "audio"],
        "exercises": ["E1", "E2"]
      },
      {
        "lesson_id": "L200",
        "lesson_name": "Introducción al futuro simple",
        "skills": ["future_simple"],
        "tags": ["grammar"],
        "exercises": ["E3"]
      }
    ]
  }'
```

Esto crea (si no existen): Nodos Leccion, Skill, Etiqueta, Ejercicio

Relaciones:

```
(:Leccion)-[:REFUERZA_SKILL]->(:Skill)

(:Leccion)-[:TIENE_ETIQUETA]->(:Etiqueta)

(:Leccion)-[:TIENE_EJERCICIO]->(:Ejercicio)
```

#### 2. Registrar un evento de lección completada

Simula que un usuario completa una lección con ciertos errores por skill.
El servicio consulta un perfil de usuario mock y actualiza el grafo.

```
curl -X POST "http://localhost:8000/events/lesson-completed" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "u_101",
    "lesson_id": "L160",
    "correct": 8,
    "incorrect": 2,
    "duration_seconds": 320,
    "completed_at": "2025-11-28T15:30:00Z",
    "skills_stats": [
      { "skill_id": "past_simple", "errors": 3, "attempts": 5 },
      { "skill_id": "pronouns",    "errors": 1, "attempts": 4 }
    ]
  }'
```

Este endpoint actualiza en Neo4j:

```
Nodo (:Usuario {id_usuario: "u_101"}) con datos de perfil (mock).

Relación (:Usuario)-[:COMPLETO_LECCION]->(:Leccion).

Relaciones (:Usuario)-[:FALLA_EN_SKILL]->(:Skill) con tasa de error.

Relaciones (:Usuario)-[:PREFIERE_ETIQUETA]->(:Etiqueta) a partir del perfil.
```

#### 3. Cargar similitudes entre usuarios (admin)

Permite registrar relaciones SIMILAR_A para luego usar la estrategia de “usuarios similares”.

```
curl -X POST "http://localhost:8000/admin/user-similarity-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {
        "user_id": "u_101",
        "similar_users": [
          { "id": "u_202", "score": 0.87 },
          { "id": "u_303", "score": 0.75 }
        ]
      }
    ]
  }'
```

Esto crea en Neo4j:
```
(u_101)-[:SIMILAR_A {score: 0.87}]->(u_202)
(u_101)-[:SIMILAR_A {score: 0.75}]->(u_303)
```

#### 4. Obtener recomendaciones para un usuario

Endpoint principal del subsistema de recomendaciones.
```
curl "http://localhost:8000/users/u_101/recommendations?strategy=weak-skills&limit=5"
```

Estrategias disponibles (parámetro strategy):

- **weak-skills**: Recomendaciones basadas en skills donde el usuario tiene mayor tasa de error.

- **similar-users**: Usa relaciones SIMILAR_A para recomendar lecciones que completaron usuarios similares.

- **skills-and-preferences**: Combina skills débiles (FALLA_EN_SKILL) con preferencias de contenido (PREFIERE_ETIQUETA).

Ejemplo de respuesta (simplificada):

```
{
  "user_id": "u_101",
  "strategy": "weak-skills",
  "items": [
    {
      "lesson_id": "L160",
      "lesson_name": "Historias en pasado simple",
      "exercise_ids": ["E1", "E2"],
      "reason": "refuerzo_de_skill",
      "skills": ["past_simple"],
      "tags": ["stories", "audio"],
      "score": 0.6,
      "explanation": "Refuerza skills débiles (past_simple) con tasa de error aproximada 0.60."
    }
  ]
}
```