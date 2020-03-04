import json
import os
import random

import bottle


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()


@bottle.route("/")
def index():
    return "Your Battlesnake is alive!"


@bottle.post("/ping")
def ping():
    """
    Used by the Battlesnake Engine to make sure your snake is still working.
    """
    return bottle.HTTPResponse(status=200)


@bottle.post("/start")
def start():
    """
    Called every time a new Battlesnake game starts and your snake is in it.
    Your response will control how your snake is displayed on the board.
    """
    data = bottle.request.json
    print("START:", json.dumps(data))

    response = {"color": "#00FF00", "headType": "regular", "tailType": "regular"}
    return bottle.HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/move")
def move():
    """
    Called when the Battlesnake Engine needs to know your next move.
    The data parameter will contain information about the board.
    Your response must include your move of up, down, left, or right.
    """
    # Organize game data
    data = bottle.request.json

    # Get board dimensions
    width = data['board']['width']
    height = data['board']['height']

    # Foods is list of food positions, head is position of head
    foods = data['board']['food']
    head = data['you']['body'][0]

    d_min = width + height
    target = head
    for food in foods:
        d = abs(food['x'] - head['x']) + abs(food['y'] - head['y'])

        if d < d_min:
            d_min = d
            target = food


    positions = {
        (head['x'] - 1, head['y']): 'left',
        (head['x'], head['y'] + 1): 'up',
        (head['x'] + 1, head['y']): 'right',
        (head['x'], head['y'] - 1): 'down',
    }

    neighbours = {
        (head['x'] - 2, head['y']): 'left',
        (head['x'] - 1, head['y'] + 1): 'left',
        (head['x'] - 1, head['y'] - 1): 'left',
        (head['x'], head['y'] + 2): 'up',
        (head['x'] - 1, head['y'] + 1): 'up',
        (head['x'] + 1, head['y'] + 1): 'up',
        (head['x'] + 2, head['y']): 'right',
        (head['x'] + 1, head['y'] + 1): 'right',
        (head['x'] + 1, head['y'] - 1): 'right',
        (head['x'], head['y'] - 2): 'down',
        (head['x'] - 1, head['y'] - 1): 'down',
        (head['x'] + 1, head['y'] - 1): 'down',
    }

    moves = {
        'left': (target['x'] - head['x'] < 0) * 1,
        'up': (target['y'] - head['y'] > 0) * 1,
        'right': (target['x'] - head['x'] > 0) * 1,
        'down': (target['x'] - head['x'] < 0) * 1,
    }


    # Check boundary conditions
    for position, move in positions.items():
        if position['x'] < 0 or position['y'] < 0:
            moves[move] -= 10

    # Check for occupied and risky spaces
    for snake in data['board']['snakes']:
        for indx, body in enumerate(snake['body']):
            key = (body['x'], body['y'])

            pmove = positions.get(key)
            if pmove is not None:
                moves[pmove] -= 10

            nmove = neighbours.get(key)
            if nmove is not None:
                moves[nmove] -= 1

    move = sorted(moves.keys(), key=lambda x: moves[x])[0]

    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
    shout = "I am a python snake!"

    response = {"move": move, "shout": shout}
    return bottle.HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/end")
def end():
    """
    Called every time a game with your snake in it ends.
    """
    data = bottle.request.json
    print("END:", json.dumps(data))
    return bottle.HTTPResponse(status=200)



def main():
    bottle.run(
        application,
        host=os.getenv("IP", "0.0.0.0"),
        port=os.getenv("PORT", "8080"),
        debug=os.getenv("DEBUG", True),
    )


if __name__ == "__main__":
    main()
