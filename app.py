import random
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'super_secret_santa_key'  # Required for flash messages

class Participant:
    def __init__(self, name, avatar_url=None):
        self.name = name
        self.avatar_url = avatar_url or f"https://api.dicebear.com/9.x/thumbs/svg?seed={name}"

def solve_secret_santa(names, constraints):
    """
    names: list of strings
    constraints: list of dicts {'giver': str, 'receiver': str, 'type': 'must'|'must_not'}
    Returns: list of (giver, receiver) tuples or None if no solution
    """
    n = len(names)
    if n < 2:
        return None

    # Separate constraints
    must_give = {} # giver -> receiver
    must_not_give = set() # (giver, receiver)

    for c in constraints:
        g, r = c['giver'], c['receiver']
        if c['type'] == 'must':
            if g in must_give and must_give[g] != r:
                return None # Conflicting must constraints
            must_give[g] = r
        elif c['type'] == 'must_not':
            must_not_give.add((g, r))

    # Backtracking solver to find a Hamiltonian cycle that satisfies constraints
    # We need a permutation of names p[0] -> p[1] -> ... -> p[n-1] -> p[0]
    
    # Optimization: Pre-check if must_give forms a valid partial chain/cycles
    # For a single ring, we can't have sub-cycles unless the sub-cycle is the whole ring.
    
    # Let's try a simpler approach: randomized attempts with validation if N is small
    # Or a proper backtracking search. Given N is likely small (<50), backtracking is fine.
    
    # We need to assign a receiver for each giver such that:
    # 1. Everyone gives to exactly one person
    # 2. Everyone receives from exactly one person
    # 3. No one gives to themselves
    # 4. Constraints are met
    # 5. The graph is connected (one single cycle) - THIS IS KEY for "Secret Santa Ring"
    
    # Let's build the cycle directly.
    # We need to order the names [p1, p2, ..., pn] such that p1->p2, p2->p3... pn->p1
    
    # Filter valid next candidates
    def get_valid_next(current_giver, available_receivers):
        candidates = []
        for r in available_receivers:
            if r == current_giver: continue
            if (current_giver, r) in must_not_give: continue
            if current_giver in must_give and must_give[current_giver] != r: continue
            candidates.append(r)
        return candidates

    # We can fix the first person to break symmetry if no 'must' constraints exist, 
    # but with constraints, we should just try to build a path.
    
    # Actually, simpler: Just find a permutation that satisfies 'must' and 'must_not' 
    # AND forms a single cycle.
    
    import itertools
    
    # If N is very small, permutations are okay. If N is 10-20, we need to be smarter.
    # Let's use a randomized greedy approach with restarts for performance on larger N.
    
    max_attempts = 10000
    for _ in range(max_attempts):
        pool = names[:]
        random.shuffle(pool)
        
        # Check if this permutation forms a valid cycle considering constraints
        # Cycle: pool[0]->pool[1]->...->pool[n-1]->pool[0]
        
        valid = True
        pairs = []
        for i in range(n):
            giver = pool[i]
            receiver = pool[(i + 1) % n]
            
            # Check constraints
            if giver == receiver: # Should not happen if n > 1
                valid = False; break
            if (giver, receiver) in must_not_give:
                valid = False; break
            if giver in must_give and must_give[giver] != receiver:
                valid = False; break
            
            pairs.append((giver, receiver))
            
        if valid:
            # Also need to check if any 'must' constraints were missed? 
            # The loop above checks "if giver in must_give, is receiver correct?"
            # But what if a 'must' constraint implies a link that ISN'T in our cycle?
            # e.g. must_give A->B. If our cycle is A->C->... then valid=False above catches it.
            # So we are good.
            return pairs

    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Parse form data
        # Expecting raw form data or json? Let's assume standard form submission
        # We'll need dynamic fields, so maybe JS on frontend sends JSON?
        # Let's stick to simple form parsing for now, or use JSON if easier.
        pass
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    names = [n.strip() for n in data.get('names', []) if n.strip()]
    constraints = data.get('constraints', [])
    
    if len(names) < 2:
        return {"error": "Need at least 2 participants"}, 400
        
    pairs = solve_secret_santa(names, constraints)
    
    if not pairs:
        return {"error": "No valid solution found with these constraints!"}, 400
        
    # Build response with avatars
    result = []
    for g, r in pairs:
        result.append({
            'giver': {'name': g, 'avatar': f"https://api.dicebear.com/9.x/thumbs/svg?seed={g}"},
            'receiver': {'name': r, 'avatar': f"https://api.dicebear.com/9.x/thumbs/svg?seed={r}"}
        })
        
    return {"pairs": result}

if __name__ == '__main__':
    app.run(debug=True, port=5001)
