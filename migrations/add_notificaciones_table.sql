-- Migración para añadir la tabla de notificaciones

CREATE TABLE notificaciones (
  id SERIAL PRIMARY KEY,
  usuario_id VARCHAR(100) NOT NULL,
  titulo VARCHAR(255) NOT NULL,
  mensaje TEXT NOT NULL,
  tipo VARCHAR(50) DEFAULT 'info',
  fecha_creacion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  leida BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (usuario_id) REFERENCES Usuarios(usuario)
);

-- Índice para mejorar el rendimiento de las consultas por usuario
CREATE INDEX idx_notificaciones_usuario ON notificaciones(usuario_id);

-- Índice para mejorar el rendimiento de las consultas por estado de lectura
CREATE INDEX idx_notificaciones_leida ON notificaciones(leida);