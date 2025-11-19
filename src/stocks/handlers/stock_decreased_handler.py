"""
Handler: Stock Decreased
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import config
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer
from db import get_sqlalchemy_session
from payments.models.outbox import Outbox
from payments.outbox_processor import OutboxProcessor
from stocks.commands.write_stock import check_out_items_from_stock


class StockDecreasedHandler(EventHandler):
    """Handles StockDecreased events"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        """Get event type name"""
        return "StockDecreased"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        """Execute every time the event is published"""
        '''
        TODO: Consultez le diagramme de machine à états pour savoir quelle opération 
        effectuer dans cette méthode. 
        
        **Conseil** : si vous préférez, avant de travailler sur l'implémentation event-driven, 
        effectuez un appel synchrone (requête HTTP) à l'API Payments, attendez le résultat, puis 
        continuez la saga. L'approche synchrone peut être plus facile à comprendre dans un premier temps.
          
        En revanche, dans une implémentation 100% event-driven, ce StockDecreasedHandler se trouvera 
        dans l'API Payments et non dans Store Manager, car c'est l'API Payments qui doit 
        être notifiée de la mise à jour du stock afin de générer une transaction de paiement.
        '''
        session = get_sqlalchemy_session()
        try: 
            new_outbox_item = Outbox(order_id=event_data['order_id'], 
                                    user_id=event_data['user_id'], 
                                    total_amount=event_data['total_amount'],
                                    order_items=event_data['order_items'])
            session.add(new_outbox_item)
            session.flush() 
            session.commit()
            OutboxProcessor().run(new_outbox_item)
        except Exception as e:
            session.rollback()
            self.logger.debug("La création d'une transaction de paiement a échoué : " + str(e))
            event_data['event'] = "PaymentCreationFailed"
            event_data['error'] = str(e)
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)
        finally:
            session.close()

