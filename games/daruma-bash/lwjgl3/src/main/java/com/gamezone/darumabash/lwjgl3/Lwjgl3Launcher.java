package com.gamezone.darumabash.lwjgl3;

import com.badlogic.gdx.backends.lwjgl3.Lwjgl3Application;
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3ApplicationConfiguration;
import com.gamezone.darumabash.DarumaGame;
import com.gamezone.darumabash.Platform;

/**
 * Desktop launcher. Run with {@code gradlew lwjgl3:run} or
 * {@code gradlew lwjgl3:run --args="--seed=42"}.
 *
 * <p>Verification flags, all optional:
 * <ul>
 *   <li>{@code --seed=N} pins the run, which makes a session reproducible.</li>
 *   <li>{@code --autostart} skips the menu and starts a run immediately.</li>
 *   <li>{@code --shot=<path>} writes one screenshot to {@code path} and quits - the only way to
 *       see what the game actually drew on Windows, where grabbing a GL window from outside comes
 *       back blank.</li>
 *   <li>{@code --shot-frames=N} how many frames to draw before that screenshot (default 30).</li>
 * </ul>
 */
public class Lwjgl3Launcher {

    public static void main(String[] args) {
        // Desktop builds its fonts from the TTF at startup and can write screenshots; the shared
        // game only knows the Platform seam, which keeps core compilable for GWT.
        Platform.install(new DesktopPlatform());
        new Lwjgl3Application(new DarumaGame(seedFrom(args), value(args, "--shot="),
                intValue(args, "--shot-frames=", 30), has(args, "--autostart")),
                configuration());
    }

    /** {@code --seed=N} pins the run, which makes a session reproducible. */
    private static long seedFrom(String[] args) {
        for (String arg : args) {
            if (arg.startsWith("--seed=")) {
                try {
                    return Long.parseLong(arg.substring("--seed=".length()).trim());
                } catch (NumberFormatException ignored) {
                    // fall through to a random run
                }
            }
        }
        return 0L;
    }

    private static boolean has(String[] args, String flag) {
        for (String arg : args) {
            if (arg.equals(flag)) {
                return true;
            }
        }
        return false;
    }

    private static String value(String[] args, String prefix) {
        for (String arg : args) {
            if (arg.startsWith(prefix)) {
                return arg.substring(prefix.length()).trim();
            }
        }
        return null;
    }

    private static int intValue(String[] args, String prefix, int fallback) {
        String raw = value(args, prefix);
        if (raw != null) {
            try {
                return Integer.parseInt(raw);
            } catch (NumberFormatException ignored) {
                // fall through to the default
            }
        }
        return fallback;
    }

    private static Lwjgl3ApplicationConfiguration configuration() {
        Lwjgl3ApplicationConfiguration config = new Lwjgl3ApplicationConfiguration();
        config.setTitle("Daruma Bash");
        config.setWindowedMode(1280, 720);
        config.useVsync(true);
        config.setForegroundFPS(60);
        config.setResizable(true);
        return config;
    }
}
