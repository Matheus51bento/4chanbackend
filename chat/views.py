from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.utils import extend_schema

class WebSocketSchemaView(SpectacularAPIView):
    
    @extend_schema(
        summary="API Schema with WebSocket Endpoints",
        description="This schema includes documentation for WebSocket endpoints.",
        responses={200: 'application/vnd.oai.openapi+json'}
    )
    def get(self, request, *args, **kwargs):
        schema = super().get(request, *args, **kwargs)
        
        # Add WebSocket documentation
        schema.data['paths']['/ws/chat/{room_name}/'] = {
            'get': {
                'summary': 'WebSocket Connection for Chat',
                'description': """
                **WebSocket API for Chat**

                **Events:**
                - `chat_message`: Receive a chat message.
                - `joined_chat`: Notify when a user joins the chat.
                - `left_chat`: Notify when a user leaves the chat.

                **Payload:**
                - `event`: The event name.
                - `data`: The event data.
                """,
                'parameters': [
                    {
                        'name': 'room_name',
                        'in': 'path',
                        'required': True,
                        'schema': {
                            'type': 'string'
                        },
                        'description': 'Name of the chat room'
                    }
                ],
                'responses': {
                    '101': {
                        'description': 'Switching Protocols',
                    }
                }
            }
        }
        
        schema.data['paths']['/ws/chatlist/'] = {
            'get': {
                'summary': 'WebSocket Connection for Chat List',
                'description': """
                **WebSocket API for Chat List**

                **Events:**
                - `chat_created`: Notify when a new chat room is created.

                **Payload:**
                - `room_name`: The name of the chat room.
                """,
                'responses': {
                    '101': {
                        'description': 'Switching Protocols',
                    }
                }
            }
        }
        
        return schema
