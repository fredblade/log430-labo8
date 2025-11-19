"""
Handler: Payment Created
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import requests
from typing import Dict, Any
import config
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer

class PaymentCreatedHandler(EventHandler):
    """Handles PaymentCreated events"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        """Get event type name"""
        return "PaymentCreated"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        """Execute every time the event is published"""
        # TODO: Consultez le diagramme de machine à états pour savoir quelle opération effectuer dans cette méthode. Mettez votre commande à jour avec le nouveau payment_id.
        # N'oubliez pas d'enregistrer le payment_link dans votre commande
        event_data["payment_link"] = "todo-add-payment-link-here"

        try:
            self.logger.debug(f"Création du paiement pour order_id={event_data.get('order_id')}, user_id={event_data.get('user_id')}, total_amount={event_data.get('total_amount')}")
            response = requests.post(f'{config.API_GATEWAY_URL}/payments-api/payments',
                json={
                    "user_id": event_data.get("user_id"),
                    "order_id": event_data.get("order_id"),
                    "total_amount": event_data.get("total_amount")
                },
                headers={'Content-Type': 'application/json'}
            )
            
            payment_response = response.json()
            self.logger.debug("Réponse de la création du paiement : " + str(payment_response))
            
            # Extract payment_id from response
            payment_id = payment_response.get('payment_id')
            if payment_id:
                event_data["payment_id"] = payment_id
                event_data["payment_link"] = f"http://api-gateway:8080/payments-api/payments/process/{payment_id}"
            else:
                event_data["payment_link"] = str(payment_response)
            
            # Si l'operation a réussi, déclenchez SagaCompleted.
            event_data['event'] = "SagaCompleted"
            self.logger.debug(f"payment_id={event_data.get('payment_id')}, payment_link={event_data['payment_link']}")
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)

        except Exception as e:
            # TODO: Si l'operation a échoué, déclenchez l'événement adéquat selon le diagramme.
            event_data['error'] = str(e)
            self.logger.error(f"Erreur lors de la création du paiement: {str(e)}")
            event_data['event'] = "PaymentCreationFailed"
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)


