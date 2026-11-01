package com.gamezone.darumabash;

import java.util.Random;

/**
 * Daruma Bash rules, plain Java with no libGDX imports: the same class runs on the GWT browser
 * build and inside a headless assert run on the desktop, so the scoring and stage rules have one
 * home and the screen only paints them.
 *
 * <p>Rules (faithful to kumpulangames' Daruma Bash, minus the Lyto platform layer)
 * <ul>
 *   <li>A tower of daruma blocks stands on a pedestal. The bottom block is the target; a glowing
 *       arrow shows the direction the swipe must travel, and it alternates on every clean hit.</li>
 *   <li>A clean hit knocks the target out, the stack above drops one block, score goes up and the
 *       next swift hit is worth more: the combo counts consecutive hits made within
 *       {@link #HIT_WINDOW} seconds of the previous one.</li>
 *   <li>A clean hit inside the window also adds one bonus second to the clock ("Bonus 1 Second").</li>
 *   <li>A slow-but-correct swipe still knocks the block out, but the combo resets. A swipe against
 *       the arrow knocks nothing out and resets the combo too; a too-short swipe is ignored
 *       outright, since it is usually an accidental click.</li>
 *   <li>Clearing {@link #BLOCKS_PER_STAGE} blocks advances the stage: the clock refills (a little
 *       less each stage, down to {@link #MIN_STAGE_TIME}) with a stage-clear bonus. The tower
 *       respawns tall whenever it reaches its last block.</li>
 *   <li>The clock emptying ends the run; the best score survives via the caller's preferences.</li>
 * </ul>
 */
public final class DarumaSim {

    /** What one swipe produced. */
    public enum Outcome { CLEAN, SLOW, WRONG_DIR, SWIPE_TOO_SHORT }

    /** Blocks stacked when a fresh tower spawns. */
    public static final int TOWER_MAX = 6;
    /** Clean hits needed to advance a stage. */
    public static final int BLOCKS_PER_STAGE = 5;
    /** Clock at the start of stage 1, in seconds. */
    public static final float START_TIME = 25f;
    /** Floor under the per-stage refill, so late stages stay playable. */
    public static final float MIN_STAGE_TIME = 14f;
    /** Seconds shaved off the refill per stage number. */
    public static final float STAGE_TIME_STEP = 1.5f;
    /** Hitting within this many seconds of the last hit keeps the combo and adds bonus time. */
    public static final float HIT_WINDOW = 1.0f;
    /** Bonus seconds granted by a clean fast hit. */
    public static final float BONUS_TIME = 1f;
    /** Stage-clear bonus score. */
    public static final int STAGE_CLEAR_BONUS = 500;
    /** Points for one clean hit, before the combo multiplier. */
    public static final int HIT_SCORE = 100;
    /** Extra points per step of the current combo. */
    public static final int COMBO_SCORE = 25;

    /** Pins the run for reproducible tests; 0 means a random one. */
    private final long seed;
    private final Random rng = new Random();

    private int score;
    private int stage = 1;
    private int combo;
    private int best;
    private int newBest;
    private float timer = START_TIME;
    private boolean over;
    private int towerLeft = TOWER_MAX;
    private int stageBlocks;
    /** Direction the next swipe must travel: +1 = left to right, -1 = right to left. */
    private int nextDirection = 1;
    /** Seconds since the last clean/slow hit; drives the combo window. */
    private float sinceLastHit = 99f;

    public DarumaSim() {
        this(0L);
    }

    public DarumaSim(long seed) {
        this.seed = seed;
        rng.setSeed(seed != 0L ? seed : System.nanoTime());
        nextDirection = rng.nextBoolean() ? 1 : -1;
        best = 0;
	}

    // ------------------------------------------------------------------ queries (the screen paints these)

    public int score() { return score; }

    public int stage() { return stage; }

    public int combo() { return combo; }

    public int best() { return best; }

    /** 1 when this run set a new best, so the over panel can shout about it once. */
    public int newBest() { return newBest; }

    public float timer() { return timer; }

    public boolean over() { return over; }

    public int towerLeft() { return towerLeft; }

    public int stageBlocks() { return stageBlocks; }

    public int nextDirection() { return nextDirection; }

    /** Seconds since the last real hit; the combo window is judged on this. */
    public float sinceLastHit() { return sinceLastHit; }

    // ------------------------------------------------------------------ rules

    /**
     * Resolves one horizontal swipe travelling {@code direction} (sign only) made
     * {@code reaction} seconds after the previous hit. Never called once {@link #over()}.
     */
    public Outcome swipe(int direction, float reaction) {
        if (over || direction == 0) {
            return Outcome.SWIPE_TOO_SHORT;
        }
        if (direction != nextDirection) {
            combo = 0;
            return Outcome.WRONG_DIR;
        }
        if (reaction > HIT_WINDOW) {
            combo = 0;
            knockOut();
            return Outcome.SLOW;
        }
        combo++;
        score += HIT_SCORE * stage + COMBO_SCORE * combo;
        timer += BONUS_TIME;
        knockOut();
        return Outcome.CLEAN;
    }

    /** Advances the clock; the run ends the moment it runs out. */
    public void tick(float delta) {
        if (over) {
            return;
        }
        sinceLastHit += delta;
        timer -= delta;
        if (timer <= 0f) {
            timer = 0f;
            over = true;
            if (score > best) {
                best = score;
                newBest = 1;
            }
        }
    }

    /** One block has left the tower: score, stage progress, direction flip, tower refill. */
    private void knockOut() {
        sinceLastHit = 0f;
        towerLeft--;
        stageBlocks++;
        nextDirection = -nextDirection;

        if (stageBlocks >= BLOCKS_PER_STAGE) {
            score += STAGE_CLEAR_BONUS;
            stage++;
            stageBlocks = 0;
            timer = Math.max(MIN_STAGE_TIME, START_TIME - (stage - 1) * STAGE_TIME_STEP);
            if (score > best) {
                // Live best update: the over panel also handles it, but a stage-clear record
                // should survive even if the player alt-tabs away immediately after.
                best = score;
                newBest = 1;
            }
        }
        if (towerLeft <= 1) {
            towerLeft = TOWER_MAX;
        }
    }

    // ------------------------------------------------------------------ self-check

    private static void check(boolean condition, String what) {
        if (!condition) {
            throw new AssertionError("DarumaSim self-test failed: " + what);
        }
    }

    /**
     * Drives one scripted run through every rule and throws on the first broken one.
     * Run with:{@code java -cp core/build/classes/java/main com.gamezone.darumabash.DarumaSim}
     */
    public static void main(String[] args) {
        DarumaSim sim = new DarumaSim(7L);
        int startDir = sim.nextDirection();
        check(sim.timer() == START_TIME && !sim.over() && sim.towerLeft() == TOWER_MAX,
                "fresh run state");
        check(sim.score() == 0 && sim.stage() == 1, "fresh counters");

        // Fast correct hits: +1 bonus second each, combo grows.
        sim.tick(0.1f);
        Outcome first = sim.swipe(startDir, 0.4f);
        check(first == Outcome.CLEAN, "correct fast swipe = CLEAN");
        check(sim.combo() == 1, "combo after first hit");
        check(sim.timer() == START_TIME - 0.1f + BONUS_TIME, "bonus second added");
        int dirAfterFirst = sim.nextDirection();
        check(dirAfterFirst == -startDir, "direction flips after a hit");
        check(sim.towerLeft() == TOWER_MAX - 1, "tower shrank");

        // A too-short swipe does nothing; a wrong direction resets the combo.
        check(sim.swipe(0, 0.2f) == Outcome.SWIPE_TOO_SHORT, "zero-length swipe ignored");
        Outcome wrong = sim.swipe(-dirAfterFirst, 0.2f);
        check(wrong == Outcome.WRONG_DIR, "swipe against the arrow = WRONG_DIR");
        check(sim.combo() == 0 && sim.nextDirection() == dirAfterFirst,
                "wrong swipe resets combo but not the cue");

        // A slow correct hit scores no combo and no bonus, but still moves the run.
        sim.tick(HIT_WINDOW + 0.05f);
        float before = sim.timer();
        check(sim.swipe(dirAfterFirst, HIT_WINDOW + 0.05f) == Outcome.SLOW,
                "late-correct swipe = SLOW");
        check(sim.timer() == before, "SLOW grants no bonus time");
        check(sim.combo() == 0, "SLOW resets combo");

        // Full tower drain respawns a fresh tower.
        sim.tick(0.1f);
        int guard = 0;
        while (sim.towerLeft() != TOWER_MAX && guard++ < 20) {
            sim.swipe(sim.nextDirection(), 0.3f);
            sim.tick(0.05f);
        }
        check(sim.towerLeft() == TOWER_MAX, "tower respawns when drained");

        // Stage clear: BLOCKS_PER_STAGE hits advance the stage and refill the clock. Every hit
        // in this loop is fast and consecutive, so the combo climbs 1..5 while still stage 1.
        DarumaSim fresh = new DarumaSim(11L);
        fresh.tick(0.2f);
        int expected = 0;
        for (int i = 0; i < BLOCKS_PER_STAGE; i++) {
            check(fresh.swipe(fresh.nextDirection(), 0.4f) == Outcome.CLEAN, "hit " + i + " clean");
            expected += HIT_SCORE + COMBO_SCORE * (i + 1);
            fresh.tick(0.2f);
        }
        expected += STAGE_CLEAR_BONUS;
        check(fresh.stage() == 2, "stage advanced after " + BLOCKS_PER_STAGE + " hits");
        check(fresh.score() == expected, "stage-clear score arithmetic");
        check(fresh.timer() == Math.max(MIN_STAGE_TIME, START_TIME - STAGE_TIME_STEP) - 0.2f,
                "timer refilled on stage clear"); // minus the loop's trailing tick(0.2)

        // The clock emptying ends the run and stamps the best.
        DarumaSim over = new DarumaSim(13L);
        over.tick(0.1f);
        over.swipe(over.nextDirection(), 0.3f);
        over.tick(200f);
        check(over.over() && over.timer() == 0f, "clock out ends the run");
        check(over.best() == over.score() && over.newBest() == 1, "best stamped on game over");

        System.out.println("DarumaSim self-test: all checks passed");
    }
}
