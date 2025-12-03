// Perfil de u_101: skills débiles + preferencias
MATCH (u101:Usuario {id_usuario:'u_101'}), (sPS:Skill {id_skill:'past_simple'}), (sCMP:Skill {id_skill:'comparatives'}),
      (tagAudio:Etiqueta {id_etiqueta:'audio'})
MERGE (u101)-[:FALLA_EN_SKILL {errores:7, tasa_error:0.62, ventana:'30d'}]->(sPS)
MERGE (u101)-[:FALLA_EN_SKILL {errores:3, tasa_error:0.30, ventana:'30d'}]->(sCMP)
MERGE (u101)-[:PREFIERE_ETIQUETA {peso:0.8, fuente:'explícita', updated_at:datetime()}]->(tagAudio);

// Perfil de u_102 y u_103
MATCH (u102:Usuario {id_usuario:'u_102'}), (u103:Usuario {id_usuario:'u_103'}),
      (sCMP:Skill {id_skill:'comparatives'}), (tagConv:Etiqueta {id_etiqueta:'conversation'})
MERGE (u102)-[:PREFIERE_ETIQUETA {peso:0.6, fuente:'implícita', updated_at:datetime()}]->(tagConv)
MERGE (u103)-[:FALLA_EN_SKILL {errores:2, tasa_error:0.25, ventana:'30d'}]->(sCMP);

// Lección -> Skill (refuerzos)
MATCH (L144:Leccion {id_leccion:'L144'}), (L160:Leccion {id_leccion:'L160'}), (L150:Leccion {id_leccion:'L150'}),
      (sPS:Skill {id_skill:'past_simple'}), (sCMP:Skill {id_skill:'comparatives'})
MERGE (L144)-[:REFUERZA_SKILL {intensidad:8}]->(sPS)
MERGE (L160)-[:REFUERZA_SKILL {intensidad:9}]->(sPS)
MERGE (L150)-[:REFUERZA_SKILL {intensidad:7}]->(sCMP);

// Lección -> Etiqueta
MATCH (L144:Leccion {id_leccion:'L144'}), (L160:Leccion {id_leccion:'L160'}), (L150:Leccion {id_leccion:'L150'}),
      (tagAudio:Etiqueta {id_etiqueta:'audio'}), (tagConv:Etiqueta {id_etiqueta:'conversation'})
MERGE (L144)-[:TIENE_ETIQUETA]->(tagAudio)
MERGE (L160)-[:TIENE_ETIQUETA]->(tagConv)
MERGE (L150)-[:TIENE_ETIQUETA]->(tagConv);

// Lección -> Ejercicios
MATCH (L144:Leccion {id_leccion:'L144'}), (L160:Leccion {id_leccion:'L160'}), (L150:Leccion {id_leccion:'L150'}),
      (E1:Ejercicio {id_ejercicio:'E1'}), (E2:Ejercicio {id_ejercicio:'E2'}),
      (E3:Ejercicio {id_ejercicio:'E3'}), (E4:Ejercicio {id_ejercicio:'E4'}), (E5:Ejercicio {id_ejercicio:'E5'})
MERGE (L144)-[:TIENE_EJERCICIO {orden:1, dificultad:3}]->(E1)
MERGE (L144)-[:TIENE_EJERCICIO {orden:2, dificultad:3}]->(E2)
MERGE (L160)-[:TIENE_EJERCICIO {orden:1, dificultad:3}]->(E4)
MERGE (L160)-[:TIENE_EJERCICIO {orden:2, dificultad:4}]->(E5)
MERGE (L150)-[:TIENE_EJERCICIO {orden:1, dificultad:2}]->(E3);

// Eventos
MATCH (u101:Usuario {id_usuario:'u_101'}), (u102:Usuario {id_usuario:'u_102'}), (u103:Usuario {id_usuario:'u_103'}),
      (L144:Leccion {id_leccion:'L144'}), (L160:Leccion {id_leccion:'L160'}), (L150:Leccion {id_leccion:'L150'})
MERGE (u101)-[:COMPLETO_LECCION {fecha: datetime('2025-11-18T10:00:00Z'), puntaje:60, intentos:2, tiempo_seg:280}]->(L150) // ya hizo L150
MERGE (u102)-[:COMPLETO_LECCION {fecha: datetime('2025-11-19T09:50:00Z'), puntaje:85, intentos:1, tiempo_seg:260}]->(L144)
MERGE (u102)-[:COMPLETO_LECCION {fecha: datetime('2025-11-20T09:50:00Z'), puntaje:88, intentos:1, tiempo_seg:255}]->(L160)
MERGE (u103)-[:COMPLETO_LECCION {fecha: datetime('2025-11-17T08:30:00Z'), puntaje:82, intentos:1, tiempo_seg:240}]->(L150);

// Similaridad
MATCH (u101:Usuario {id_usuario:'u_101'}), (u102:Usuario {id_usuario:'u_102'})
MERGE (u101)-[:SIMILAR_A {score:0.92, metodo:'skills', updated_at: datetime()}]->(u102);
