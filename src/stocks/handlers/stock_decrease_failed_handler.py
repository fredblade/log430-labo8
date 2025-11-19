"""
Handler: Stock Decrease Failed
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import config
from db import get_sqlalchemy_session
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer
from stocks.commands.write_stock import check_in_items_to_stock


class StockDecreaseFailedHandler(EventHandler):
    """Handles StockDecreaseFailed events"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        """Get event type name"""
        return "StockDecreaseFailed"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        """Execute every time the event is published"""
        # TODO: Consultez le diagramme de machine à états pour savoir quelle opération effectuer dans cette méthode. 

        try:
            session = get_sqlalchemy_session()
            check_in_items_to_stock(session, event_data['order_items'])
            session.commit()
            # Si l'operation a réussi, déclenchez OrderCancelled.
            event_data['event'] = "OrderCancelled"
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)
        except Exception as e:
            # TODO: Si l'operation a échoué, continuez la compensation des étapes précedentes.

            # Aucune action spécifique n'est définie dans le diagramme pour cette situation.
            event_data['error'] = str(e)
  
