// ==== USUARIOS ====
MERGE (u101:Usuario {id_usuario:'u_101'})
  ON CREATE SET u101.name='Alice',  u101.idioma='en', u101.nivel=4;
MERGE (u102:Usuario {id_usuario:'u_102'})
  ON CREATE SET u102.name='Bob',    u102.idioma='en', u102.nivel=4;
MERGE (u103:Usuario {id_usuario:'u_103'})
  ON CREATE SET u103.name='Carol',  u103.idioma='en', u103.nivel=4;

// ==== SKILLS ====
MERGE (sPS:Skill {id_skill:'past_simple'})
  ON CREATE SET sPS.name='Past Simple', sPS.nombre='Pasado simple';
MERGE (sCMP:Skill {id_skill:'comparatives'})
  ON CREATE SET sCMP.name='Comparatives', sCMP.nombre='Comparativos';

// ==== ETIQUETAS ====
MERGE (tagAudio:Etiqueta {id_etiqueta:'audio'})
  ON CREATE SET tagAudio.name='Audio';
MERGE (tagConv:Etiqueta {id_etiqueta:'conversation'})
  ON CREATE SET tagConv.name='Conversation';

// ==== LECCIONES ====
MERGE (L144:Leccion {id_leccion:'L144'})
  ON CREATE SET L144.name='L144 · Past Simple drill',
                L144.idioma='en', L144.nivel=4,
                L144.tema='Past Simple drill',
                L144.descripcion='Ejercicios de pasado simple.';
MERGE (L160:Leccion {id_leccion:'L160'})
  ON CREATE SET L160.name='L160 · Past Simple stories',
                L160.idioma='en', L160.nivel=4,
                L160.tema='Past Simple stories',
                L160.descripcion='Historias en pasado simple.';
MERGE (L150:Leccion {id_leccion:'L150'})
  ON CREATE SET L150.name='L150 · Comparatives practice',
                L150.idioma='en', L150.nivel=4,
                L150.tema='Comparatives practice',
                L150.descripcion='Práctica de comparativos.';

// ==== EJERCICIOS ====
MERGE (E1:Ejercicio {id_ejercicio:'E1'})
  ON CREATE SET E1.name='Exercise E1', E1.tipo='gap_fill';
MERGE (E2:Ejercicio {id_ejercicio:'E2'})
  ON CREATE SET E2.name='Exercise E2', E2.tipo='listening';
MERGE (E3:Ejercicio {id_ejercicio:'E3'})
  ON CREATE SET E3.name='Exercise E3', E3.tipo='multiple_choice';
MERGE (E4:Ejercicio {id_ejercicio:'E4'})
  ON CREATE SET E4.name='Exercise E4', E4.tipo='listening';
MERGE (E5:Ejercicio {id_ejercicio:'E5'})
  ON CREATE SET E5.name='Exercise E5', E5.tipo='writing';