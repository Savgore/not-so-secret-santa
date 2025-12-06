import unittest
from app import solve_secret_santa

class TestSecretSanta(unittest.TestCase):
    def test_basic_ring(self):
        names = ['Alice', 'Bob', 'Charlie']
        constraints = []
        pairs = solve_secret_santa(names, constraints)
        self.assertIsNotNone(pairs)
        self.assertEqual(len(pairs), 3)
        
        # Verify it's a valid ring
        givers = set(p[0] for p in pairs)
        receivers = set(p[1] for p in pairs)
        self.assertEqual(givers, set(names))
        self.assertEqual(receivers, set(names))
        
        # Verify no self-giving
        for g, r in pairs:
            self.assertNotEqual(g, r)

    def test_must_give(self):
        names = ['Alice', 'Bob', 'Charlie', 'Dave']
        constraints = [{'giver': 'Alice', 'receiver': 'Bob', 'type': 'must'}]
        pairs = solve_secret_santa(names, constraints)
        self.assertIsNotNone(pairs)
        
        # Check if Alice gives to Bob
        alice_pair = next(p for p in pairs if p[0] == 'Alice')
        self.assertEqual(alice_pair[1], 'Bob')

    def test_must_not_give(self):
        names = ['Alice', 'Bob', 'Charlie']
        constraints = [{'giver': 'Alice', 'receiver': 'Bob', 'type': 'must_not'}]
        pairs = solve_secret_santa(names, constraints)
        self.assertIsNotNone(pairs)
        
        # Check if Alice does NOT give to Bob
        alice_pair = next(p for p in pairs if p[0] == 'Alice')
        self.assertNotEqual(alice_pair[1], 'Bob')

    def test_impossible(self):
        names = ['Alice', 'Bob']
        # Alice must give to Bob, Bob must give to Alice (valid swap, but is it a ring? Yes, A->B, B->A is a ring of 2)
        # Let's try impossible: Alice must not give to Bob, Alice must not give to Alice (implicit).
        # In a 2-person game, Alice MUST give to Bob. So if we forbid it, it should fail.
        constraints = [{'giver': 'Alice', 'receiver': 'Bob', 'type': 'must_not'}]
        pairs = solve_secret_santa(names, constraints)
        self.assertIsNone(pairs)

if __name__ == '__main__':
    unittest.main()
