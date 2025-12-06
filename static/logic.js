// static/logic.js

function solveSecretSanta(names, constraints) {
    const n = names.length;
    if (n < 2) return null;

    // Separate constraints
    const mustGive = {}; // giver -> receiver
    const mustNotGive = new Set(); // "giver|receiver" strings

    for (const c of constraints) {
        const g = c.giver;
        const r = c.receiver;
        if (c.type === 'must') {
            if (mustGive[g] && mustGive[g] !== r) {
                return null; // Conflicting must constraints
            }
            mustGive[g] = r;
        } else if (c.type === 'must_not') {
            mustNotGive.add(`${g}|${r}`);
        }
    }

    // Randomized greedy approach with restarts
    const maxAttempts = 10000;
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        // Shuffle names
        const pool = [...names];
        for (let i = pool.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [pool[i], pool[j]] = [pool[j], pool[i]];
        }

        // Check if this permutation forms a valid cycle
        // Cycle: pool[0]->pool[1]->...->pool[n-1]->pool[0]
        let valid = true;
        const pairs = [];
        
        for (let i = 0; i < n; i++) {
            const giver = pool[i];
            const receiver = pool[(i + 1) % n];

            // Check constraints
            if (giver === receiver) {
                valid = false; break;
            }
            if (mustNotGive.has(`${giver}|${receiver}`)) {
                valid = false; break;
            }
            if (mustGive[giver] && mustGive[giver] !== receiver) {
                valid = false; break;
            }
            
            pairs.push({
                giver: { name: giver, avatar: `https://api.dicebear.com/9.x/thumbs/svg?seed=${giver}` },
                receiver: { name: receiver, avatar: `https://api.dicebear.com/9.x/thumbs/svg?seed=${receiver}` }
            });
        }
        
        if (valid) {
            // Additional check: Did we satisfy ALL 'must' constraints?
            // The loop checks "If I am giving to X, is that allowed?"
            // But if I MUST give to Y, and I am giving to X (where X!=Y), the loop catches it:
            // if (mustGive[giver] && mustGive[giver] !== receiver) -> valid=false
            // So we are good.
            return pairs;
        }
    }

    return null;
}
