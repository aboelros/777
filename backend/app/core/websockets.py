from typing import Dict, List
from fastapi import WebSocket, status
from uuid import UUID
import structlog

logger = structlog.get_logger(__name__)

class WebSocketManager:
    """Manages active WebSocket connections grouped by project_id."""
    
    def __init__(self):
        # project_id -> list of WebSockets
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: UUID):
        """Accept connection and add to project group."""
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)
        logger.info("WebSocket connected", project_id=str(project_id), total_connections=len(self.active_connections[project_id]))

    def disconnect(self, websocket: WebSocket, project_id: UUID):
        """Remove connection from project group."""
        if project_id in self.active_connections:
            if websocket in self.active_connections[project_id]:
                self.active_connections[project_id].remove(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info("WebSocket disconnected", project_id=str(project_id))

    async def broadcast_to_project(self, project_id: UUID, message: dict):
        """Send message to all connections in a project group."""
        if project_id in self.active_connections:
            logger.debug("Broadcasting to project", project_id=str(project_id), type=message.get("type"))
            disconnected_sockets = []
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning("Failed to send message over WebSocket", error=str(e))
                    disconnected_sockets.append(connection)
            
            # Clean up stale connections
            for socket in disconnected_sockets:
                self.disconnect(socket, project_id)

manager = WebSocketManager()
