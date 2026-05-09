# builds a fresh deck
def build_deck():
    return {"A": 4, "2": 4, "3": 4, "4": 4, "5": 4, "6": 4, "7": 4, "8": 4, "9": 4, "10": 4, "J": 4, "Q": 4, "K": 4}


# remove a card from the deck
def remove_cards(deck, cards):
    for card in cards:
        deck[card] -= 1


# our hand value plus if our hand is soft
def hand_value(cards):
    total = 0
    aces = 0
    for card in cards:
        if card in ("J", "Q", "K"):
            total += 10
        elif card == "A":
            total += 11
            aces += 1
        else:
            total += int(card)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


# if we have a soft hand
def is_soft(cards):
    total = 0
    aces = 0
    for card in cards:
        if card in ("J", "Q", "K"):
            total += 10
        elif card == "A":
            total += 11
            aces += 1
        else:
            total += int(card)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return aces > 0


def dealer_outcomes(dealer_cards, deck):
    """
    assume that the dealer will stand on 17+
    we enumerate all possibilities from the remaining cards
    return a list of probabilities of each combination outcome
    """
    total = hand_value(dealer_cards)

    if total > 21:
        return {"bust": 1.0}
    if total >= 17:
        return {total: 1.0}

    results = {}
    remaining = sum(deck.values())

    # calculate each probability for each rank
    for rank, count in deck.items():
        if count == 0:
            continue
        prob = count / remaining

        # remove,recurse, restore
        deck[rank] -= 1
        outcomes = dealer_outcomes(dealer_cards + [rank], deck)
        deck[rank] += 1

        for total, p in outcomes.items():
            results[total] = results.get(total, 0) + prob * p

    return results


def compare(player_total, dealer_dist):
    """
    compare player versus dealer
    we add the probabilities
    """
    win = lose = tie = 0.0
    for dealer_total, prob in dealer_dist.items():
        if dealer_total == "bust" or dealer_total < player_total:
            win += prob
        elif dealer_total == player_total:
            tie += prob
        else:
            lose += prob
    return win, lose, tie


def bust_probability(player_cards, deck):
    # prob that player will bust next hit
    remaining = sum(deck.values())
    bust_count = 0
    for rank, count in deck.items():
        # unlikely but possible
        if count == 0:
            continue
        if hand_value(player_cards + [rank]) > 21:
            bust_count += count
    return bust_count / remaining


def ev_stand(player_cards, dealer_upcard, deck):
    """
    the probability distribution if the player stands now
    """
    total = hand_value(player_cards)
    dist = dealer_outcomes([dealer_upcard], deck)
    return compare(total, dist)


def ev_double(player_cards, dealer_upcard, deck):
    """
    the probability distribution if the player doubles ie. hit then stand
    """
    remaining = sum(deck.values())
    win = lose = tie = 0.0
    for rank, count in deck.items():
        if count == 0:
            continue
        prob = count / remaining
        new_total = hand_value(player_cards + [rank])
        if new_total > 21:
            lose += prob
        else:
            deck[rank] -= 1
            dist = dealer_outcomes([dealer_upcard], deck)
            deck[rank] += 1
            w, l, p = compare(new_total, dist)
            win += prob * w
            lose += prob * l
            tie += prob * p
    return win, lose, tie
 

def ev_hit(player_cards, dealer_upcard, deck, cache=None):
    """
    the probability distribution for hitting once
    """
    if cache is None:
        cache = {}
    remaining = sum(deck.values())
    win = lose = tie = 0.0
    for rank, count in deck.items():
        if count == 0:
            continue
        prob = count / remaining
        new_cards = player_cards + [rank]
        new_total = hand_value(new_cards)
        if new_total > 21:
            lose += prob
        else:
            deck[rank] -= 1
            w, l, p = best_ev(new_cards, dealer_upcard, deck, cache)
            deck[rank] += 1
            win += prob * w
            lose += prob * l
            tie += prob * p
    return win, lose, tie


def best_ev(player_cards, dealer_upcard, deck, cache=None):
    """
    the best possible move for the player right now
    """
    if cache is None:
        cache = {}
    total = hand_value(player_cards)
    print(f"best_ev called: total={total}, cards={player_cards}")
    if total > 21:
        return 0.0, 1.0, 0.0

    key = (total, is_soft(player_cards), dealer_upcard, tuple(sorted(deck.items())))
    if key in cache:
        return cache[key]

    stand_w, stand_l, stand_p = ev_stand(player_cards, dealer_upcard, deck)
    hit_w, hit_l, hit_p = ev_hit(player_cards, dealer_upcard, deck, cache)

    if (stand_w - stand_l) >= (hit_w - hit_l):
        result = stand_w, stand_l, stand_p
    else:
        result = hit_w, hit_l, hit_p

    cache[key] = result
    return result


def calculate(player_cards: list[str], dealer_upcard: str) -> dict:
    # start with a new deck
    deck = build_deck()
    # remove the cards we have seen
    remove_cards(deck, player_cards + [dealer_upcard])

    # used for double
    is_first_two = len(player_cards) == 2
    player_total = hand_value(player_cards)

    cache = {}

    stand_w, stand_l, stand_p = ev_stand(player_cards, dealer_upcard, deck)
    hit_w, hit_l, hit_p = ev_hit(player_cards, dealer_upcard, deck, cache)
    bust_pct = bust_probability(player_cards, deck)

    actions = {
        "stand": (stand_w, stand_l, stand_p),
        "hit":   (hit_w, hit_l, hit_p),
    }

    if is_first_two:
        double_w, double_l, double_p = ev_double(player_cards, dealer_upcard, deck)
        actions["double"] = (double_w, double_l, double_p)
 
    best_action = max(actions, key=lambda a: actions[a][0] - actions[a][1])
    best_w, best_l, best_p = actions[best_action]

    # our json response format
    return {
        "action":     best_action,
        "hand_value": player_total,
        "win":    round(best_w, 4),
        "lose":   round(best_l, 4),
        "tie":   round(best_p, 4),
        "bust":   round(bust_pct, 4),
        "is_soft": is_soft(player_cards)
    }
    