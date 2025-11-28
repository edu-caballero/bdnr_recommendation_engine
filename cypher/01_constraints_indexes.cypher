// PK / unicidad
CREATE CONSTRAINT usuario_pk   IF NOT EXISTS FOR (u:Usuario)   REQUIRE u.id_usuario   IS UNIQUE;
CREATE CONSTRAINT leccion_pk   IF NOT EXISTS FOR (l:Leccion)   REQUIRE l.id_leccion   IS UNIQUE;
CREATE CONSTRAINT ejercicio_pk IF NOT EXISTS FOR (e:Ejercicio) REQUIRE e.id_ejercicio IS UNIQUE;
CREATE CONSTRAINT skill_pk     IF NOT EXISTS FOR (s:Skill)     REQUIRE s.id_skill     IS UNIQUE;
CREATE CONSTRAINT etiqueta_pk  IF NOT EXISTS FOR (t:Etiqueta)  REQUIRE t.id_etiqueta  IS UNIQUE;

// Índices típicos para filtros
CREATE INDEX leccion_idioma_nivel IF NOT EXISTS FOR (l:Leccion) ON (l.idioma, l.nivel);
CREATE INDEX usuario_idioma_nivel IF NOT EXISTS FOR (u:Usuario) ON (u.idioma, u.nivel);

// (Opcional) Full-text si vas a buscar por texto en lecciones
CREATE FULLTEXT INDEX leccion_texto IF NOT EXISTS FOR (l:Leccion) ON EACH [l.tema, l.descripcion];
