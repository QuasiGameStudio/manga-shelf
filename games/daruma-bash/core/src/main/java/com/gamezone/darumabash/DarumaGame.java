package com.gamezone.darumabash;

import com.badlogic.gdx.Game;

/** Entry point for the shared (platform-independent) game. */
public class DarumaGame extends Game {

    /** Seed for the first run, or 0 for a random one. Set by the launcher's {@code --seed=N}. */
    private final long initialSeed;
    /** Write one screenshot here then quit, or null to just play. Set by {@code --shot=<path>}. */
    private final String shotPath;
    /** How many frames to draw before that screenshot. Set by {@code --shot-frames=N}. */
    private final int shotFrames;
    /** Skip the menu and start a run at once. Set by {@code --autostart}. */
    private final boolean autoStart;

    public DarumaGame() {
        this(0L);
    }

    public DarumaGame(long initialSeed) {
        this(initialSeed, null, 30, false);
    }

    public DarumaGame(long initialSeed, String shotPath, int shotFrames, boolean autoStart) {
        this.initialSeed = initialSeed;
        this.shotPath = shotPath;
        this.shotFrames = shotFrames;
        this.autoStart = autoStart;
    }

    @Override
    public void create() {
        setScreen(new DarumaScreen(initialSeed, shotPath, shotFrames, autoStart));
    }
}
