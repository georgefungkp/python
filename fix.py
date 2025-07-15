tags = {
    6: "AvgPx (Calculated average price of all fills)",
    14: "CumQty (Total quantity filled)",
    31: "LastPx (Last traded price)",
    32: "LastQty (Last traded quantity)",
    35: {"name": "MsgType (Message Type)",
         "values": {
             "3": "Reject",
             "8": "Execution Report",
             "E": "New Order Single",
             "F": "Order Cancel Request",
             "H": "Order Status Request",
             "I": "New Order List",
             "K": "Order Status Request",
         }
    },
    38: "OrderQty (Quantity ordered)",
    39: {
        "name": "OrdStatus (Order status)",
        "values": {
            "0": "New",
            "1": "Partially Filled",
            "2": "Filled",
            "4": "Canceled",
            "8": "Rejected",
            "A": "Pending New"
        }
    },
    40: {
        "name": "OrdType (Order type)",
        "values": {
            "1": "Market",
            "2": "Limit"
            # Add other order types as needed
        }
    },
    44: "Price (Limit Price per unit)",
    54: {
        "name": "Side",
        "values": {
            "1": "Buy",
            "2": "Sell"
            # Add other sides as needed
        }
    },
    55: "Symbol (Security identifier/ticker)",
    150: {
        "name": "ExecType (Execution type)",
        "values": {
            "0": "New",
            "4": "Canceled",
            "F": "Trade"
            # Add other exec types as needed
        }
    },
    151: "LeavesQty (Quantity remaining to be executed)"
}

import random


def quiz():
    tag_id, tag_data = random.choice(list(tags.items()))

    if isinstance(tag_data, dict):
        # Handle enumerated tags
        answer = input(f"Tag {tag_id} is for what? ")
        if answer.lower() == tag_data['name'].lower().split()[0]:
            print("Correct! Possible values:")
            # for val, desc in tag_data['values'].items():
            #     print(f"  {val}: {desc}")
        else:
            print(f"Nope! It's {tag_data['name']}")

        # Bonus: Quiz on values
        val, val_desc = random.choice(list(tag_data['values'].items()))
        val_answer = input(f"What does value '{val}' mean in tag {tag_id}? ")
        print("Correct!" if val_answer.lower() == val_desc.lower() else f"Nope! It's {val_desc}")

    else:
        # Handle simple tags
        answer = input(f"Tag {tag_id} is for what? ")
        correct_answer = tag_data.split()[0]
        print(f"Correct!" if answer.lower() == correct_answer.lower() else f"Nope! It's {correct_answer}")
        # correct_answer = tag_data
        # print(f"Correct!" if int(answer) == int(correct_answer) else f"Nope! It's {correct_answer}")


# Run the quiz
while True:
    quiz()