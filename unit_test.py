import unittest
from calc import (
    build_deck, remove_cards, hand_value, is_soft,
    dealer_outcomes, compare, bust_probability, calculate
)

class TestBuildDeck(unittest.TestCase):
    def test_correct_counts(self):
        deck = build_deck()
        for rank, count in deck.items():
            self.assertEqual(count, 4)

    def test_correct_ranks(self):
        deck = build_deck()
        expected = {"A","2","3","4","5","6","7","8","9","10","J","Q","K"}
        self.assertEqual(set(deck.keys()), expected)

    def test_total_cards(self):
        deck = build_deck()
        self.assertEqual(sum(deck.values()), 52)


class TestRemoveCards(unittest.TestCase):
    def test_removes_single_card(self):
        deck = build_deck()
        remove_cards(deck, ["A"])
        self.assertEqual(deck["A"], 3)

    def test_removes_multiple_cards(self):
        deck = build_deck()
        remove_cards(deck, ["A", "K", "2"])
        self.assertEqual(deck["A"], 3)
        self.assertEqual(deck["K"], 3)
        self.assertEqual(deck["2"], 3)

    def test_removes_duplicates(self):
        deck = build_deck()
        remove_cards(deck, ["A", "A"])
        self.assertEqual(deck["A"], 2)

    def test_total_decrements(self):
        deck = build_deck()
        remove_cards(deck, ["A", "K", "6"])
        self.assertEqual(sum(deck.values()), 49)


class TestHandValue(unittest.TestCase):
    def test_simple_hand(self):
        self.assertEqual(hand_value(["5", "7"]), 12)

    def test_face_cards(self):
        self.assertEqual(hand_value(["J", "Q"]), 20)

    def test_blackjack(self):
        self.assertEqual(hand_value(["A", "K"]), 21)

    def test_soft_hand(self):
        self.assertEqual(hand_value(["A", "7"]), 18)

    def test_ace_flips_to_one(self):
        # A + 7 + 8 = 16, ace flips to 1
        self.assertEqual(hand_value(["A", "7", "8"]), 16)

    def test_multiple_aces(self):
        # A + A = 12 (one counts as 11, one as 1)
        self.assertEqual(hand_value(["A", "A"]), 12)

    def test_bust(self):
        self.assertEqual(hand_value(["K", "Q", "5"]), 25)

    def test_ten_value(self):
        self.assertEqual(hand_value(["10", "9"]), 19)


class TestIsSoft(unittest.TestCase):
    def test_soft_hand(self):
        self.assertTrue(is_soft(["A", "7"]))

    def test_hard_hand(self):
        self.assertFalse(is_soft(["8", "Q"]))

    def test_ace_flipped_is_hard(self):
        # A + 7 + 8: ace had to flip to 1
        self.assertFalse(is_soft(["A", "7", "8"]))

    def test_double_ace_soft(self):
        # A + A = 12, one ace still counts as 11
        self.assertTrue(is_soft(["A", "A"]))

    def test_no_ace(self):
        self.assertFalse(is_soft(["5", "6"]))


class TestDealerOutcomes(unittest.TestCase):
    def test_probabilities_sum_to_one(self):
        deck = build_deck()
        remove_cards(deck, ["6", "8", "Q"])
        dist = dealer_outcomes(["6"], deck)
        total = sum(dist.values())
        self.assertAlmostEqual(total, 1.0, places=6)

    def test_dealer_stands_at_17(self):
        deck = build_deck()
        dist = dealer_outcomes(["10", "7"], deck)
        self.assertEqual(dist, {17: 1.0})

    def test_dealer_busts(self):
        deck = build_deck()
        dist = dealer_outcomes(["10", "8", "7"], deck)
        self.assertEqual(dist, {"bust": 1.0})

    def test_contains_only_valid_outcomes(self):
        deck = build_deck()
        dist = dealer_outcomes(["6"], deck)
        for outcome in dist:
            self.assertTrue(outcome == "bust" or 17 <= outcome <= 21)


class TestCompare(unittest.TestCase):
    def test_player_wins(self):
        dist = {18: 1.0}
        w, l, t = compare(20, dist)
        self.assertAlmostEqual(w, 1.0)
        self.assertAlmostEqual(l, 0.0)
        self.assertAlmostEqual(t, 0.0)

    def test_player_loses(self):
        dist = {20: 1.0}
        w, l, t = compare(18, dist)
        self.assertAlmostEqual(w, 0.0)
        self.assertAlmostEqual(l, 1.0)
        self.assertAlmostEqual(t, 0.0)

    def test_tie(self):
        dist = {18: 1.0}
        w, l, t = compare(18, dist)
        self.assertAlmostEqual(w, 0.0)
        self.assertAlmostEqual(l, 0.0)
        self.assertAlmostEqual(t, 1.0)

    def test_dealer_bust_is_win(self):
        dist = {"bust": 1.0}
        w, l, t = compare(15, dist)
        self.assertAlmostEqual(w, 1.0)

    def test_mixed_outcomes(self):
        dist = {"bust": 0.3, 17: 0.3, 20: 0.4}
        w, l, t = compare(18, dist)
        self.assertAlmostEqual(w, 0.6)  # bust + 17
        self.assertAlmostEqual(l, 0.4)  # 20
        self.assertAlmostEqual(t, 0.0)


class TestBustProbability(unittest.TestCase):
    def test_no_bust_possible(self):
        # hand value 2, any card keeps under 21
        deck = build_deck()
        remove_cards(deck, ["A", "A"])
        prob = bust_probability(["A", "A"], deck)
        self.assertAlmostEqual(prob, 0.0)

    def test_high_bust_chance(self):
        # hand value 20, almost everything busts
        deck = build_deck()
        remove_cards(deck, ["K", "Q"])
        prob = bust_probability(["K", "Q"], deck)
        self.assertGreater(prob, 0.9)

    def test_between_zero_and_one(self):
        deck = build_deck()
        remove_cards(deck, ["8", "7"])
        prob = bust_probability(["8", "7"], deck)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)


class TestCalculate(unittest.TestCase):
    def test_blackjack_stands(self):
        result = calculate(["A", "K"], "6")
        self.assertEqual(result["action"], "stand")
        self.assertEqual(result["hand_value"], 21)

    def test_blackjack_is_soft(self):
        result = calculate(["A", "K"], "6")
        self.assertTrue(result["is_soft"])

    def test_hard_20_stands(self):
        result = calculate(["K", "Q"], "6")
        self.assertEqual(result["action"], "stand")

    def test_hard_20_not_soft(self):
        result = calculate(["K", "Q"], "6")
        self.assertFalse(result["is_soft"])

    def test_low_hand_hits(self):
        result = calculate(["2", "3"], "K")
        self.assertEqual(result["action"], "hit")

    def test_probabilities_sum_to_one(self):
        result = calculate(["8", "Q"], "K")
        total = result["win"] + result["lose"] + result["tie"]
        self.assertAlmostEqual(total, 1.0, places=3)

    def test_response_keys_present(self):
        result = calculate(["A", "7"], "6")
        for key in ["action", "hand_value", "is_soft", "win", "lose", "tie", "bust"]:
            self.assertIn(key, result)

    def test_soft_18_is_soft(self):
        result = calculate(["A", "7"], "6")
        self.assertTrue(result["is_soft"])
        self.assertEqual(result["hand_value"], 18)

    def test_action_is_valid(self):
        result = calculate(["8", "7"], "10")
        self.assertIn(result["action"], ["hit", "stand", "double"])

    def test_double_only_on_first_two(self):
        # 3 cards — double should not be possible
        result = calculate(["2", "3", "4"], "6")
        self.assertNotEqual(result["action"], "double")


if __name__ == "__main__":
    unittest.main(verbosity=2)