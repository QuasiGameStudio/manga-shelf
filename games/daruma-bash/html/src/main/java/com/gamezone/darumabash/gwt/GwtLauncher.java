package com.gamezone.darumabash.gwt;

import com.badlogic.gdx.ApplicationListener;
import com.badlogic.gdx.backends.gwt.GwtApplication;
import com.badlogic.gdx.backends.gwt.GwtApplicationConfiguration;
import com.gamezone.darumabash.DarumaGame;
import com.gamezone.darumabash.Platform;

/**
 * Launches the browser build. Installs the web font/screenshot backend first, then creates the
 * same {@link DarumaGame} the desktop launcher does - so gameplay is shared, not duplicated.
 */
public class GwtLauncher extends GwtApplication {

    @Override
    public GwtApplicationConfiguration getConfig() {
        // Fill the browser window, with no letterboxing padding.
        GwtApplicationConfiguration cfg = new GwtApplicationConfiguration(true);
        cfg.padVertical = 0;
        cfg.padHorizontal = 0;
        return cfg;
    }

    @Override
    public ApplicationListener createApplicationListener() {
        Platform.install(new WebPlatform());
        // No seed, no screenshot path, no autostart: the browser build always starts at the menu.
        return new DarumaGame();
    }
}
