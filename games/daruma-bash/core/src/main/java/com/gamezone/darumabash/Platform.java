package com.gamezone.darumabash;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.g2d.BitmapFont;

/**
 * The two places where the shared game cannot behave identically on every backend: building the
 * UI fonts, and grabbing the framebuffer.
 *
 * <p>Desktop rasterises the TTF at startup with FreeType; the browser has no FreeType backend, so
 * it loads pre-baked atlases instead (see {@code tools/bake-web-fonts.py}). Each launcher installs
 * its own implementation before the game is created. Keeping the choice here means the GWT compiler
 * never sees a FreeType or file-system call, and the desktop path stays exactly as it was.
 */
public final class Platform {

    /** Per-backend services the game needs but cannot implement itself. */
    public interface Impl {
        /**
         * @param size    pixel height of the generated face
         * @param border  outline width in pixels
         * @param shadow  shadow offset in pixels
         * @param text    fill colour
         * @param outline outline colour
         */
        BitmapFont createFont(int size, float border, int shadow, Color text, Color outline);

        void captureScreenshot(String path);
    }

    /** Used when a launcher installs nothing: playable, but not the intended presentation. */
    private static final Impl FALLBACK = new Impl() {
        @Override
        public BitmapFont createFont(int size, float border, int shadow, Color text, Color outline) {
            Gdx.app.error("Platform", "no font backend installed - scaling the bundled default font");
            BitmapFont font = new BitmapFont();
            font.getData().setScale(size >= 60 ? 4.0f : size >= 26 ? 1.7f : 1.3f);
            font.setColor(text);
            return font;
        }

        @Override
        public void captureScreenshot(String path) {
            Gdx.app.error("Platform", "screenshots are not supported on this backend");
        }
    };

    private static Impl impl = FALLBACK;

    private Platform() {
    }

    /** Called once by the launcher, before {@code Lwjgl3Application}/{@code GwtApplication}. */
    public static void install(Impl platform) {
        impl = platform != null ? platform : FALLBACK;
    }

    public static BitmapFont createFont(int size, float border, int shadow, Color text,
                                        Color outline) {
        return impl.createFont(size, border, shadow, text, outline);
    }

    public static void captureScreenshot(String path) {
        impl.captureScreenshot(path);
    }
}
