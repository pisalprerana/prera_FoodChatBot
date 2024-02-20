from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper


app= FastAPI()

inprogress_orders= {}

@app.post("/")
async def handle_request(request: Request):
    payload= await request.json()

    intent= payload['queryResult']['intent']['displayName']
    parameters= payload['queryResult']['parameters']
    output_contexts=payload['queryResult']['outputContexts']
    session_id= generic_helper.extract_session_id(output_contexts[0]['name'])

    intent_handler_dict= {
        'order.add-context-ongoing.order': add_to_order,
        'order.remove-context-ongoing.order': remove_from_order,
        'order.complete - context: ongoing.order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }

    return intent_handler_dict[intent](parameters,session_id)


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I am having trouble finding your order. Sorry"

        })
    current_order= inprogress_orders[session_id]
    food_items= parameters["food-item"]

    removed_items=[]
    no_such_items= []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items)>0:
        fulfillment_text= f"Removed {",".join(removed_items)} from your order"

    if len(no_such_items)>0:
        fulfillment_text= f'Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys())==0:
        fulfillment_text +="Your order is empty"

    else:
        generic_helper.get_str_from_food_dict(current_order)

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
def add_to_order(parameters: dict, session_id: str):
    food_items= parameters["food-item"]
    quantities= parameters["number"]

    if len(food_items)!= len(quantities):
        fulfillment_text= "Sorry I didn't understand. Can you please specify food items and quantities"
    else:
        new_food_dict= dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict= inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id]= current_food_dict
        else:
            inprogress_orders[session_id]= new_food_dict


        order_str= generic_helper.get_str_from_food_dict(inprogress_orders[session_id])

        fulfillment_text= f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
def complete_order(parameters: dict, session_id: str, inprogress_orders):
    if session_id not in inprogress_orders:
        fulfillment_text= "I'm having trouble finding your order. Sorry! Can you please place a new order?"
    else:
        order= inprogress_orders=[session_id]
        number= save_to_db(order)

        if number== -1:
            fulfillment_text= "Sorry, i could not process your order due to a backend error." \
                               "Please place a new order again"
        else:
            order_total= db_helper.get_total_order_price(number)
            fulfillment_text= f"Awesome. We have placed your order." \
                              f"Here is your order id # {number}" \
                              f"Your order total is {order_total} which you can pay at the time of delivery"

        del inprogress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
def save_to_db(order: dict):
    #order= {"pizzas":2, "chole": 1}
    next_number= db_helper.get_next_number()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_items(
            food_item,
            quantity,
            next_number
        )

        if rcode== -1:
            return -1

    db_helper.insert_order_tracking(next_number, "in progress")

    return next_number



def track_order(parameters: dict, session_id: str):
    number= int(parameters['number'])
    order_status = db_helper.get_order_status(number)

    if order_status:
        fulfillment_text= f"The order status for order id: {number} is: {order_status}"
    else:
        fulfillment_text= f"No order found with order id: {number}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
