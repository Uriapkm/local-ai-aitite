"""
Sistema de Memoria - Abuelo IA
Almacenamiento persistente de conversaciones y preferencias usando SQLite
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class MemoryManager:
    """
    Gestiona la memoria persistente del agente:
    - Historial de conversaciones
    - Preferencias del usuario
    - Contexto de sesiones anteriores
    """
    
    def __init__(self, db_path: str = "./data/abuelo_memory.db"):
        """
        Inicializa el gestor de memoria
        
        Args:
            db_path: Ruta al archivo SQLite
        """
        self.db_path = db_path
        
        # Asegurar directorio existe
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar base de datos
        self._init_database()
        
        print(f"💾 MemoryManager inicializado:")
        print(f"   - DB: {db_path}")
    
    def _init_database(self):
        """Inicializa las tablas de la base de datos"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Tabla: Conversaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_input TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    action_taken TEXT,
                    context JSON
                )
            """)
            
            # Tabla: Preferencias del usuario
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla: Estadísticas de uso
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    interaction_count INTEGER DEFAULT 0,
                    youtube_searches INTEGER DEFAULT 0,
                    ir_commands INTEGER DEFAULT 0,
                    UNIQUE(date)
                )
            """)
            
            # Índices para búsquedas rápidas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_preferences_key 
                ON preferences(key)
            """)
            
            conn.commit()
            print("   ✅ Base de datos inicializada")
            
        except Exception as e:
            print(f"❌ Error inicializando DB: {e}")
            raise
        finally:
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        return conn
    
    # === CONVERSACIONES ===
    
    def save_conversation(self, 
                         user_input: str, 
                         assistant_response: str,
                         action_taken: Optional[str] = None,
                         context: Optional[Dict[str, Any]] = None):
        """
        Guarda una interacción en el historial
        
        Args:
            user_input: Texto del usuario
            assistant_response: Respuesta del asistente
            action_taken: Acción ejecutada (IR_SEND, YOUTUBE_SEARCH, etc.)
            context: Contexto adicional (JSON serializable)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            context_json = json.dumps(context) if context else None
            
            cursor.execute("""
                INSERT INTO conversations (user_input, assistant_response, action_taken, context)
                VALUES (?, ?, ?, ?)
            """, (user_input, assistant_response, action_taken, context_json))
            
            conn.commit()
            print(f"   💬 Conversación guardada (ID: {cursor.lastrowid})")
            
        except Exception as e:
            print(f"❌ Error guardando conversación: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_recent_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Obtiene las últimas conversaciones
        
        Args:
            limit: Número máximo de conversaciones a retornar
            
        Returns:
            Lista de dicts con keys: timestamp, user_input, assistant_response, action_taken
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT timestamp, user_input, assistant_response, action_taken, context
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conversations = []
            
            for row in rows:
                conv = {
                    "timestamp": row["timestamp"],
                    "user_input": row["user_input"],
                    "assistant_response": row["assistant_response"],
                    "action_taken": row["action_taken"],
                    "context": json.loads(row["context"]) if row["context"] else None
                }
                conversations.append(conv)
            
            # Retornar en orden cronológico (más antiguo primero)
            return list(reversed(conversations))
            
        except Exception as e:
            print(f"❌ Error obteniendo conversaciones: {e}")
            return []
        finally:
            conn.close()
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca conversaciones que contengan un término
        
        Args:
            query: Término de búsqueda
            limit: Máximo de resultados
            
        Returns:
            Lista de conversaciones matching
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            search_pattern = f"%{query}%"
            
            cursor.execute("""
                SELECT timestamp, user_input, assistant_response, action_taken
                FROM conversations
                WHERE user_input LIKE ? OR assistant_response LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (search_pattern, search_pattern, limit))
            
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                results.append({
                    "timestamp": row["timestamp"],
                    "user_input": row["user_input"],
                    "assistant_response": row["assistant_response"],
                    "action_taken": row["action_taken"]
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error buscando conversaciones: {e}")
            return []
        finally:
            conn.close()
    
    def clear_conversations(self, older_than_days: Optional[int] = None):
        """
        Limpia el historial de conversaciones
        
        Args:
            older_than_days: Si se especifica, solo borra conversaciones más antiguas
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if older_than_days:
                cursor.execute("""
                    DELETE FROM conversations
                    WHERE timestamp < datetime('now', ?)
                """, (f'-{older_than_days} days',))
                print(f"   🧹 Conversaciones older than {older_than_days} days borradas")
            else:
                cursor.execute("DELETE FROM conversations")
                print("   🧹 Todas las conversaciones borradas")
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Error limpiando conversaciones: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    # === PREFERENCIAS ===
    
    def save_preference(self, key: str, value: Any):
        """
        Guarda una preferencia del usuario
        
        Args:
            key: Clave de la preferencia
            value: Valor (cualquier tipo serializable a JSON)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            value_json = json.dumps(value)
            
            cursor.execute("""
                INSERT OR REPLACE INTO preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value_json))
            
            conn.commit()
            print(f"   ⚙️ Preferencia guardada: {key} = {value}")
            
        except Exception as e:
            print(f"❌ Error guardando preferencia: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Obtiene una preferencia guardada
        
        Args:
            key: Clave de la preferencia
            default: Valor por defecto si no existe
            
        Returns:
            Valor de la preferencia o default
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT value FROM preferences WHERE key = ?
            """, (key,))
            
            row = cursor.fetchone()
            
            if row:
                return json.loads(row["value"])
            else:
                return default
                
        except Exception as e:
            print(f"❌ Error obteniendo preferencia: {e}")
            return default
        finally:
            conn.close()
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """
        Obtiene todas las preferencias guardadas
        
        Returns:
            Dict con todas las preferencias
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT key, value FROM preferences")
            
            prefs = {}
            for row in cursor.fetchall():
                prefs[row["key"]] = json.loads(row["value"])
            
            return prefs
            
        except Exception as e:
            print(f"❌ Error obteniendo preferencias: {e}")
            return {}
        finally:
            conn.close()
    
    # === ESTADÍSTICAS ===
    
    def increment_interaction_count(self, date: Optional[str] = None):
        """Incrementa contador de interacciones del día"""
        self._increment_stat("interaction_count", date)
    
    def increment_youtube_searches(self, date: Optional[str] = None):
        """Incrementa contador de búsquedas YouTube del día"""
        self._increment_stat("youtube_searches", date)
    
    def increment_ir_commands(self, date: Optional[str] = None):
        """Incrementa contador de comandos IR del día"""
        self._increment_stat("ir_commands", date)
    
    def _increment_stat(self, stat_name: str, date: Optional[str] = None):
        """Incrementa una estadística específica"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            date_str = date or datetime.now().strftime("%Y-%m-%d")
            
            # Insertar si no existe
            cursor.execute("""
                INSERT OR IGNORE INTO usage_stats (date, interaction_count, youtube_searches, ir_commands)
                VALUES (?, 0, 0, 0)
            """, (date_str,))
            
            # Incrementar
            cursor.execute(f"""
                UPDATE usage_stats
                SET {stat_name} = {stat_name} + 1
                WHERE date = ?
            """, (date_str,))
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Error incrementando estadística: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_usage_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Obtiene estadísticas de uso de los últimos N días
        
        Args:
            days: Número de días hacia atrás
            
        Returns:
            Lista de stats diarios
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT date, interaction_count, youtube_searches, ir_commands
                FROM usage_stats
                WHERE date >= date('now', ?)
                ORDER BY date DESC
            """, (f'-{days} days',))
            
            stats = []
            for row in cursor.fetchall():
                stats.append({
                    "date": row["date"],
                    "interaction_count": row["interaction_count"],
                    "youtube_searches": row["youtube_searches"],
                    "ir_commands": row["ir_commands"]
                })
            
            return stats
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return []
        finally:
            conn.close()
    
    # === UTILIDADES ===
    
    def get_conversation_context_for_llm(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """
        Obtiene contexto formateado para enviar al LLM
        
        Args:
            max_messages: Número máximo de mensajes a incluir
            
        Returns:
            Lista de dicts con 'role' y 'content' para Ollama
        """
        conversations = self.get_recent_conversations(limit=max_messages)
        
        context = []
        for conv in conversations:
            context.append({
                "role": "user",
                "content": conv["user_input"]
            })
            context.append({
                "role": "assistant",
                "content": conv["assistant_response"]
            })
        
        return context
    
    def export_data(self, output_path: str) -> bool:
        """
        Exporta todos los datos a JSON
        
        Args:
            output_path: Ruta al archivo de salida
            
        Returns:
            True si éxito
        """
        try:
            data = {
                "conversations": self.get_recent_conversations(limit=1000),
                "preferences": self.get_all_preferences(),
                "usage_stats": self.get_usage_stats(days=365),
                "exported_at": datetime.now().isoformat()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"   📦 Datos exportados a: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando datos: {e}")
            return False
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Obtiene resumen estadístico general"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Total conversaciones
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_convos = cursor.fetchone()[0]
            
            # Total días con actividad
            cursor.execute("SELECT COUNT(DISTINCT date) FROM usage_stats")
            active_days = cursor.fetchone()[0]
            
            # Stats últimos 7 días
            recent_stats = self.get_usage_stats(days=7)
            total_interactions = sum(s["interaction_count"] for s in recent_stats)
            
            return {
                "total_conversations": total_convos,
                "active_days": active_days,
                "interactions_last_7_days": total_interactions,
                "preferences_count": len(self.get_all_preferences())
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo resumen: {e}")
            return {}
        finally:
            conn.close()


# Punto de entrada para testing
if __name__ == "__main__":
    print("🧪 Testing MemoryManager...\n")
    
    memory = MemoryManager("./data/test_memory.db")
    
    # Guardar conversaciones de prueba
    memory.save_conversation(
        user_input="¿Cómo se enciende la TV?",
        assistant_response="Presiona el botón rojo del control remoto.",
        action_taken="IR_SEND"
    )
    
    memory.save_conversation(
        user_input="Busca videos de música clásica",
        assistant_response="Claro, buscando música clásica en YouTube.",
        action_taken="YOUTUBE_SEARCH"
    )
    
    # Guardar preferencias
    memory.save_preference("volumen_preferido", 15)
    memory.save_preference("canal_favorito", "La 1")
    memory.save_preference("youtube_quality", "1080p")
    
    # Incrementar stats
    memory.increment_interaction_count()
    memory.increment_ir_commands()
    
    # Leer datos
    print("\n📜 Conversaciones recientes:")
    for conv in memory.get_recent_conversations(limit=5):
        print(f"   - {conv['user_input']} → {conv['action_taken']}")
    
    print("\n⚙️ Preferencias:")
    for key, value in memory.get_all_preferences().items():
        print(f"   - {key}: {value}")
    
    print("\n📊 Estadísticas:")
    summary = memory.get_stats_summary()
    for key, value in summary.items():
        print(f"   - {key}: {value}")
    
    print("\n✅ Test completado")
